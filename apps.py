from django.db import connection

__author__ = 'ozgur'

from django.core.management import call_command
from django.apps import AppConfig
import logging

logger = logging.getLogger("wbdap.debug")


class ApplicationManagerAppConfig(AppConfig):
    name = 'applicationManager'
    label = 'applicationManager'
    verbose_name = "applicationManager App"
    yvar = "yvar"

    appName = 'applicationManager'
    verbose_name = 'applicationManager'
    url = 'applicationManager'
    namedUrl = 'applicationManager'
    active = True
    description = "Readme file"


    ready_run = False


    @staticmethod
    def db_table_exists(prefix):
        for table_name in connection.introspection.table_names():
            if prefix in table_name:
                return True
        return False

    # Sadece bir kere uygulama baslatildiginda calistirilmakta
    #TODO: ready metodu icinde db islemleri onerilmiyor. Dolayisi ile asagaidaki kod icin bir alternatif gerekli, bak identitymanager
    def ready(self):
        import applicationManager.signals.signals
        import applicationManager.signals.handlers


        # if not self.ready_run:
        #     if not self.db_table_exists('applicationManager_'):
        #         try:
        #             call_command('migrate', 'applicationManager')
        #
        #         except:
        #             logger.fatal('unable to migrate applicationManager app ')
        #
        #     if self.db_table_exists('applicationManager_application'):
        #         # if there is no data in applicationManager_application table fill it
        #         cursor = connection.cursor()
        #         sql = """SELECT count(*) as tot FROM applicationManager_application"""
        #         cursor.execute(sql)
        #         data = cursor.fetchone()
        #         if data[0] == 0:
        #             call_command('loaddata', 'applicationManager/fixtures/initial_data.json')
        #
        # self.ready_run = True