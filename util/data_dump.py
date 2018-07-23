import os
from django.core.management import call_command
import logging

logger = logging.getLogger(os.path.basename(__file__))


def dump_application_data(appname):
    try:
        call_command('dumpdata', appname, indent=2, output=appname + "/fixtures/initial_data.json")
    except Exception as e:
        logger.error(e)
        return False
    return True


def load_application_data(appname):
    try:
        call_command('loaddata', appname + "/fixtures/initial_data.json")
    except Exception as e:
        logger.error(e)
        return False
    return True


def dump_selected_application_data(apps):
    mess_list = []
    for app in apps:
        try:
            dump_application_data(app.app_name)
        except Exception as e:
            mess_list.append(str(e))
        if len(mess_list)!= 0:
            return mess_list
    return True



def migrate_db(appname):
    try:
        call_command('makemigrations', appname)
    except Exception as e:
        return e
    return True

