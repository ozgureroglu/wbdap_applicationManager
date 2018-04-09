from wbdap import settings
from django.apps import apps
import os

__author__ = 'ozgur'


def getAppList():
    applist = []
    for appconf in apps.get_app_configs():

        if (settings.SITE_ROOT in appconf.path):
            print('\n')
            print(appconf.path)
            print(appconf.path.split('/')[-1])
            applist.append(apps.get_app_config(appconf.path.split('/')[-1]))
            # appCfg = apps.get_app_config(path.split('/')[-1])
            # print(appCfg.yvar)

    return applist




# Get the list of all applications by walking in the applications folder;
# Returns only the folders which have apps.py file in them
def getAppNameListByAppsPy():
    appNameList = []
    for file in os.listdir():
        if os.path.isdir(file):
            if not file.startswith('.') and not file.startswith('__'):
                if os.path.exists(file + '/apps.py'):
                    appNameList.append(file)
    return appNameList



def getssAppNameList():
    appNameList = []
    for appconf in apps.get_app_configs():
        # print(path)
        if (settings.SITE_ROOT in appconf.path):
            appNameList.append(appconf.path.split('/')[-1])

    applications = open(settings.SITE_ROOT + "/applications.txt", "w+")

    for item in appNameList:
        applications.write("%s\n" % item)
    return appNameList
