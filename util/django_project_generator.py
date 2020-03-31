__author__ = 'ozgur'

import subprocess
import threading
import os
import logging
import psutil

import mako
from mako.template import Template

from applicationManager.models import DjangoProject, Application
from io import StringIO
from django.conf import settings
from django.core.management import call_command

from applicationManager.signals.signals import application_creation_failed_signal

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



allow_read=True

class DjangoProjectGenerator:

    def __init__(self, project: DjangoProject):
        # Project object is coming from the database records which holds the metadata of the project

        self.project = project
        self.dprjLoc = settings.SCAFFOLD_DPRJ_DIR
        self.dprjDir = os.path.join(settings.SCAFFOLD_DPRJ_DIR, self.project.name)
        self.site_root = settings.SCAFFOLD_APPS_DIR
        self.sub_models = settings.SUB_MODEL_DIR
        self.project_root_folder = os.path.join(self.site_root, self.project.name)
        self.app_name = "ms"





    def create_file_from_template(self,template_file, context, loc):

        try:
            t = Template(filename=template_file)
            buf = StringIO()
            c = mako.runtime.Context(buf, data=context)
            t.render_context(c)

            open(loc, "w+").write(buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating blank.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=self.app_name))
            raise Exception('creation of blank.html failed: ' + str(e))





    def delete_project(self):
        os.remove(self.project_root_folder)

    def create(self):
        """
        Creates a django project and an application with all necessary secondary folders
        """

        print(self.dprjLoc)
        # Check if app root folder exists; if not go on to create
        if not os.path.exists('{0}{1}'.format(self.dprjLoc, self.project.name)):

            # First generate the Django Project
            try:
                logger.info('Creating the project {0} ...'.format(self.project.name))
                os.chdir(self.dprjLoc)
                call_command('startproject', self.project.name)
            except Exception as e:
                return {'Error': e}

            # Then create a fully functional app in the project
            try:
                self.run_all_steps()
            except Exception as e:
                return

            return True

        else:
            logger.info("Project folder exists\t{0}{1}".format(self.site_root, self.project.name))
            return {'Error': 'Path exists'}


    def output_reader(self, proc):
        """
        Called from the thread started in run server and reads and prints the output for
        this threaded django instance.
        """
        print('output reader thread started')
        global allow_read
        while allow_read:

            nextline = proc.stdout.readline()
            if nextline != '' and nextline != b'':
                print('got line from output: {0}\n'.format(nextline), end='')


    def runServer(self):
        if settings.DEBUG:
            # call_command ile cagrilamaz.
            wd = os.getcwd()
            os.chdir(os.path.join(settings.SCAFFOLD_DPRJ_DIR, self.project.name))

            cwd = os.getcwd()
            print(cwd)
            python3bin = os.path.join(settings.VENV_PATH, "bin/python3")
            prjman = os.path.join(cwd, 'manage.py')
            print(python3bin)
            print(prjman)
            # Asagidaki popen'a python verildiginde virtual env tanimlanmis oluyor,
            # ancak env bos verilince DJANGO_SETTINGS_MODULE
            # env var processi calistiran env den alinmamis oluyor.
            process = subprocess.Popen([python3bin, prjman, 'runserver', str(self.project.port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={})

            comm = "pgrep -f {}".format(self.project.name)
            bpids = subprocess.check_output(comm, shell=True)

            pids = bpids.decode("utf-8").rstrip("\n").split("\n")

            ipids = [int(i) for i in pids]

            self.project.pids = ipids
            self.project.save()

            global allow_read
            allow_read = True

            t = threading.Thread(target=self.output_reader, args=(process,))
            t.start()

            os.chdir(wd)
            # call_command('runserver', self.application.port)
        else:
            pass

    def stopServer(self):
        """ Check For the existence of a unix pid. """
        try:
            global allow_read
            allow_read = False
            for i in self.project.pids.strip('][').split(', '):

                cmd = "pkill -P {}".format(int(i))
                print(subprocess.check_output(cmd, shell=True))
            self.project.pids=[]
            self.project.save()

        except OSError:
            return False
        else:
            return True



    def run_all_steps(self):
        """
        Run all application creation steps
        """
        # Output received from startapp django shell command
        cmd_output = StringIO()

        try:
            # Asagidaki kisim daha once yanlis bir yaklasimla yapilmisti.Django manage.py icin api sagliyor.Asagidaki buna gore yazildi
            # # Manage.py ile yeni uygulama uretim islemini burada yapiyorum; ne yazik ki return degeri yok, stdout'dan cikti okunuyor .
            # # Sadece exception handling ile bakabilinir.
            # os.system('python manage.py startapp {0}'.format(self.application.app_name))
            os.chdir(self.dprjDir)
            call_command('startapp',self.app_name, stdout=cmd_output)
            logger.info('=========================================================================================\n'
                        '\t\tNew Django application \'' + self.app_name + '\' has been created via manage.py.')
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

    def create_urls_file(self):
        template_file = "applicationManager/templates/applicationManager/applicationFileTemplates/app_urls_template.txt"
        context = {'applicationName': self.app_name, 'url': self.app_name, 'models': self.app.models.all()}
        loc = self.dprjDir + "/" + self.app_name + "/urls.py"

        self.create_file_from_template(template_file, context, loc)


