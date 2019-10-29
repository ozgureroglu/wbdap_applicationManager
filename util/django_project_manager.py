import subprocess
import threading
import urllib

from applicationManager.models import DjangoProject
from applicationManager.signals.signals import application_creation_failed_signal

__author__ = 'ozgur'

import mako
import os
import sys
import logging
import time
import queue
from mako import runtime
from mako.template import Template
from django.template import loader
from io import StringIO
from django.conf import settings
from django.core.management import call_command
from django.core.management.commands import startproject

logger = logging.getLogger("wbdap.debug")

IMPORT_MODEL_TEMPLATE = """from %(app)s.models import %(model)s
"""

IMPORT_SUB_MODEL_TEMPLATE = """from %(app)s.%(sub_models_dir)s.generated_models import *
"""

IMPORT_DJANGO_DB = """from django.db import models
"""

CHARFIELD_TEMPLATE = """
    %(name)s = models.CharField(max_length=%(length)s, null=%(null)s, blank=%(blank)s)
"""

TEXTFIELD_TEMPLATE = """
    %(name)s = models.TextField(null=%(null)s, blank=%(null)s)
"""

INTEGERFIELD_TEMPLATE = """
    %(name)s = models.IntegerField(null=%(null)s, default=%(default)s)
"""

DECIMALFIELD_TEMPLATE = """
    %(name)s = models.DecimalField(max_digits=%(digits)s, decimal_places=%(places)s, null=%(null)s, default=%(default)s)
"""

DATETIMEFIELD_TEMPLATE = """
    %(name)s = models.DateTimeField(null=%(null)s, default=%(default)s)
"""

FOREIGNFIELD_TEMPLATE = """
    %(name)s = models.ForeignKey(%(foreign)s, null=%(null)s, blank=%(null)s)
"""


MODEL_TEMPLATE = """
#begin_%(model)s
class %(model)s(models.Model):
    %(fields)s
    update_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
#end_%(model)s"""


class DjangoProjectManager:
    def __init__(self, project: DjangoProject):
        # Project object is coming from the database records which holds the metadata of the project

        self.project = project
        self.site_root = settings.SITE_ROOT
        self.sub_models = settings.SUB_MODEL_DIR
        self.project_root_folder = os.path.join(self.site_root, self.project.name)


        try:
            self.site_root = settings.SCAFFOLD_APPS_DIR
        except:
            self.site_root = './'

    # Creates the application and all necessary other folders
    def create(self):

        # Check if app root folder exists; if not go on to create
        if not os.path.exists('{0}{1}'.format(self.site_root, self.project.name)):

            # run_all_steps creates all other application folders
            try:
                logger.info('Creating the project {0} ...'.format(self.project.name))

                call_command('startproject', self.project.name)

            except Exception as e:
                return {'Error':e}
            return True

        else:
            logger.info("Project folder exists\t{0}{1}".format(self.site_root, self.project.name))
            return {'Error':'Path exists'}

    def output_reader(self, proc):
        print('output reader thread started')
        while True:
            print("reading a line")
            nextline = proc.stdout.readline()
            if nextline != '':
                print('got line from outq: {0}'.format(nextline), end='')
            # if nextline != '':
                # outq.put(nextline.decode('utf-8'))

        # for line in iter(proc.stdout.readline, b''):
        #     outq.put(line.decode('utf-8'))



    def runserver(self):
        if settings.DEBUG:
            #call_command ile cagrilamaz.
            wd = os.getcwd()
            os.chdir(self.project.name)
            cwd = os.getcwd()
            print(cwd)
            python3bin = os.path.join(settings.VENV_PATH, "bin/python3")
            prjman = os.path.join(cwd, 'manage.py')
            print(python3bin)
            print(prjman)
            # Asagidaki popen'a python verildiginde virtual env tanimlanmis oluyor, ancak env bos verilince DJANGO_SETTINGS_MODULE
            # env var processi calistiran env den alinmamis oluyor.
            process = subprocess.Popen([python3bin, prjman, 'runserver', str(self.project.port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={}, universal_newlines=True , bufsize=1 )

            t = threading.Thread(target=self.output_reader, args=(process,))
            t.start()

            # try:
            #         try:
            #             line = outq.get(block=False)
            #             print('got line from outq: {0}'.format(line), end='')
            #         except queue.Empty:
            #             print('could not get line from queue')
            #         time.sleep(0.1)
            # finally:
            #     try:
            #         process.wait(timeout=0.2)
            #         print('== subprocess exited with rc =', process.returncode)
            #     except subprocess.TimeoutExpired:
            #         print('subprocess still running')
            # # t.join()


            # for line in output.read():
            #     print(line.strip())

            self.project.pid = process.pid
            # self.project.status = True
            # self.project.save()


            # call_command('runserver', self.application.port)
        else:
            pass

    def stopServer(pid):
        """ Check For the existence of a unix pid. """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True


    # Run all application creation steps
    def run_all_steps(self):
        # Output received from startapp django shell command
        cmd_output = StringIO()

        try:
            # Asagidaki kisim daha once yanlis bir yaklasimla yapilmisti.Django manage.py icin api sagliyor.Asagidaki buna gore yazildi
            # # Manage.py ile yeni uygulama uretim islemini burada yapiyorum; ne yazik ki return degeri yok, stdout'dan cikti okunuyor .
            # # Sadece exception handling ile bakabilinir.
            # os.system('python manage.py startapp {0}'.format(self.application.app_name))

            call_command('startapp',self.application.app_name,stdout=cmd_output)
            logger.info('=========================================================================================\n'
                        '\t\tNew Django application \'' + self.application.app_name + '\' has been created via manage.py.')
        except Exception as e:
            logger.fatal('Exception occured while creating django application: %s', str(e))
            raise Exception('./manage.py startapp failed : '+str(e))

        startapp = cmd_output.getvalue()
        res_flag=True

        # eger cmd_output ciktisi bos ise basarili bir sekilde uygulama uretilmistir.
        if startapp is "":
            try:

                logger.info(
                    "================================= STAGE 1 ==================================\nCreating folders and files for the application using templates\n")

                self.create_urls_file()
                self.create_application_folders()
                self.create_views_file()
                self.create_signals_file()
                self.create_forms_file()
                self.create_apps_file()
                self.create_models_file()
                self.create_template_files()
                self.send_create_signal()

                # self.updateAppsDBWoAppConfig()

                # Following is not a good method
                # updateProjectUrlsFile(request)
                #

                logger.info('Stage-1 DONE.')
            except:
                logger.error('Stage-1 FAILED, check subtask exception')



            try:

                logger.info(
                    "================================= STAGE 2 ==================================\n\t\t")
                # self.updateProjectUrlsPy()
                # self.updateProjectSettingsPy()
                logger.info(
                    "Stage-2 DONE.")

            except Exception as e:
                logger.error(
                    "Stage-2 FAILED, check subtask exception")

        else:
            logger.error("Manage.py could not create the app")
            logger.error(startapp)


    #
    # # Creates the urls.py file of the project
    # def create_urls_file(self):
    #     app_name = self.application.app_name
    #     url = self.application.namedUrl
    #
    #     # If aplication was already created run
    #     if os.path.exists('{0}{1}'.format(self.site_root, self.application.app_name)):
    #         logger.info('Creating urls.py for the new application : ' + self.application.app_name)
    #         try:
    #             t = loader.get_template('applicationManager/applicationFileTemplates/app_urls_template.txt')
    #             c = {'applicationName': self.application.app_name, 'url': url}
    #             rendered = t.render(c)
    #             open(self.site_root + "/" + app_name + "/urls.py", "w+").write(rendered)
    #
    #         except Exception as e:
    #             logger.fatal('Exception occured while creating Urls.py : %s', e)
    #             # Send the necessary signals to rollback
    #             application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                              application=Application.objects.get(app_name=app_name))
    #             raise Exception('create_urls_file failed')
    #
    #     else:
    #         logger.fatal("no such application: {0}".format(self.application.app_name))

    # Creates template and static folders
    # def create_application_folders(self):
    #     app_name = self.application.app_name
    #     # If aplication was already created run
    #     if os.path.exists('{0}{1}'.format(self.site_root, app_name)):
    #         logger.info('Creating extra folders for the new application')
    #
    #         signals_dir = self.site_root + "/" + app_name + "/signals/"
    #         template_dir = self.site_root + "/" + app_name + "/templates/" + app_name
    #         static_dir = self.site_root + "/" + app_name + "/static/" + app_name
    #         templatetags = self.site_root + "/" + app_name + "/templatetags/"
    #         fixtures = self.site_root + "/" + app_name + "/fixtures/"
    #         management = self.site_root + "/" + app_name + "/management/"
    #
    #         try:
    #             # Creating the folders
    #             if not os.path.exists(fixtures):
    #                 os.makedirs(fixtures)
    #                 open(fixtures + "/" + app_name + "_fixtures_readme.txt", "w+")
    #
    #             if not os.path.exists(templatetags):
    #                 os.makedirs(templatetags)
    #
    #             if not os.path.exists(management):
    #                 os.makedirs(management)
    #                 os.makedirs(management+ "/commands")
    #
    #             if not os.path.exists(template_dir):
    #                 os.makedirs(signals_dir)
    #
    #             if not os.path.exists(template_dir):
    #                 os.makedirs(template_dir)
    #
    #             if not os.path.exists(static_dir):
    #                 os.makedirs(static_dir)
    #                 os.makedirs(static_dir + "/jscript")
    #                 open(static_dir + "/jscript/" + app_name + ".jscript", "w+")
    #                 os.makedirs(static_dir + "/css")
    #                 open(static_dir + "/css/" + app_name + ".css", "w+")
    #                 copyfile(
    #                     self.site_root + "/applicationManager/templates/applicationManager/applicationFileTemplates/one-page-wonder.css",
    #                     static_dir + "/css/" + "/one-page-wonder.css")
    #
    #                 os.makedirs(static_dir + "/images")
    #                 copyfile(
    #                     self.site_root + "/applicationManager/templates/applicationManager/applicationFileTemplates/background.jpg",
    #                     static_dir + "/images/" + "/background.jpg")
    #
    #             logger.info('OK. Created necessary folders...')
    #         except Exception as e:
    #             logger.fatal("Exception occurred while creating Folders : %s", e)
    #             application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                              application=Application.objects.get(app_name=app_name))
    #
    #             raise Exception('unable to create folders: '+str(e))
    #
    #     else:
    #         logger.fatal("no such application: {0}".format(app_name))
    #
    # def create_views_file(self):
    #     app_name = self.application.app_name
    #     logger.info('Creating view files for the new application')
    #     try:
    #         t = loader.get_template(
    #             'applicationManager/applicationFileTemplates/app_views_template.txt')
    #         c = {'applicationName': app_name}
    #         rendered = t.render(c)
    #
    #         open(self.site_root + "/" + app_name + "/views.py", "w+").write(rendered)
    #
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating view file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('create views file failed: '+str(e))
    #
    #
    # def create_signals_file(self):
    #     app_name = self.application.app_name
    #     logger.info('Creating signals files for the new application')
    #     try:
    #         t = loader.get_template(
    #             'applicationManager/applicationFileTemplates/app_signals_init_template.txt')
    #
    #         c = {'applicationName': app_name}
    #         rendered = t.render(c)
    #
    #         open(self.site_root + "/" + app_name + "/signals/__init__.py", "w+").write(rendered)
    #
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating signals init file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('create signals init file failed: ' + str(e))
    #
    #     try:
    #         t = loader.get_template(
    #             'applicationManager/applicationFileTemplates/app_signals_handler_template.txt')
    #         c = {'applicationName': app_name}
    #         rendered = t.render(c)
    #
    #         open(self.site_root + "/" + app_name + "/signals/handler.py", "w+").write(rendered)
    #
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating signals handler file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('create signals handle file failed: ' + str(e))
    #
    #
    # def create_forms_file(self):
    #
    #     app_name = self.application.app_name
    #     logger.info('Creating forms for the new application')
    #     try:
    #         t = loader.get_template(
    #             'applicationManager/applicationFileTemplates/app_forms_template.txt')
    #         c = {'applicationName': app_name}
    #         rendered = t.render(c)
    #
    #         open(self.site_root + "/" + app_name + "/forms.py", "w+").write(rendered)
    #
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating view file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('create forms file failed: ' + str(e))
    #
    #
    # def create_apps_file(self):
    #     app_name = self.application.app_name
    #     verbose_name = self.application.verbose_name
    #     url = self.application.url
    #     namedUrl = self.application.namedUrl
    #     core_app = self.application.core_app
    #     # owner_id = request.POST['owner_id']
    #     description = self.application.description
    #     owner_id = 1
    #
    #     if self.application.active == 'on':
    #         active = "True"
    #     else:
    #         active = "False"
    #
    #     logger.info('Creating apps.py file for the new application')
    #
    #     try:
    #         t = loader.get_template(
    #             'applicationManager/applicationFileTemplates/apps.py.txt')
    #         c = {'app_name': app_name, 'verbose_name': verbose_name, 'url': url, 'namedUrl': namedUrl,
    #              'active': active,
    #              'core_app': core_app, 'owner_id': owner_id,
    #              'description': description}
    #         rendered = t.render(c)
    #
    #         t2 = loader.get_template(
    #             'applicationManager/applicationFileTemplates/init.py.txt')
    #
    #         # c = Context({'app_name': app_name,'verbose_name':verbose_name,'url':url,'namedUrl':namedUrl,'active':active,'readmeContent':readmeContent})
    #         renderedInit = t2.render(c)
    #
    #         open(self.site_root + "/" + app_name + "/apps.py", "w+").write(rendered)
    #         open(self.site_root + "/" + app_name + "/__init__.py", "w+").write(renderedInit)
    #     except Exception as e:
    #         logger.error("Exception occurred while creating apps.py file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('create apps.py file failed: ' + str(e))
    #
    #
    # def create_models_file(self):
    #
    #     """
    #     Method which creates the models.py file of the application using the models template
    #     @param app_name: name of the application to be created
    #     @return: returns 1 on success and 0 on fail
    #     """
    #     app_name = self.application.app_name
    #     logger.info('Creating default models for the new application')
    #     try:
    #         t = loader.get_template(
    #             'applicationManager/applicationFileTemplates/app_models_file_template.txt')
    #         c = {'applicationName': app_name}
    #         rendered = t.render(c)
    #         open(self.site_root + "/" + app_name + "/models.py", "w+").write(rendered)
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating models.py file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('create sample models failed: ' + str(e))
    #
    #
    # def del_between_lines(self, fp, start, end):
    #     fp = fp
    #     for i, line in enumerate(fp):
    #         if i == start:
    #             pass
    #         elif i == end:
    #             pass
    #         elif i > end:
    #             break
    #     fp.close()
    #
    # def create_model(self, model_id):
    #     """
    #     Creates the model if it does not exists, then fills(sync operation) the attributes. If model exists
    #     then again it just syncs the fields.
    #     """
    #     model = AppModel.objects.get(id=model_id)
    #     app_name = self.application.app_name
    #
    #     logger.info("---------- Model -------------")
    #
    #     with open('{0}{1}/models.py'.format(self.site_root, self.application.app_name), 'r+') as fo:
    #
    #         data = fo.readlines()
    #         fo.seek(0, 0)
    #         # Check if model already exists in models.py:
    #         # if it exists it means that it has been created manually return
    #         for line in data:
    #             if 'class {0}'.format(model) in line:
    #                 logger.info('exists\t{0}{1}/models.py'.format(self.site_root, self.application.app_name))
    #                 return
    #
    #         # So here it does not exist in models.py lets create it in sub_models folder
    #
    #         # Open sub_models directory
    #         if not os.path.exists('{0}{1}/{2}'.format(self.site_root, app_name, self.sub_models)):
    #             os.mkdir('{0}{1}/{2}'.format(self.site_root, app_name, self.sub_models))
    #
    #         # Rewrite the models file appending the import lines
    #         # open file
    #         # mfile = open('{0}{1}/models.py'.format(self.site_root, self.application.app_name, self.sub_models), 'r')
    #
    #         # fo.close()
    #
    #         # Models.py icindeki generated_models importu yoksa ekle
    #         # with open('{0}{1}/models.py'.format(self.site_root, self.application.app_name, self.sub_models), 'w') as fp:
    #         flag = True
    #         for line in data:
    #             if 'from {0}.{1}.generated_models'.format(app_name, self.sub_models) in line:
    #                 flag = False
    #                 break
    #
    #         if flag:
    #             fo.write('from {0}.{1}.generated_models import *'.format(app_name, self.sub_models) + "\n" + data)
    #
    #                     # --- Rewrite ends
    #
    #         if not os.path.exists('{0}{1}/{2}/generated_models.py'.format(self.site_root, app_name, self.sub_models)):
    #             f=open('{0}{1}/{2}/generated_models.py'.format(self.site_root, app_name, self.sub_models), 'w')
    #             f.close()
    #
    #         if self.model_exists(model_id, '{0}{1}/{2}/generated_models.py'.format(self.site_root, app_name,
    #                                                                                self.sub_models)):
    #             # Kaldirip terkar ekle, belki fieldlar degismistir.
    #             logger.info("Model exists")
    #             # Following line cleans the file.
    #             filename= '{0}{1}/{2}/generated_models.py'.format(self.site_root, app_name, self.sub_models)
    #             # f = open('{0}{1}/{2}/generated_models.py'.format(self.site_root, self.application.app_name, self.sub_models), 'w')
    #             # self.remove_model_from_file(model_id,
    #             #                             '{0}{1}/{2}/generated_models.py'.format(self.site_root, self.application.app_name,
    #             #                                                                     self.sub_models))
    #             self.append_model_to_file(model_id,filename)
    #         else:
    #             logger.info("no such model")
    #             self.append_model_to_file(model_id,
    #                                       '{0}{1}/{2}/generated_models.py'.format(self.site_root, app_name,
    #                                                                               self.sub_models))
    #
    # def line_prepender(self, filehandler, line):
    #     filehandler.seek(0, 0)
    #     data = filehandler.read()
    #
    #     print(data)
    #     filehandler.seek(0, 0)
    #     filehandler.write(line + "\n"+data)
    #
    # def remove_model_from_file(self, model_id, filepath):
    #     begin_line = 0
    #     end_line = 0
    #
    #     model_name = (AppModel.objects.get(id=model_id)).name
    #
    #     logger.info("Removing model "+model_name+" from generated_models file")
    #
    #     mfile = open(filepath, 'r')
    #     lines = mfile.readlines()
    #     mfile.close()
    #
    #     for ln, line in enumerate(lines):
    #
    #         if '#begin_' + model_name.format(self.application.app_name, self.sub_models) in line:
    #             begin_line = ln
    #
    #         if '#end_' + model_name.format(self.application.app_name, self.sub_models) in line:
    #             end_line = ln
    #
    #     wfile = open(filepath, 'w')
    #     #
    #     # for no, line in enumerate(lines):
    #     #     if begin_line <= no <= end_line:
    #     #         pass
    #     #     else:
    #     #         wfile.write(line)
    #
    # def str_exists(self, file, target_line):
    #     f = open(file, 'r')
    #     lines = f.readlines()
    #     f.close()
    #
    #     for line in lines:
    #         if target_line in line:
    #             return True
    #     return False
    #
    # def append_model_to_file(self, model_id, file):
    #
    #     # REFILL EVERYTHING
    #
    #     # Flag for inclusion of sub module directory
    #     inc_smdir = True
    #     inc_import_template = True
    #
    #     # Prepare fields
    #     self.imports = []
    #     fields = []
    #
    #     model = AppModel.objects.get(id=model_id)
    #     mfields = model.fields.all()
    #     print(mfields)
    #     for field in mfields:
    #         new_field = self.get_field(field)
    #         print(new_field)
    #         if new_field:
    #             fields.append(new_field)
    #
    #     print(fields)
    #
    #     with open(file, 'w') as fp:
    #         if not self.str_exists(file, "from " + model.app.app_name + ".models import *"):
    #             fp.write(IMPORT_MODEL_TEMPLATE % {"app": self.application.app_name, "model": "*"})
    #
    #         if not self.str_exists(file, "from django.db import models"):
    #             fp.write(IMPORT_DJANGO_DB)
    #
    #         # fp.write(''.join([import_line for import_line in self.imports]))
    #         fp.write(MODEL_TEMPLATE % {"model": model, "fields": ''.join(field for field in fields)})
    #
    #     if inc_smdir:
    #         with open('{0}{1}/models.py'.format(self.site_root, self.application.app_name), 'a') as fp:
    #             fp.write(IMPORT_SUB_MODEL_TEMPLATE % {"app": self.application.app_name, "sub_models_dir": self.sub_models})
    #
    # def create_template_files(self):
    #
    #     """
    #     This method creates the project compliant template files to be used with views.
    #     @param app_name: Application name to be created
    #     @param appUrl:  The URL of the applciation
    #     @return:  True or False depending on the success
    #     """
    #     app_name = self.application.app_name
    #     appUrl = self.application.url
    #
    #     logger.info('Creating template files for the new application')
    #     try:
    #         t = Template(
    #             filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_landing_html_template.txt')
    #         # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
    #         buf = StringIO()
    #         c = mako.runtime.Context(buf, applicationName=app_name)
    #         t.render_context(c)
    #
    #         open(self.site_root + "/" + app_name + "/templates/" + app_name + "/landing.html", "w+").write(
    #             buf.getvalue())
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating index2.html file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('creation of index2.html failed: ' + str(e))
    #
    #     try:
    #         t = Template(
    #             filename='applicationManager/templates/applicationManager/applicationFileTemplates/application_app-template-file_template.txt')
    #         # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
    #         buf = StringIO()
    #         c = mako.runtime.Context(buf, applicationName=app_name)
    #         t.render_context(c)
    #
    #         open(self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_app_template.html",
    #              "w+").write(buf.getvalue())
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating app_template.html file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('creation of app template file failed: ' + str(e))
    #     try:
    #         t = Template(
    #             filename='applicationManager/templates/applicationManager/applicationFileTemplates/application_dashboard_navbar_template.txt')
    #         buf = StringIO()
    #         c = mako.runtime.Context(buf, applicationName=appUrl)
    #         t.render_context(c)
    #
    #         open(self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_navbar.html",
    #              "w+").write(
    #             buf.getvalue())
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating navbar.html file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('creation of navbar.html failed: ' + str(e))
    #     try:
    #         t = Template(
    #             filename='applicationManager/templates/applicationManager/applicationFileTemplates/application_dashboard_navbar_template2.txt')
    #         buf = StringIO()
    #         c = mako.runtime.Context(buf, applicationName=appUrl)
    #         t.render_context(c)
    #
    #         open(self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_navbar2.html",
    #              "w+").write(
    #             buf.getvalue())
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating navbar.html file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('creation of navbar2.html failed: ' + str(e))
    #
    #     try:
    #         t = Template(
    #             filename='applicationManager/templates/applicationManager/applicationFileTemplates/application_dashboard_left_sidebar_template.txt')
    #         buf = StringIO()
    #         c = mako.runtime.Context(buf, applicationName=appUrl)
    #         t.render_context(c)
    #
    #         open(self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_left_sidebar.html",
    #              "w+").write(
    #             buf.getvalue())
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating navbar.html file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('creation of left_sidebar.html failed: ' + str(e))
    #
    #     try:
    #         t = Template(
    #             filename='applicationManager/templates/applicationManager/applicationFileTemplates/application-wide_navbar_template.txt')
    #         buf = StringIO()
    #         c = mako.runtime.Context(buf, applicationName=appUrl)
    #         t.render_context(c)
    #
    #         open(
    #             self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_landing_page_navbar.html",
    #             "w+").write(
    #             buf.getvalue())
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating landing page navbar.html file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('creation of landing_page_navbar failed: ' + str(e))
    #
    #     try:
    #         t = Template(
    #             filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_new_page_template.txt')
    #         buf = StringIO()
    #         c = mako.runtime.Context(buf, applicationName=appUrl)
    #         t.render_context(c)
    #
    #         open(self.site_root + "/" + app_name + "/templates/" + app_name + "/new_page_template.html",
    #              "w+").write(
    #             buf.getvalue())
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating navbar.html file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('creation of new_page_template.html failed: ' + str(e))
    #
    #     try:
    #         t = Template(
    #             filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_index_html_template.txt')
    #         # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
    #         buf = StringIO()
    #         c = mako.runtime.Context(buf, applicationName=app_name)
    #         t.render_context(c)
    #
    #         open(self.site_root + "/" + app_name + "/templates/" + app_name + "/dashboard.html", "w+").write(
    #             buf.getvalue())
    #     except Exception as e:
    #         logger.fatal("Exception occurred while creating dashboard.html file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=app_name))
    #         raise Exception('creation of dashboard.html failed: ' + str(e))
    #     return True
    #
    # def updateProjectUrlsPy(self):
    #     """
    #        This method created the Urls.py file for the entire project using a template file.
    #        Method reads application table and create the necessary file.
    #     """
    #
    #     try:
    #         logger.info(
    #             "\n--------------------------------------------------------\n\t\tRefreshing application list in urls.py")
    #         copyfile(self.site_root + "/" + settings.APPLICATION_NAME + "/urls.py",
    #                  self.site_root + "/" + settings.APPLICATION_NAME + "/urls.py.backup")
    #         t = loader.get_template('applicationManager/applicationFileTemplates/project_urls_py.txt')
    #
    #         apps = Application.objects.all()
    #
    #         c = {'applist': apps}
    #         rendered = t.render(c)
    #
    #         open(self.site_root + "/" + settings.APPLICATION_NAME + "/urls.py", "w+").write(rendered)
    #     except Exception as e:
    #         raise Exception('updateProjectUrlsPy failed: '+str(e))
    # # def updateProjectUrlsPy(self):
    # #     """
    # #         This method created the Urls.py file for the entire project using a template file.
    # #
    # #     """
    # #     logger.info("\n--------------------------------------------------------------\n\t\t"
    # #                 "Refreshing application list in urls.py")
    # #     t = loader.get_template('applicationManager/applicationFileTemplates/project_urls_py.txt')
    # #
    # #     app_nameList = getAppNameListByAppsPy()
    # #     print("Applications which will be created in database : " + str(app_nameList))
    # #
    # #     try:
    # #         allapps = Application.objects.all()
    # #         allapps.delete()
    # #         print("deleted applications table content")
    # #     except  Exception as e:
    # #         print("Deletion of database entries for applications failed")
    # #
    # #     appConfigs = []
    # #     for app_name in app_nameList:
    # #         pass
    # #         # Application config ile bu islemin yapilmasi durumu imkansiz: Cunku appconfig kullanmak icin
    # #         # app settings dosyasinda olmali ama bu durumda uygulama yeniden basladigi icin tum uygulama akisi
    # #         # resetlenmektedir.
    # #         # # confName = app_name+'AppConfig'
    # #         # print(app_name)
    # #         # appConf = apps.get_app_config(app_name)
    # #         # appConfigs.append(appConf)
    # #         # print(appConf)
    # #         # # print(appConf.yvar)
    # #
    # #     c = Context({'applist': appConfigs})
    # #     rendered = t.render(c)
    # #
    # #     # buf = StringIO()
    # #     # c = mako.runtime.Context(buf, applist=appConfigs)
    # #     # t.render_context(c)
    # #
    # #     open(self.site_root + "/" + settings.APPLICATION_NAME + "/urls.py", "w+").write(rendered)
    #
    # # Updates only the settings file
    # def updateProjectSettingsPy(self):
    #     try:
    #         copyfile(self.site_root + "/" + settings.APPLICATION_NAME + "/settings.py",
    #                  self.site_root + "/" + settings.APPLICATION_NAME + "/settings.py." + str(
    #                      datetime.datetime.now().isoformat()))
    #         appList = Application.objects.all()
    #         print("List of applications to be added to the settings file :" + str(appList))
    #
    #         t = loader.get_template('applicationManager/applicationFileTemplates/project_settings_py.txt')
    #         c = {'appList': appList}
    #         rendered = t.render(c)
    #         open(self.site_root + "/" + settings.APPLICATION_NAME + "/settings.py", "w+").write(rendered)
    #     except  Exception as e:
    #
    #         logger.fatal("Exception occurred while updating project settings file : %s", e)
    #         application_creation_failed_signal.send(sender=Application.__class__, test="testString",
    #                                          application=Application.objects.get(app_name=self.application.app_name))
    #         raise Exception('creation of project settings.py failed: ' + str(e))
    #
    # def rollback(self):
    #     logger.error("Rolling back the installation")
    #     raise NotImplementedError
    #     pass
    #
    # def get_import(self, model):
    #     for dir in os.listdir(self.site_root):
    #         if os.path.isdir('{0}{1}'.format(self.site_root, dir)) \
    #                 and os.path.exists('{0}{1}/models.py'.format(self.site_root, dir)):
    #             with open('{0}{1}/models.py'.format(self.site_root, dir), 'r') as fp:
    #                 # Check if model exists
    #                 for line in fp.readlines():
    #                     if 'class {0}(models.Model)'.format(model) in line:
    #                         # print "Foreign key '%s' was found in app %s..." % (model, dir)
    #                         return IMPORT_MODEL_TEMPLATE % {'app': dir, 'model': model}
    #     return None
    #
    # def is_imported(self, path, model):
    #     with open(path, 'r') as import_file:
    #         for line in import_file.readlines():
    #             if 'import {0}'.format(model) in line:
    #                 print("Foreign key '%s' was found in models.py..." % (model))
    #                 return True
    #     return False
    #
    # def is_declared(self, path, model):
    #     with open(path, 'r') as import_file:
    #         for line in import_file.readlines():
    #             if 'class {0}'.format(model.capitalize()) in line:
    #                 logger.info("Foreign key '%s' was found in models.py..." % (model))
    #                 return True
    #     return False
    #
    # def get_type_parameters(self, field):
    #     # parameter list is assumed comma seperated equity phrases
    #     params = field.type_parameter
    #
    #     if params == "":
    #         return None
    #     else:
    #         # try:
    #         #     if isinstance(params,six.string_types):
    #         #
    #         #     else:
    #         #         print(params.__class__)
    #         # except ValueError as e:
    #         #     logger.fatal("Json document is not well formatted : "+params)
    #
    #         pass
    #
    # def get_field(self, field):
    #     self.get_type_parameters(field)
    #
    #     # Default vals
    #     field_name = field.name
    #     null_val = True
    #     blank_val = True
    #     lenght_val = "255"
    #     default_val = "255"
    #     digits_val = "3"
    #     places_val = "3"
    #
    #     print(field)
    #     print(field.__class__)
    #
    #     tp = field.type_parameter
    #     try:
    #         tp = tp.split(",")
    #     except:
    #         logger.warning("No comma seperated input")
    #
    #     for param in tp:
    #         try:
    #             param_key, param_val = param.split(":")
    #         except:
    #             logger.error("parameter format is not correct")
    #             break
    #
    #         if param_key.lower() == "null":
    #             null_val = param_val
    #
    #         if param_key.lower() == "blank":
    #             blank_val = param_val
    #
    #         if param_key.lower() == "length":
    #             lenght_val = param_val
    #
    #         if param_key.lower() == "default":
    #             default_val = param_val
    #
    #         if param_key.lower() == "digits":
    #             digits_val = param_val
    #
    #         if param_key.lower() == "places":
    #             places_val = param_val
    #
    #         if param_key.lower() == "foreign":
    #             foreign_val = param_val
    #
    #     if field.type.lower() == 'char' or field.type.lower() == 'charfield' :
    #         return CHARFIELD_TEMPLATE % {'name': field_name, 'length': lenght_val, 'null': null_val, 'blank': blank_val}
    #
    #     elif field.type.lower() == 'text' or field.type.lower() == 'textfield':
    #         return TEXTFIELD_TEMPLATE % {'name': field_name, 'null': null_val}
    #
    #     elif field.type.lower() == 'int' or field.type.lower() == 'integerfield':
    #         return INTEGERFIELD_TEMPLATE % {'name': field_name, 'null': null_val, 'default': default_val}
    #
    #     elif field.type.lower() == 'decimal' or field.type.lower() == 'decimalfield':
    #         return DECIMALFIELD_TEMPLATE % {
    #             'name': field_name,
    #             'digits': digits_val,
    #             'places': places_val,
    #             'null': null_val,
    #             'default': default_val,
    #         }
    #     elif field.type.lower() == 'datetime' or field.type.lower() == 'datetimesssfield':
    #
    #         return DATETIMEFIELD_TEMPLATE % {'name': field_name, 'null': null_val, 'default': default_val}
    #
    #     elif field.type.lower() == 'foreign':
    #         foreign = foreign_val
    #         name = field_name
    #         # Check if this foreign key is already in models.py
    #         if foreign in ('User', 'Group'):
    #             if not self.is_imported('{0}{1}/models.py'.format(self.site_root,
    #                                                               self.application.app_name), foreign):
    #                 self.imports.append('\nfrom django.contrib.auth.models import User, Group\n')
    #             return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign, 'null': 'True'}
    #
    #         if self.is_imported('{0}{1}/models.py'.format(
    #                 self.site_root, self.application.app_name), foreign) or self.is_declared('{0}{1}/models.py'.format(
    #             self.site_root, self.application.app_name), foreign):
    #             return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign, 'null': 'True'}
    #
    #         # Check imports
    #         if self.get_import(foreign):
    #             self.imports.append(self.get_import(foreign))
    #             return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign, 'null': 'True'}
    #
    #         logger.info('error\t{0}{1}/models.py\t{2} class not found'.format(
    #             self.site_root, self.application.app_name, foreign), 1)
    #         return None
    #
    # def model_exists(self, model_id, file):
    #
    #     mfile = open(file.format(self.site_root, self.application.app_name, self.sub_models), 'r')
    #     lines = mfile.readlines()
    #     mfile.close()
    #
    #     model_name = (AppModel.objects.get(id=model_id)).name
    #
    #     for line in lines:
    #         if 'class ' + model_name + '(models.Model):'.format(self.application.app_name, self.sub_models) in line:
    #             return True
    #     return False

