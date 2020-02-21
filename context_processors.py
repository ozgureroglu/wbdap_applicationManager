from django.urls import resolve

from .models import Application
import logging

logger = logging.getLogger('applicationManager.context_processor')


def django_app_list_processor(request):
    """
    Returns the list of application objects to navigation bars.
    :param request:
    :return:
    """
    applist = []
    try:
        apps = Application.objects.filter(active="1")
        for app in apps:
            applist.append(app)

    except Exception as e:
        logger.fatal(e)

    # Following sorted list takes app_name as key in the lambda expression
    return {'appList': sorted(applist, key=lambda x: x.app_name, reverse=False)}



def django_current_app_name_processor(request):
    """
    Returns the name of the currently accessed application name to navigation bar.
    It is assumed that the applications are all in the project folder

    :param request:
    :return:
    """
    return {'current_app_name': resolve(request.path).app_name}


# def django_current_app_processor(request):
#     """
#     Returns the name of the currently accessed application name to navigation bar.
#     It is assumed that the applications are all in the project folder
#     :param request:
#     :return:
#     """
#     # print(resolve(request.path).view_name)
#     # print(request.build_absolute_uri())
#     # print(request.path.split("/")[1]+":index")
#     return {'curApp_index': request.path.split("/")[1] + ":index"}

def get_app(request):
    app_name = resolve(request.path)._func_path
    app = (app_name.split("."))[0]
    if not app == 'django':
        return Application.objects.get(app_name = app)
    else:
        return None


def add_app_settings_processor(request):
    app = get_app(request)
    data={}
    if app == None:
        return {}
    if not app.settings_list.filter(app_id=app.id).count() == 0:

        for s in app.settings_list.filter(app_id=app.id):
            data[s.setting.name] = s.value
    print(data)
    return data


def get_current_app_type(request):
    """
    Returns the type of the current app :
    :param request:
    :return:
    """
    app_name = resolve(request.path)._func_path
    app = (app_name.split("."))[0]

    is_core_app = False
    try:
        app_obj = Application.objects.get(app_name=app)
        is_core_app = app_obj.core_app

    except Exception as e:
        logger.fatal(e)

    return {'is_core_app': is_core_app}


def get_current_app(request):
    """
    Returns the type of the current app :
    :param request:
    :return:
    """
    app_name = resolve(request.path)._func_path
    app = (app_name.split("."))[0]


    try:
        app_obj = Application.objects.get(app_name=app)
        return {'current_app': app_obj}

    except Exception as e:
        logger.fatal(e)
        return {'current_app': None}


def get_current_view_name(request):
    """
    Returns the name of the requested view of the current app :
    :param request:
    :return:
    """
    app_name = resolve(request.path).route
    view = (app_name.split("."))[len(app_name.split("."))-1]
    return {'view_name': view}


def get_current_view_path(request):
    """
    Returns the name of the requested view of the current app :
    :param request:
    :return:
    """
    if resolve(request.path).route == "":
        return {'view_path': ""}
    else:
        route = resolve(request.path).route
        path_nodes = str(route).split("/")
        # Remove the '' element from the array

        path_nodes.pop()
        return {'view_path': path_nodes.pop()}







# def app_access_check(request):
#     """
#     Better to do in middleware
#     :param request:
#     :return:
#     """
#     app_name = resolve(request.path).app_name
#     if (request.user.has_perm(app_name+"_access")):
#         return {'has_access': True}
#     else:
#         return {'has_access': False}
#
