__author__ = 'ozgur'

from shutil import copyfile
from django.core.management import call_command
from applicationManager.models import Application, AppModel
from applicationManager.signals.signals import application_creation_failed_signal, application_files_created_signal

import mako
import os
import logging
import datetime
from mako import runtime
from mako.template import Template
from django.template import loader
from io import StringIO
from django.conf import settings

from applicationManager.util.Exceptions import SiteRootNotSetException, StageException, \
    ManagePyStartAppException, ApplicationFolderExistsException, UrlPyCreationException

logger = logging.getLogger("wbdap.debug")
slogger = logging.getLogger("wbdap.sdebug")

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


class DjangoApplicationCreator:
    def __init__(self, application: Application):
        # Application object is coming from the database records
        # which holds the metadata of the application

        self.app = application
        self.site_root = settings.SITE_ROOT
        self.sub_models = settings.SUB_MODEL_DIR

        # check if the custom_settings file has the attribute;
        # otherwise set the root of the folder as site.root
        if hasattr(settings, 'SCAFFOLD_APPS_DIR'):
            self.site_root = settings.SCAFFOLD_APPS_DIR
        else:
            self.site_root = './'

    def create(self):
        """Creates the django application and all necessary extra folders and files"""
        logger.info("Starting the app creation")

        # Check if site_root variable is set ; otherwise raise except
        try:
            self.site_root
        except Exception as e:
            logger.fatal("Site root not set exception")
            raise SiteRootNotSetException

        # Check if set siteroot exists, otherwise raise exception
        if not os.path.exists('{0}'.format(self.site_root)):
            logger.fatal("SCAFFOLD_APPS_DIR {0} does not exists".format(self.site_root))
            raise Exception("SCAFFOLD_APPS_DIR {0} does not exists".format(self.site_root))

        # Check if app folder exists, if it is raise exception
        if os.path.exists(os.path.join(self.site_root, self.app.app_name)):
            logger.fatal("Application folder exists\t{0}/{1}".format(self.site_root, self.app.app_name))
            raise ApplicationFolderExistsException(
                "Application folder exists\t{0}/{1}".format(self.site_root, self.app.app_name))

        # If all of the above requirements are ok, call run_all_steps which creates all other application files and folders
        try:
            logger.info('Creating the application {0} ...'.format(self.app.app_name))
            self.run_all_steps()
        except Exception as e:
            logger.fatal('A fatal stage exception occurred, rolling back all changes ...')
            self.rollback()
            raise StageException
        except ManagePyStartAppException as e:
            self.rollback()
            raise StageException
        return True

    def run_manage_py(self):
        """Create the application using the django manage.py command"""
        # Output received from startapp django shell command
        cmd_output = StringIO()

        try:
            # Asagidaki kisim daha once yanlis bir yaklasimla yapilmisti.Django manage.py icin api
            # sagliyor.Asagidaki buna gore yazildi
            # # Manage.py ile yeni uygulama uretim islemini burada yapiyorum; ne yazik ki
            # return degeri yok, stdout'dan cikti okunuyor .
            # # Sadece exception handling ile bakilabilinir.
            # os.system('python manage.py startapp {0}'.format(self.app.app_name))

            call_command('startapp', self.app.app_name, stdout=cmd_output)
            logger.info('=========================================================================================\n'
                        'New Django application \'' +
                        self.app.app_name +
                        '\' has just been created programmatically via manage.py.')

        except Exception as e:
            logger.fatal('Exception occured while creating django application: %s', str(e))
            raise ManagePyStartAppException

        startapp = cmd_output.getvalue()

        # eger cmd_output ciktisi bos ise basarili bir sekilde uygulama uretilmistir.
        if startapp is "":
            return True
        else:
            return False

    def run_all_steps(self):
        """
        Run all app creation steps in order
        """
        try:
            if self.run_manage_py():
                logger.info(
                    "================================= STAGE 1 ==================================\n"
                    "Creating folders and files for the application using templates\n")

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
                return True
        except ManagePyStartAppException:
            raise
        except Exception as e:
            logger.fatal('A Stage-1 step FAILED, check subtask exception: %s' % e)
            raise

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

    def create_urls_file(self):
        """"Creates the urls.py file of the project using a template file"""
        # If aplication was already created run: we are rechecking this as this method can be called independently later
        if os.path.exists('{0}/{1}'.format(self.site_root, self.app.app_name)):
            logger.info('Creating urls.py for the new application : ' + self.app.app_name)
            try:
                t = loader.get_template('applicationManager/applicationFileTemplates/app_urls_template.txt')
                c = {'applicationName': self.app.app_name, 'url': self.app.namedUrl, 'models': self.app.models.all()}
                rendered = t.render(c)
                open(self.site_root + "/" + self.app.app_name + "/urls.py", "w+").write(rendered)

            except Exception as e:
                logger.fatal('Exception occured while creating Urls.py : %s', e)
                # Send the necessary signals to rollback
                application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                        application=Application.objects.get(app_name=self.app.app_name))
                raise UrlPyCreationException('create_urls_file failed: '+str(e))
        else:
            logger.fatal("no such application: {0}".format(self.app.app_name))

    def create_application_folders(self):
        """Create template, signals, handlers and static file folders"""

        # If aplication was already created run
        if os.path.exists('{0}/{1}'.format(self.site_root, self.app.app_name)):
            logger.info('Creating supporting folders for the new application')

            signals_dir = self.site_root + "/" + self.app.app_name + "/signals/"
            template_dir = self.site_root + "/" + self.app.app_name + "/templates/" + self.app.app_name
            static_dir = self.site_root + "/" + self.app.app_name + "/static/" + self.app.app_name
            templatetags = self.site_root + "/" + self.app.app_name + "/templatetags/"
            fixtures = self.site_root + "/" + self.app.app_name + "/fixtures/"
            management = self.site_root + "/" + self.app.app_name + "/management/"

            try:
                # Creating the folders
                if not os.path.exists(fixtures):
                    os.makedirs(fixtures)
                    open(fixtures + "/" + self.app.app_name + "_fixtures_readme.txt", "w+")
                    slogger.info("Created fixtures folder")

                if not os.path.exists(templatetags):
                    os.makedirs(templatetags)
                    slogger.info("Created templatetags folder")

                if not os.path.exists(management):
                    os.makedirs(management)
                    os.makedirs(management + "/commands")
                    slogger.info("Created management folder")

                if not os.path.exists(signals_dir):
                    os.makedirs(signals_dir)
                    slogger.info("Created signals folder")

                if not os.path.exists(template_dir):
                    os.makedirs(template_dir)

                if not os.path.exists(static_dir):
                    os.makedirs(static_dir)
                    os.makedirs(static_dir + "/jscript")
                    open(static_dir + "/jscript/" + self.app.app_name + ".jscript", "w+")
                    os.makedirs(static_dir + "/css")
                    open(static_dir + "/css/" + self.app.app_name + ".css", "w+")
                    copyfile(
                        self.site_root + "/applicationManager/templates/applicationManager/applicationFileTemplates/one-page-wonder.css",
                        static_dir + "/css/" + "/one-page-wonder.css")

                    os.makedirs(static_dir + "/images")
                    copyfile(
                        self.site_root + "/applicationManager/templates/applicationManager/applicationFileTemplates/background.jpg",
                        static_dir + "/images/" + "/background.jpg")
                    slogger.info("Created statics folder")

                logger.info('OK. Created necessary folders...')
            except Exception as e:
                logger.fatal("Exception occurred while creating Folders : %s", e)
                application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                        application=Application.objects.get(app_name=self.app.app_name))

                raise Exception('unable to create folders: ' + str(e))

        else:
            logger.fatal("no such application: {0}".format(self.app.app_name))

    def create_views_file(self):
        """Create default views for the application"""

        try:
            t = loader.get_template(
                'applicationManager/applicationFileTemplates/app_views_template.txt')
            c = {'applicationName': self.app.app_name,'models': self.app.models.all()}
            rendered = t.render(c)

            open(self.site_root + "/" + self.app.app_name + "/views.py", "w+").write(rendered)
            slogger.info('Created view files')
        except Exception as e:
            logger.fatal("Exception occurred while creating view file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=self.app.app_name))
            raise Exception('create views file failed: ' + str(e))

    def create_signals_file(self):
        """Create default signals and handles file for the application"""

        try:
            t = loader.get_template(
                'applicationManager/applicationFileTemplates/app_signals_file_template.txt')
            c = {'applicationName': self.app.app_name}
            rendered = t.render(c)

            open(self.site_root + "/" + self.app.app_name + "/signals/__init__.py", "w+").write("__author__ = 'ozgur'")
            open(self.site_root + "/" + self.app.app_name + "/signals/signals.py", "w+").write(rendered)
            slogger.info('Created signals files')
        except Exception as e:
            logger.fatal("Exception occurred while creating signals init file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=self.app.app_name))
            raise Exception('create signals init file failed: ' + str(e))

        try:
            t = loader.get_template(
                'applicationManager/applicationFileTemplates/app_signals_handler_template.txt')
            c = {'applicationName': self.app.app_name}
            rendered = t.render(c)

            open(self.site_root + "/" + self.app.app_name + "/signals/handler.py", "w+").write(rendered)
            slogger.info('Created signal handler files')
        except Exception as e:
            logger.fatal("Exception occurred while creating signals handler file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=self.app.app_name))
            raise Exception('create signals handle file failed: ' + str(e))

    def create_forms_file(self):
        """Create default forms files for the application"""

        try:
            t = loader.get_template(
                'applicationManager/applicationFileTemplates/app_forms_template.txt')
            c = {'applicationName': self.app.app_name}
            rendered = t.render(c)

            open(self.site_root + "/" + self.app.app_name + "/forms.py", "w+").write(rendered)
            slogger.info('Created forms')
        except Exception as e:
            logger.fatal("Exception occurred while creating view file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=self.app.app_name))
            raise Exception('create forms file failed: ' + str(e))

    def create_apps_file(self):
        """Creates the apps file for the application"""

        app_name = self.app.app_name
        verbose_name = self.app.verbose_name
        url = self.app.url
        namedUrl = self.app.namedUrl
        core_app = self.app.core_app
        # owner_id = request.POST['owner_id']
        description = self.app.description
        owner_id = 1

        if self.app.active == 'on':
            active = "True"
        else:
            active = "False"

        try:
            t = loader.get_template(
                'applicationManager/applicationFileTemplates/apps.py.txt')
            c = {'app_name': app_name, 'verbose_name': verbose_name, 'url': url, 'namedUrl': namedUrl,
                 'active': active,
                 'core_app': core_app, 'owner_id': owner_id,
                 'description': description}
            rendered = t.render(c)

            t2 = loader.get_template(
                'applicationManager/applicationFileTemplates/init.py.txt')

            # c = Context({'app_name': app_name,'verbose_name':verbose_name,'url':url,'namedUrl':namedUrl,'active':active,'readmeContent':readmeContent})
            renderedInit = t2.render(c)

            open(self.site_root + "/" + app_name + "/apps.py", "w+").write(rendered)
            open(self.site_root + "/" + app_name + "/__init__.py", "w+").write(renderedInit)
            slogger.info('Created apps.py and __init__.py file')
        except Exception as e:
            logger.error("Exception occurred while creating apps.py file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('create apps.py file failed: ' + str(e))

    def create_models_file(self):

        """
        Method which creates the models.py file of the application using the models template
        @param app_name: name of the application to be created
        @return: returns 1 on success and 0 on fail
        """
        app_name = self.app.app_name
        logger.info('Creating default models for the new application')
        try:
            t = loader.get_template(
                'applicationManager/applicationFileTemplates/app_models_file_template.txt')
            c = {'applicationName': app_name,'models':self.app.models.all()}
            rendered = t.render(c)
            open(self.site_root + "/" + app_name + "/models.py", "w+").write(rendered)
        except Exception as e:
            logger.fatal("Exception occurred while creating models.py file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('create sample models failed: ' + str(e))

    def del_between_lines(self, fp, start, end):
        fp = fp
        for i, line in enumerate(fp):
            if i == start:
                pass
            elif i == end:
                pass
            elif i > end:
                break
        fp.close()

    def create_model(self, model_id):
        """
        Creates the model if it does not exists, then fills(sync operation) the attributes. If model exists 
        then again it just syncs the fields.
        """
        model = AppModel.objects.get(id=model_id)
        app_name = self.app.app_name

        logger.info("---------- Model -------------")

        with open('{0}/{1}/models.py'.format(self.site_root, self.app.app_name), 'r+') as fo:

            data = fo.readlines()
            fo.seek(0, 0)
            # Check if model already exists in models.py:
            # if it exists it means that it has been created manually return
            for line in data:
                if 'class {0}'.format(model) in line:
                    logger.info('exists\t{0}/{1}/models.py'.format(self.site_root, self.app.app_name))
                    return

            # So here it does not exist in models.py lets create it in sub_models folder

            # Open sub_models directory
            if not os.path.exists('{0}/{1}/{2}'.format(self.site_root, app_name, self.sub_models)):
                os.mkdir('{0}/{1}/{2}'.format(self.site_root, app_name, self.sub_models))

            # Rewrite the models file appending the import lines
            # open file
            # mfile = open('{0}/{1}/models.py'.format(self.site_root, self.app.app_name, self.sub_models), 'r')

            # fo.close()

            # Models.py icindeki generated_models importu yoksa ekle
            # with open('{0}/{1}/models.py'.format(self.site_root, self.app.app_name, self.sub_models), 'w') as fp:
            flag = True
            for line in data:
                if 'from {0}.{1}.generated_models'.format(app_name, self.sub_models) in line:
                    flag = False
                    break

            if flag:
                fo.write('from {0}.{1}.generated_models import *'.format(app_name, self.sub_models) + "\n" + data)

                # --- Rewrite ends

            if not os.path.exists('{0}/{1}/{2}/generated_models.py'.format(self.site_root, app_name, self.sub_models)):
                f = open('{0}/{1}/{2}/generated_models.py'.format(self.site_root, app_name, self.sub_models), 'w')
                f.close()

            if self.model_exists(model_id, '{0}/{1}/{2}/generated_models.py'.format(self.site_root, app_name,
                                                                                   self.sub_models)):
                # Kaldirip terkar ekle, belki fieldlar degismistir.
                logger.info("Model exists")
                # Following line cleans the file.
                filename = '{0}/{1}/{2}/generated_models.py'.format(self.site_root, app_name, self.sub_models)
                # f = open('{0}/{1}/{2}/generated_models.py'.format(self.site_root, self.app.app_name, self.sub_models), 'w')
                # self.remove_model_from_file(model_id,
                #                             '{0}/{1}/{2}/generated_models.py'.format(self.site_root, self.app.app_name,
                #                                                                     self.sub_models))
                self.append_model_to_file(model_id, filename)
            else:
                logger.info("no such model")
                self.append_model_to_file(model_id,
                                          '{0}/{1}/{2}/generated_models.py'.format(self.site_root, app_name,
                                                                                  self.sub_models))

    def line_prepender(self, filehandler, line):
        filehandler.seek(0, 0)
        data = filehandler.read()

        print(data)
        filehandler.seek(0, 0)
        filehandler.write(line + "\n" + data)

    def remove_model_from_file(self, model_id, filepath):
        begin_line = 0
        end_line = 0

        model_name = (AppModel.objects.get(id=model_id)).name

        logger.info("Removing model " + model_name + " from generated_models file")

        mfile = open(filepath, 'r')
        lines = mfile.readlines()
        mfile.close()

        for ln, line in enumerate(lines):

            if '#begin_' + model_name.format(self.app.app_name, self.sub_models) in line:
                begin_line = ln

            if '#end_' + model_name.format(self.app.app_name, self.sub_models) in line:
                end_line = ln

        wfile = open(filepath, 'w')
        #
        # for no, line in enumerate(lines):
        #     if begin_line <= no <= end_line:
        #         pass
        #     else:
        #         wfile.write(line)

    def str_exists(self, file, target_line):
        f = open(file, 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            if target_line in line:
                return True
        return False

    def append_model_to_file(self, model_id, file):

        # REFILL EVERYTHING

        # Flag for inclusion of sub module directory
        inc_smdir = True
        inc_import_template = True

        # Prepare fields
        self.imports = []
        fields = []

        model = AppModel.objects.get(id=model_id)
        mfields = model.fields.all()
        print(mfields)
        for field in mfields:
            new_field = self.get_field(field)
            print(new_field)
            if new_field:
                fields.append(new_field)

        print(fields)

        with open(file, 'w') as fp:
            if not self.str_exists(file, "from " + model.app.app_name + ".models import *"):
                fp.write(IMPORT_MODEL_TEMPLATE % {"app": self.app.app_name, "model": "*"})

            if not self.str_exists(file, "from django.db import models"):
                fp.write(IMPORT_DJANGO_DB)

            # fp.write(''.join([import_line for import_line in self.imports]))
            fp.write(MODEL_TEMPLATE % {"model": model, "fields": ''.join(field for field in fields)})

        if inc_smdir:
            with open('{0}/{1}/models.py'.format(self.site_root, self.app.app_name), 'a') as fp:
                fp.write(
                    IMPORT_SUB_MODEL_TEMPLATE % {"app": self.app.app_name, "sub_models_dir": self.sub_models})

    def send_create_signal(self):
        application_files_created_signal.send(sender=self.__class__, application=self.app)



    def create_template_files(self):

        """
        This method creates the project compliant template files to be used with views.
        @param app_name: Application name to be created
        @param appUrl:  The URL of the applciation
        @return:  True or False depending on the success
        """
        app_name = self.app.app_name
        appUrl = self.app.url

        logger.info('Creating template files for the new application')
        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_landing_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/landing.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating index2.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of index2.html failed: ' + str(e))

        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/application_app-template-file_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_app_template.html",
                 "w+").write(buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating app_template.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of app template file failed: ' + str(e))
        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/application_dashboard_navbar_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=appUrl)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_navbar.html",
                 "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating navbar.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of navbar.html failed: ' + str(e))
        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/application_dashboard_navbar_template2.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=appUrl)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_navbar2.html",
                 "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating navbar.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of navbar2.html failed: ' + str(e))

        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/application_dashboard_left_sidebar_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=appUrl)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_left_sidebar.html",
                 "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating navbar.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of left_sidebar.html failed: ' + str(e))

        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/application-wide_navbar_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=appUrl)
            t.render_context(c)

            open(
                self.site_root + "/" + app_name + "/templates/" + app_name + "/" + app_name + "_landing_page_navbar.html",
                "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating landing page navbar.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of landing_page_navbar failed: ' + str(e))

        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_new_page_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=appUrl)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/new_page_template.html",
                 "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating navbar.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of new_page_template.html failed: ' + str(e))
# -------------------------
        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_model_list_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name, models = self.app.models.all())
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/example"+app_name+"model_list.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating dashboard.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of dashboard.html failed: ' + str(e))

        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_model_form_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/example"+app_name+"appmodel_form.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating dashboard.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of dashboard.html failed: ' + str(e))

        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_model_delete_confirm_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/"+app_name+"_confirm_delete.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating dashboard.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of dashboard.html failed: ' + str(e))



        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_blank_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/blank.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating blank.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of blank.html failed: ' + str(e))




        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_crud_base_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/crudbase.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating blank.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of blank.html failed: ' + str(e))



        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_crud_list_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/crud_list.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating blank.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of blank.html failed: ' + str(e))




        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_crud_form_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/crud_form.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating blank.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of blank.html failed: ' + str(e))



        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_crud_delete_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/crud_delete.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating blank.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of blank.html failed: ' + str(e))





#-----------------------------

        try:
            t = Template(
                filename='applicationManager/templates/applicationManager/applicationFileTemplates/app_dashboard_html_template.txt')
            # t = loader.get_template('projectCore/applicationFileTemplates/app_index_html_template.txt')
            buf = StringIO()
            c = mako.runtime.Context(buf, applicationName=app_name)
            t.render_context(c)

            open(self.site_root + "/" + app_name + "/templates/" + app_name + "/dashboard.html", "w+").write(
                buf.getvalue())
        except Exception as e:
            logger.fatal("Exception occurred while creating dashboard.html file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(app_name=app_name))
            raise Exception('creation of dashboard.html failed: ' + str(e))
        return True

    def updateProjectUrlsPy(self):
        """
           This method created the Urls.py file for the entire project using a template file.
           Method reads application table and create the necessary file.
        """

        try:
            logger.info(
                "\n--------------------------------------------------------\n\t\tRefreshing application list in urls.py")
            copyfile(self.site_root + "/" + settings.APPLICATION_NAME + "/urls.py",
                     self.site_root + "/" + settings.APPLICATION_NAME + "/urls.py.backup")
            t = loader.get_template('applicationManager/applicationFileTemplates/project_urls_py.txt')

            apps = Application.objects.all()

            c = {'applist': apps}
            rendered = t.render(c)

            open(self.site_root + "/" + settings.APPLICATION_NAME + "/urls.py", "w+").write(rendered)
        except Exception as e:
            raise Exception('updateProjectUrlsPy failed: ' + str(e))

    # def updateProjectUrlsPy(self):
    #     """
    #         This method created the Urls.py file for the entire project using a template file.
    #
    #     """
    #     logger.info("\n--------------------------------------------------------------\n\t\t"
    #                 "Refreshing application list in urls.py")
    #     t = loader.get_template('applicationManager/applicationFileTemplates/project_urls_py.txt')
    #
    #     app_nameList = getAppNameListByAppsPy()
    #     print("Applications which will be created in database : " + str(app_nameList))
    #
    #     try:
    #         allapps = Application.objects.all()
    #         allapps.delete()
    #         print("deleted applications table content")
    #     except  Exception as e:
    #         print("Deletion of database entries for applications failed")
    #
    #     appConfigs = []
    #     for app_name in app_nameList:
    #         pass
    #         # Application config ile bu islemin yapilmasi durumu imkansiz: Cunku appconfig kullanmak icin
    #         # app custom_settings dosyasinda olmali ama bu durumda uygulama yeniden basladigi icin tum uygulama akisi
    #         # resetlenmektedir.
    #         # # confName = app_name+'AppConfig'
    #         # print(app_name)
    #         # appConf = apps.get_app_config(app_name)
    #         # appConfigs.append(appConf)
    #         # print(appConf)
    #         # # print(appConf.yvar)
    #
    #     c = Context({'applist': appConfigs})
    #     rendered = t.render(c)
    #
    #     # buf = StringIO()
    #     # c = mako.runtime.Context(buf, applist=appConfigs)
    #     # t.render_context(c)
    #
    #     open(self.site_root + "/" + custom_settings.APPLICATION_NAME + "/urls.py", "w+").write(rendered)

    # Updates only the custom_settings file
    def updateProjectSettingsPy(self):
        try:
            copyfile(self.site_root + "/" + settings.APPLICATION_NAME + "/custom_settings.py",
                     self.site_root + "/" + settings.APPLICATION_NAME + "/custom_settings.py." + str(
                         datetime.datetime.now().isoformat()))
            appList = Application.objects.all()
            print("List of applications to be added to the custom_settings file :" + str(appList))

            t = loader.get_template('applicationManager/applicationFileTemplates/project_settings_py.txt')
            c = {'appList': appList}
            rendered = t.render(c)
            open(self.site_root + "/" + settings.APPLICATION_NAME + "/custom_settings.py", "w+").write(rendered)
        except  Exception as e:

            logger.fatal("Exception occurred while updating project custom_settings file : %s", e)
            application_creation_failed_signal.send(sender=Application.__class__, test="testString",
                                                    application=Application.objects.get(
                                                        app_name=self.app.app_name))
            raise Exception('creation of project custom_settings.py failed: ' + str(e))

    def rollback(self):
        logger.error("Rolling back the installation")
        # os.rmdir(self.app.app_name)
        raise NotImplementedError
        pass

    def get_import(self, model):
        for dir in os.listdir(self.site_root):
            if os.path.isdir('{0}/{1}'.format(self.site_root, dir)) \
                    and os.path.exists('{0}/{1}/models.py'.format(self.site_root, dir)):
                with open('{0}/{1}/models.py'.format(self.site_root, dir), 'r') as fp:
                    # Check if model exists
                    for line in fp.readlines():
                        if 'class {0}(models.Model)'.format(model) in line:
                            # print "Foreign key '%s' was found in app %s..." % (model, dir)
                            return IMPORT_MODEL_TEMPLATE % {'app': dir, 'model': model}
        return None

    def is_imported(self, path, model):
        with open(path, 'r') as import_file:
            for line in import_file.readlines():
                if 'import {0}'.format(model) in line:
                    print("Foreign key '%s' was found in models.py..." % (model))
                    return True
        return False

    def is_declared(self, path, model):
        with open(path, 'r') as import_file:
            for line in import_file.readlines():
                if 'class {0}'.format(model.capitalize()) in line:
                    logger.info("Foreign key '%s' was found in models.py..." % (model))
                    return True
        return False

    def get_type_parameters(self, field):
        # parameter list is assumed comma seperated equity phrases
        params = field.type_parameter

        if params == "":
            return None
        else:
            # try:
            #     if isinstance(params,six.string_types):
            #
            #     else:
            #         print(params.__class__)
            # except ValueError as e:
            #     logger.fatal("Json document is not well formatted : "+params)

            pass

    def get_field(self, field):
        self.get_type_parameters(field)

        # Default vals
        field_name = field.name
        null_val = True
        blank_val = True
        lenght_val = "255"
        default_val = "255"
        digits_val = "3"
        places_val = "3"

        print(field)
        print(field.__class__)

        tp = field.type_parameter
        try:
            tp = tp.split(",")
        except:
            logger.warning("No comma seperated input")

        for param in tp:
            try:
                param_key, param_val = param.split(":")
            except:
                logger.error("parameter format is not correct")
                break

            if param_key.lower() == "null":
                null_val = param_val

            if param_key.lower() == "blank":
                blank_val = param_val

            if param_key.lower() == "length":
                lenght_val = param_val

            if param_key.lower() == "default":
                default_val = param_val

            if param_key.lower() == "digits":
                digits_val = param_val

            if param_key.lower() == "places":
                places_val = param_val

            if param_key.lower() == "foreign":
                foreign_val = param_val

        if field.type.lower() == 'char' or field.type.lower() == 'charfield':
            return CHARFIELD_TEMPLATE % {'name': field_name, 'length': lenght_val, 'null': null_val, 'blank': blank_val}

        elif field.type.lower() == 'text' or field.type.lower() == 'textfield':
            return TEXTFIELD_TEMPLATE % {'name': field_name, 'null': null_val}

        elif field.type.lower() == 'int' or field.type.lower() == 'integerfield':
            return INTEGERFIELD_TEMPLATE % {'name': field_name, 'null': null_val, 'default': default_val}

        elif field.type.lower() == 'decimal' or field.type.lower() == 'decimalfield':
            return DECIMALFIELD_TEMPLATE % {
                'name': field_name,
                'digits': digits_val,
                'places': places_val,
                'null': null_val,
                'default': default_val,
            }
        elif field.type.lower() == 'datetime' or field.type.lower() == 'datetimesssfield':

            return DATETIMEFIELD_TEMPLATE % {'name': field_name, 'null': null_val, 'default': default_val}

        elif field.type.lower() == 'foreign':
            foreign = foreign_val
            name = field_name
            # Check if this foreign key is already in models.py
            if foreign in ('User', 'Group'):
                if not self.is_imported('{0}/{1}/models.py'.format(self.site_root,
                                                                  self.app.app_name), foreign):
                    self.imports.append('\nfrom django.contrib.auth.models import User, Group\n')
                return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign, 'null': 'True'}

            if self.is_imported('{0}/{1}/models.py'.format(
                    self.site_root, self.app.app_name), foreign) or self.is_declared('{0}/{1}/models.py'.format(
                self.site_root, self.app.app_name), foreign):
                return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign, 'null': 'True'}

            # Check imports
            if self.get_import(foreign):
                self.imports.append(self.get_import(foreign))
                return FOREIGNFIELD_TEMPLATE % {'name': name, 'foreign': foreign, 'null': 'True'}

            logger.info('error\t{0}/{1}/models.py\t{2} class not found'.format(
                self.site_root, self.app.app_name, foreign), 1)
            return None

    def model_exists(self, model_id, file):

        mfile = open(file.format(self.site_root, self.app.app_name, self.sub_models), 'r')
        lines = mfile.readlines()
        mfile.close()

        model_name = (AppModel.objects.get(id=model_id)).name

        for line in lines:
            if 'class ' + model_name + '(models.Model):'.format(self.app.app_name, self.sub_models) in line:
                return True
        return False
