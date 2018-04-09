import sys

from applicationManager.models import Application
from applicationManager.signals import application_creation_failed

__author__ = 'ozgur'

import logging
import tarfile
import datetime
import os
import shutil
from shutil import copyfile,rmtree
from django.conf import settings
from mako import runtime
from mako.template import Template
from django.template import loader, Context
from django.core.management import call_command
from io import StringIO

logger = logging.getLogger("wbdap.debug")


class DjangoApplicationRemover:

    def __init__(self, Application):
        self.application = Application

    def removeApp(self):
        app_name = self.application.app_name

        #remove database record
        self.remove_from_db(app_name)

        #UpdateSettings File
        self.updateSettingsFile(app_name)

        #Update Urls.py file
        self.update_urls_file(app_name)

        # self.targzApplicationFolder(app_name)

        #Remove folder
        self.removeFolders(app_name)


    def targzApplicationFolder(self,app_name):

        if not os.path.exists("AppArchive"):
            os.makedirs("AppArchive")

        output_filename = "AppArchive/"+app_name+"_"+str(datetime.datetime.now().isoformat())+".tar.gz"
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(app_name, arcname=os.path.basename(app_name))


    def removeFolders(self,app_name):
        print('removing folders')
        shutil.rmtree(app_name)

    def remove_from_db(self, app_name):
        app = Application.objects.get(app_name = app_name)
        app.delete()

    def update_urls_file(self, app_name):
        """
           This method created the Urls.py file for the entire project using a template file.
           Method reads application table and create the necessary file.
        """

        logger.info("\n--------------------------------------------------------\n\t\tRefreshing application list in urls.py")
        copyfile(settings.SITE_ROOT + "/" + settings.APPLICATION_NAME + "/urls.py", settings.SITE_ROOT + "/" + settings.APPLICATION_NAME + "/urls.py.backup")
        t = loader.get_template('applicationManager/applicationFileTemplates/project_urls_py.txt')

        apps = Application.objects.all()

        c = {'applist': apps}
        rendered = t.render(c)
        open(settings.SITE_ROOT + "/" + settings.APPLICATION_NAME + "/urls.py", "w+").write(rendered)


    def updateSettingsFile(self,app_name):
        try:
            copyfile(settings.SITE_ROOT + "/" + settings.APPLICATION_NAME + "/settings.py", settings.SITE_ROOT + "/" + settings.APPLICATION_NAME + "/settings.py."+str(datetime.datetime.now().isoformat()))
            appList = Application.objects.all()
            print("List of applications to be added to the settings file :" + str(appList))

            t = loader.get_template('applicationManager/applicationFileTemplates/project_settings_py.txt')
            c = {'appList': appList}
            rendered = t.render(c)
            open(settings.SITE_ROOT + "/" + settings.APPLICATION_NAME + "/settings.py", "w+").write(rendered)
        except  Exception as e:
            logger.fatal("Exception occurred while updating project settings file : %s", e)
            application_creation_failed.send(sender=Application.__class__, test="testString", application=Application.objects.get(app_name=self.application.app_name))
            print(sys.exc_info()[0])
            return False
        return True


