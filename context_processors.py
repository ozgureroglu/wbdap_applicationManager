from django.urls import resolve

from .models import Application
import logging

logger = logging.getLogger('applicationManager.context_processor')


def django_app_list_processor(request):
    """
    Returns the list of applications to navigation bars. It is assumed that the applications are all in
    the project root folder.

    :param request:
    :return:
    """
    applist = []
    try:
        apps = Application.objects.filter(active="1")
        for app in apps:
            # print(str(app))
            applist.append(app)
        return {'appList': sorted(applist, key=lambda x: x.app_name, reverse=False)}

    except Exception as e:
        logger.fatal(e)
        return {'appList': ''}


def django_active_app_list_processor(request):
    """
    Returns the list of applications which are set active
    :return:
    """
    applist = []
    try:
        for app in Application.objects.filter(active=True):
            applist.append(app.namedUrl)
            # print("\nActive Aplication List"+str(app.native))
        # print("\nActive Aplication List"+str(app.native))
        return {'activeAppList': sorted(applist)}
    except Exception as e:
        logger.fatal(e)
        return {'activeAppList': ''}


def django_current_app_name_processor(request):
    """
    Returns the name of the currently accessed application name to navigation bar.
    It is assumed that the applications are all in the project folder

    :param request:
    :return:
    """
    return {'current_app_name': resolve(request.path).app_name}


def django_current_app_processor(request):
    """
    Returns the name of the currently accessed application name to navigation bar.
    It is assumed that the applications are all in the project folder
    :param request:
    :return:
    """
    # print(resolve(request.path).view_name)
    # print(request.build_absolute_uri())
    # print(request.path.split("/")[1]+":index")
    return {'curApp_index': request.path.split("/")[1] + ":index"}


def get_current_app_type(request):
    """
    Returns the type of the current app
    :param request:
    :return:
    """
    app_name = resolve(request.path)._func_path
    app = (app_name.split("."))[0]

    try:
        app_obj = Application.objects.get(app_name=app)
        return {'is_core_app': app_obj.core_app}
    except Exception as e:
        return {'is_core_app': True}


def app_access_check(request):
    app_name = resolve(request.path).app_name
    if (request.user.has_perm(app_name+"_access")):
        return {'has_access': True}
    else:
        return {'has_access': False}

