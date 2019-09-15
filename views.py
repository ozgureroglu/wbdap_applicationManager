import datetime
import subprocess
import sys
import logging
import uuid
import tarfile
import json
from distutils.errors import DistutilsError
from wsgiref.util import FileWrapper

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.template import Template, Context
from django.views.decorators.http import require_http_methods, require_POST
from formtools.wizard.views import SessionWizardView
from openpyxl.compat import file
from scrapy.signals import response_received

from applicationManager.util.api_utils import create_api
from wbdap import settings
from django.conf import settings
from .util.util_functions import *
from importlib import reload, import_module
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.urls import reverse_lazy, reverse, URLResolver
from django.http.response import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render, redirect
from django.urls.resolvers import RegexPattern, get_resolver, URLPattern
from django.views.generic import UpdateView, ListView, DetailView, CreateView
from django.views.generic.edit import DeleteView
from django.conf.urls import include, url
from applicationManager.forms import AddApplicationModelForm, CreateApplicationForm, CreateModelForm, CreateFieldForm, \
    UpdateFieldForm, ApplicationCreateForm1, ApplicationCreateForm2, ApplicationCreateForm3, ApplicationCreateForm4, \
    CreateProjectForm
from applicationManager.models import Application, AppModel, Field, ApplicationLayout, \
    ApplicationPage, ApplicationUrl, ApplicationSettings, ApplicationView, ApplicationComponentTemplate, DjangoProject

from applicationManager.util.data_dump import dump_selected_application_data, dump_application_data, \
    load_application_data
from applicationManager.util.django_application_creator import DjangoApplicationCreator

from applicationManager.signals.signals import application_created_signal, application_removed_signal, \
    soft_application_removed_signal, soft_application_created_signal, project_metadata_created_signal, \
    project_metadata_removed_signal
from django.db import transaction

logger = logging.getLogger("wbdap.debug")


@login_required
# @permission_required('applicationManager.has_access')
def landing_page(request):
    if (request.user.has_perm('applicationManager.has_access')):
        print('has access')
        return redirect("applicationManager:dashboard")

    else:
        return render(request, 'applicationManager/landing.html', {})


@login_required
def dashboard(request):
    if request.user.is_superuser:
        applications = Application.objects.all()
    else:
        if Application.objects.filter(owner_id=request.user.id):
            applications = Application.objects.get(owner_id=request.user.id)
        else:
            applications = None

    return render(request,
                  'applicationManager/dashboard.html', {'user': request.user, 'all_apps': applications}
                  )


@login_required
def applications(request):
    if request.user.is_superuser:
        applications = Application.objects.all()
    else:
        if Application.objects.filter(owner_id=request.user.id):
            applications = Application.objects.get(owner_id=request.user.id)
        else:
            applications = None

    return render(request,
                  'applicationManager/applications.html', {'user': request.user, 'all_apps': applications}
                  )


@login_required
def projects(request):
    if request.user.is_superuser:
        djangoProjects = DjangoProject.objects.all()


    return render(request,
                  'applicationManager/projects.html', {'user': request.user, 'all_projects': djangoProjects}
                  )





@login_required
def application_router(request, uuid, url_name):
    app = Application.objects.get(uuid=uuid)
    app_name = app.app_name
    reload(sys.modules[settings.ROOT_URLCONF])
    # return redirect('applicationManager:dashboard')
    return redirect("/" + app_name + '/')


@login_required
def dyn_view_loader(request, uuid, url_name=None):
    if url_name == None:
        url_name = 'index-page'

    # TODO: One option is to direct call of view by named url groups: Create urls as a parametric structure
    # But this method is more suitable for static pages:https://stackoverflow.com/questions/9439899/django-dynamic-urls

    dyn_view_code = ApplicationUrl.objects.get(url_name=url_name).view_method.view_code
    print(dyn_view_code)

    exec(dyn_view_code)
    app = Application.objects.get(uuid=uuid)
    app_name = app.app_name
    reload(sys.modules[settings.ROOT_URLCONF])
    # return redirect('applicationManager:dashboard')
    for x in sys.modules:
        if 'asd' in x:
            print(x)
    # after the following line a new req-res phase begins: so there should be new urlpath for the following requset
    # return redirect("/" + app_name + '/')
    return render(request, 'applicationManager/test.html', {})


def dyn_view_loader(request, uuid, url_path=None):
    print('printing url path: ' + url_path)
    if url_path == None:
        url_path = 'indexpage'

    # TODO: One option is to direct call of view by named url groups: Create urls as a parametric structure
    # But this method is more suitable for static pages:https://stackoverflow.com/questions/9439899/django-dynamic-urls

    # dyn_view_code = ApplicationUrl.objects.get(app__uuid=uuid,url_name=url_name).view_method.view_code
    # print(dyn_view_code)

    # exec(dyn_view_code)
    # app = Application.objects.get(uuid=uuid)
    # app_name = app.app_name
    # reload(sys.modules[settings.ROOT_URLCONF])
    # return redirect('applicationManager:dashboard')
    # for x in sys.modules:
    #     if 'asd' in x:
    #         print(x)
    # after the following line a new req-res phase begins: so there should be new urlpath for the following requset
    # return redirect("/" + app_name + '/')
    # TODO: asagidakiler normal uygulamalardaki gibi yapilabilmeli
    try:
        view = ApplicationUrl.objects.get(app__uuid=uuid, url_pattern=url_path).view_method
    except Exception as e:
        messages.add_message(request, messages.ERROR, str(e))
        return redirect(reverse('applicationManager:dashboard'))

    print(view.view_code)
    print(view.__class__)
    exec(view.view_code)
    temp = None
    try:
        temp = ApplicationComponentTemplate.objects.get(id=view.template_id)
        return render(request, temp.temp_name + '__' + temp.temp_type, {})

    except ObjectDoesNotExist as e:
        print(e.__class__.__name__)
        messages.add_message(request, messages.ERROR, 'Template field not set for view')
        return redirect(reverse('applicationManager:dashboard'))


def genuuid_all(request):
    for app in Application.objects.all():
        app.uuid = uuid.uuid4()
        app.save()
        pass
    return redirect('applicationManager:dashboard')


def genuuid_app(request, id):
    app = Application.objects.get(id=id)
    app.uuid = uuid.uuid4()
    app.save()
    return redirect('applicationManager:dashboard')


def countdown_test_page(request):
    return render(request,
                  'applicationManager/applicationFileTemplates/metronic/metronic/index.html', {}
                  # 'applicationManager/index_page.html', {'user': request.user}, extraContext
                  )


@login_required
# Creates an application
def createApplication(request):
    if request.method == "POST":

        # We are creating the bound form
        form = CreateApplicationForm(request.POST)

        if form.is_valid():
            logger.info("Form is valid")
            application = form.save(commit=False)
            application.active = False
            application.owner = request.user
            application.uuid = uuid.uuid4()
            application.save()

            #
            # if res:
            #     messages.add_message(request, messages.INFO, 'Created Application ' + application.app_name)
            # else:
            #     messages.add_message(request, messages.ERROR, 'Application creation failed')
            try:
                # Send the application created signal; first parameter is the sender,
                # second one is a generic parameter, third one is the applications itself.
                application_created_signal.send(sender=Application.__class__, test="testString",
                                                application=Application.objects.get(app_name=application.app_name))
            except Exception as e:
                print(e)

            return redirect('applicationManager:dashboard')
            # return HttpResponse(status=200)
        else:
            logger.warning('Form is not valid')
            return HttpResponse(status=400)
    else:

        form = CreateApplicationForm()
        variables = {'form': form}
        return render(
            request,
            # 'applicationManager/createApplicationForm.html',
            'applicationManager/createApplication.html',
            variables
        )



@login_required
# Creates an application
def createProject(request):
    if request.method == "POST":

        # We are creating the bound form
        form = CreateProjectForm(request.POST)

        if form.is_valid():
            logger.info("Form is valid")
            project = form.save(commit=False)
            project.status = False

            project.save()
            try:
                # Send the application created signal; first parameter is the sender,
                # second one is a generic parameter, third one is the applications itself.
              project_metadata_created_signal.send(sender=Application.__class__, test="testString",
                                                project=DjangoProject.objects.get(app_name=project.name))
            except Exception as e:
                print(e)

            return redirect('applicationManager:projects')
            # return HttpResponse(status=200)
        else:
            logger.warning('Form is not valid')
            return HttpResponse(status=400)
    else:

        form = CreateProjectForm()
        variables = {'form': form}
        return render(
            request,
            # 'applicationManager/createApplicationForm.html',
            'applicationManager/createProject.html',
            variables
        )



@login_required
# Creates an application
def createApplication2(request):
    if request.method == "POST":

        # We are creating the bound form
        form = CreateApplicationForm(request.POST)

        if form.is_valid():
            logger.info("Form is valid")
            application = form.save(commit=False)
            application.active = False
            application.owner = request.user
            application.uuid = uuid.uuid4()
            application.save()

            #
            # if res:
            #     messages.add_message(request, messages.INFO, 'Created Application ' + application.app_name)
            # else:
            #     messages.add_message(request, messages.ERROR, 'Application creation failed')
            try:
                # Send the application created signal; first parameter is the sender,
                # second one is a generic parameter, third one is the applications itself.
                application_created_signal.send(sender=Application.__class__, test="testString",
                                                application=Application.objects.get(app_name=application.app_name))
            except Exception as e:
                print(e)

            return redirect('applicationManager:dashboard')
            # return HttpResponse(status=200)
        else:
            logger.warning('Form is not valid')
            return HttpResponse(status=400)
    else:

        form = CreateApplicationForm()
        variables = {'form': form}
        return render(
            request,
            'applicationManager/createApplication.html',
            variables
        )


@login_required
def delete_application(request, id):
    app = Application.objects.get(id=id)
    logger.info('Deleting application %s', app.app_name)

    if app.soft_app == True:
        try:
            app.delete()
        except Exception as e:
            logger.fatal('An exception occured while deleting application : %s', e)
            return False

        soft_application_removed_signal.send(sender=Application.__class__, test="testString",
                                             application=app)
    else:
        try:
            app.delete()
        except Exception as e:
            logger.fatal('An exception occured while deleting application : %s', e)
            return False

        application_removed_signal.send(sender=Application.__class__, test="testString",
                                        application=Application.objects.get(app_name=app.app_name))

    return redirect('applicationManager:applications')


@login_required
def application_details(request, appid):
    app = Application.objects.get(id=appid)
    return redirect('applicationManager:app')


@login_required
def generate_data(request, appid):
    pass
    return redirect('applicationManager:applications')


@login_required
def dump_all_data(request):
    apps = Application.objects.all()
    res = dump_selected_application_data(apps)
    if not res:
        for mess in res:
            messages.add_message(request, messages.WARNING, mess)

    return redirect('applicationManager:applications')


@login_required
def load_data(request, id):
    """
    Loads the fixtures of the application given by the id
    :param request:
    :param id: id of the application
    :return:
    """
    app = Application.objects.get(id=id)
    if load_application_data(app.app_name):
        messages.add_message(request, messages.INFO,
                             "Data of application " + app.app_name + " has been loaded into database.")
    else:
        messages.add_message(request, messages.WARNING,
                             "Load of application data (" + app.app_name + ") has failed.")
    return redirect('applicationManager:applications')


@login_required
def dump_app_data(request, id):
    """
    dumps only the data of the selected application
    :param request:
    :param id: id of the application
    :return:
    """
    app = Application.objects.get(id=id)
    if dump_application_data(app.app_name):
        messages.add_message(request, messages.INFO,
                             "Data of application " + app.app_name + " has been dumped into fixture file.")
    else:
        messages.add_message(request, messages.WARNING,
                             "Dumping of application data(" + app.app_name + ") has been failed")
    return redirect('applicationManager:applications')


#
# def updateProjectUrlsFile(request):
#
#     logger.info('Updating project url file for the new application')
#
#     appName = request.POST['appName'];
#     try:
#         t = Template(filename='applicationManager/applicationFileTemplates/project_urls_py.txt')
#
#         t.get_def("automatedURL").render(applicationName='test');
#
#         newURL = "url(r'^" + appName + "/', include('" + appName + ".urls', app_name='" + appName + "', namespace='" + appName + "')),"
#
#         print(newURL)
#         buf = StringIO()
#         c = mako.runtime.Context(buf, newURL=newURL)
#         t.render_context(c)
#         print(buf.getvalue())
#         open(settings.SITE_ROOT + "/" + settings.APPLICATION_NAME + "/urls.py", "w+").write(buf.getvalue())
#
#     except Exception as e:
#         print(e)
#         return 0
#
#     return 1
#

@login_required
def create_file(request, id):
    return render(request,
                  'applicationManager/create_file.html'
                  )


@login_required
def application_activate(request, id):
    app = Application.objects.get(id=id)
    if app.active:
        app.active = False

    else:
        app.active = True
        # install_app(app)
        # from django.template.loaders.app_directories import get_app_template_dirs
        # from django.template.loaders.app_directories import Loader
        # from django.template import Engine
        #
        # loader = Loader(Engine.get_default())
        # loader.load_template_source(template_dirs='templates')
        # # print(get_app_template_dirs('templates'))

    app.save()
    return redirect('applicationManager:applications')


def get_installed_apps_names():
    ins_apps = []
    confs = apps.get_app_configs()
    for conf in confs:
        ins_apps.append(conf.name)

    return ins_apps


def add_to_installed_apps(appname):
    applist = get_installed_apps_names()
    applist.append(appname)
    return applist


def install_app(app):
    if not app.app_name in get_installed_apps_names():
        apps.set_installed_apps(installed=add_to_installed_apps(app.app_name))
        # print(apps.app_configs)

        # for application in apps.app_configs:

        try:
            mod = import_module('%s.urls' % app.app_name)
            # possibly cleanup the after the imported module?
            #  might fuss up the `include(...)` or leave a polluted namespace
        except:
            # cleanup after module import if fails,
            #  maybe you can let the `include(...)` report failures
            pass
        else:
            # add the urls.py of the app to urlpatterns
            urls = URLResolver(RegexPattern(r'^/'), settings.ROOT_URLCONF)
            urlpatterns = urls.url_patterns

            urlpatterns.append(url(r'^%s/' % app.app_name, include('%s.urls' % app.app_name)))
            # print(urlpatterns)

            # app_dir = os.path.join(settings.SITE_ROOT+'/'+app.app_name)

            reload_urlconf()
            # print(sys.modules)

            for x in apps.get_app_configs():
                print(x.name)
                print(x.path)
                print("\n")

            # Burada 1. ve kaba yontem dogrudan settings.TEMPLATES altina eklemektir, ikinci yontem ise
            # bir loader kullanarak yapmaktir.

            # print(settings.TEMPLATES[0].__class__)
            # print(settings.TEMPLATES[0])
            #
            # app_dir = os.path.join(settings.SITE_ROOT + '/' + app.app_name)
            # app_conf = apps.get_app_config(app.app_name)
            # DIRS = settings.TEMPLATES[0]['DIRS']
            # if app_conf.path not in DIRS:
            #     DIRS.append(app_conf.path)
            #
            # settings.TEMPLATES[0]['DIRS'] = DIRS

            from django.template.loaders.app_directories import Loader
            from django.template import Engine
            Loader(Engine.get_default()).get_contents()

            # Django uses get_template to find the template and it takes the requested template name and an optional folder name
            # print(Loader(Engine.get_default()).get_template())

            #
    # if app.app_name in settings.INSTALLED_APPS:
    #     logger.info("Not installing app")
    #     pass
    # else:
    #     logger.info("installing app")
    #     settings.INSTALLED_APPS += (app.app_name,)
    #     print(settings.INSTALLED_APPS)
    #     apps.app_configs = OrderedDict()
    #     apps.ready = False
    #     apps.populate(settings.INSTALLED_APPS)
    #
    #
    #     # now I can generate the migrations for the new app
    #     management.call_command('makemigrations', app.app_name, interactive=False)
    #     # and migrate it
    #     management.call_command('migrate', app.app_name, interactive=False)
    #
    #
    #
    #     try:
    #         mod = import_module('%s.urls' % app)
    #         # possibly cleanup the after the imported module?
    #         #  might fuss up the `include(...)` or leave a polluted namespace
    #     except:
    #         # cleanup after module import if fails,
    #         #  maybe you can let the `include(...)` report failures
    #         pass
    #     else:
    #         urls = urlresolvers.get_resolver()
    #         urlpatterns = urls.url_patterns
    #
    #         urlpatterns.append(url(r'^%s/' % app.app_name, include('%s.urls' % app)))
    #         print(urlpatterns.__class__)
    #
    #         app_dir = os.path.join(settings.SITE_ROOT+'/'+app.app_name)
    #
    #         reload_urlconf()
    #         print(app_dir)
    #
    #
    #         # loader = Loader(dirs=app_dir)
    #         # print(loader.get_dirs())
    #
    #
    #         # print(urlpatterns)
    #     #
    #     #
    #
    #     # show_urls()
    #
    #     #
    #     # for application in settings.INSTALLED_APPS:
    #     #
    #     #     try:
    #     #         mod = import_module('%s.urls' % app)
    #     #         # possibly cleanup the after the imported module?
    #     #         #  might fuss up the `include(...)` or leave a polluted namespace
    #     #     except:
    #     #         # cleanup after module import if fails,
    #     #         #  maybe you can let the `include(...)` report failures
    #     #         pass
    #     #     else:
    #     #         # add the urls.py of the app to urlpatterns
    #     #         urlpatterns += patterns('',
    #     #             url(r'^%s/' % slugify(app), include('%s.urls' % app)
    #     #         )
    #     #
    #


def reload_urlconf(urlconf=None):
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])


def collect_urls(urls=None, namespace=None, prefix=None):
    if urls is None:
        urls = get_resolver()
    _collected = []
    prefix = prefix or []
    for x in urls.url_patterns:
        if isinstance(x, RegexPattern):
            _collected += collect_urls(x, namespace=x.namespace or namespace,
                                       prefix=prefix + [x.regex.pattern])
        elif isinstance(x, RegexPattern):
            _collected.append({'namespace': namespace or '',
                               'name': x.name or '',
                               'pattern': prefix + [x.regex.pattern],
                               'lookup_str': x.lookup_str,
                               'default_args': dict(x.default_args)})
        else:
            raise NotImplementedError(repr(x))
    return _collected


def show_urls():
    all_urls = collect_urls()
    all_urls.sort(key=lambda x: (x['namespace'], x['name']))

    for u in all_urls:
        print(u)

    # print(all_urls)
    # max_lengths = {}
    # for u in all_urls:
    #     for k in ['pattern', 'default_args']:
    #         u[k] = str(u[k])
    #     for k, v in list(u.items())[:-1]:
    #         # Skip app_list due to length (contains all app names)
    #         if (u['namespace'], u['name'], k) == \
    #                 ('admin', 'app_list', 'pattern'):
    #             continue
    #         max_lengths[k] = max(len(v), max_lengths.get(k, 0))
    #
    # for u in all_urls:
    #     sys.stdout.write(' | '.join(('{:%d}' % max_lengths.get(k, len(v))).format(v) for k, v in u.items()) + '\n')


@login_required
def redirect_to_app(request, uuid):
    app = Application.objects.get(uuid=uuid)
    app_name = app.app_name
    logger.info('will redirect to app : ' + app_name)
    reload(sys.modules[settings.ROOT_URLCONF])
    # return redirect('applicationManager:applications')
    return redirect("/" + app_name + '/')


def reload_urlconf(urlconf=None):
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])

    return redirect('applicationManager:applications')


def getAppNameListByAppsPy():
    # def test(request):
    appNameList = []
    for file in os.listdir():
        if os.path.isdir(file):
            if not file.startswith('.') and not file.startswith('__'):
                if os.path.exists(file + '/apps.py'):
                    appNameList.append(file)

    return HttpResponse(status='200')


# Serialize all apllication data to a json file for using as DBbackup
def serializeConfs(request):
    apps = Application.objects.all()
    with open("applications.json", "w") as out:
        data = serializers.serialize("json", apps, stream=out)

    return HttpResponseRedirect("/applicationManager/")


# Serialize all apllication data to a json file for using as DBbackup
def deserializeConfs(request):
    apps = Application.objects.all()
    with open("applications.json", "w") as out:
        data = serializers.serialize("json", apps, stream=out)

    return HttpResponse('')


def reindexApps(request):
    pass
    # if request.method == "GET":
    #     print('Get request')
    #     data = {'appList': Application.objects.all()}
    #
    #     return render(request, 'applicationManager/reindexApps.html', data)
    #
    # elif request.method == "POST":
    #     print('Post request')
    #
    #     updateProjectUrlsPy()
    #
    #     data = {'appList': Application.objects.all()}
    #     variables = RequestContext(request, data);
    #     return render_to_response('applicationManager/reindexApps.html', variables)


def cleanAppsTable():
    try:
        appsDbData = Application.objects.all()
        appsDbData.delete()
        return True
    except:
        return False


def updateAppsDBWoAppConfig():
    logger.info('Updating Application DB table ...')
    if cleanAppsTable():
        appNameList = getAppNameListByAppsPy()

        moduleNames = []
        # Lets load all apps AppConfig class and read the applications specific info from there
        for appName in appNameList:
            appsModule = __import__(appName + '.apps', globals(), locals(), fromlist=(appName + '.apps'), level=0)
            # print(appConfig.yvar)

            appConf = getattr(appsModule, appName[0].upper() + appName[1:] + 'AppConfig')

            app = Application()
            app.appName = appConf.appName
            app.verbose_name = appConf.verbose_name
            app.namedUrl = appConf.namedUrl
            app.description = appConf.readmeContent
            app.url = appConf.url
            app.active = appConf.active
            app.owner = User.objects.get(username='ozgur')

            app.save()


def updateAppsDB(request):
    appNameList = getAppNameListByAppsPy()

    appsDbData = Application.objects.all()
    appsDbData.delete()

    for appName in appNameList:
        appConf = apps.get_app_config(appName)
        app = Application()
        app.appName = appConf.appName
        app.verbose_name = appConf.verbose_name
        app.namedUrl = appConf.namedUrl
        app.description = appConf.readmeContent
        app.url = appConf.url
        app.active = appConf.active
        app.owner_id = 1
        app.core_app = 1
        app.save()


@require_POST
def trigger(request, id):
    setting_id = request.POST['setting_id']
    obj, created = ApplicationSettings.objects.get_or_create(app_id=id, setting_id=setting_id, defaults={}, )
    obj.toogle_setting()

    # Application.objects.get(id = id).applicationsettings.toogle_setting(request.POST['type'])
    # create_api('testapp')
    return JsonResponse({}, safe=False)


@login_required
def get_application_models(request, id):
    app = Application.objects.get(id=id)
    appConfig = apps.get_app_config(app.appName)
    return render(request, 'applicationManager/app_module_list.html', {'models': appConfig.models})


@login_required
def application_management_page(request, id):
    if request.POST:
        logger.info('received post')

    app = Application.objects.get(id=id)

    app_config = apps.get_app_config(app.app_name)
    models = app_config.get_models()
    pages = ApplicationPage.objects.filter(app_id=id)

    # Here the term model denotes the native models of django not the AppModel of applicationManager application
    # for m in models:
    #     print(m.__name__)
    #

    # model_form.helper.form_action = reverse("applicationManager:model-create", kwargs={'id': id})

    return render(request, 'applicationManager/application_management_page.html',
                  {'app_form': CreateApplicationForm,
                   'app': Application.objects.get(id=id),
                   'models': models,
                   'pages': pages,
                   'appsettings': ApplicationSettings.objects.filter(app_id=id)
                   })



@login_required
def project_management_page(request, id):
    if request.POST:
        logger.info('received post')

    prj = DjangoProject.objects.get(id=id)


    # models = app_config.get_models()
    # pages = ApplicationPage.objects.filter(app_id=id)

    # Here the term model denotes the native models of django not the AppModel of applicationManager application
    # for m in models:
    #     print(m.__name__)
    #

    # model_form.helper.form_action = reverse("applicationManager:model-create", kwargs={'id': id})

    return render(request, 'applicationManager/project_management_page.html',
                  {'app_form': CreateApplicationForm,
                   'app': prj,
                   # 'models': models,
                   # 'pages': pages,
                   # 'appsettings': ApplicationSettings.objects.filter(app_id=id)
                   })


class AppModelListView(ListView):
    model = AppModel
    http_method_names = ['get']

    # TODO: This is not a suitable way of returning json for listview: because it is redefining the response of view,
    # instead it should modify the exsiting response
    # Listview tarafindan json response donmesi icin assagidaki method override ediliyor.
    def render_to_response(self, context, **response_kwargs):
        print(self.kwargs)
        app_conf = apps.get_app_config(Application.objects.get(id=self.kwargs['id']).app_name)
        models = app_conf.get_models()
        data = {}
        model_list = []
        for model in models:
            print(model.__name__)
            model_list.append(model.__name__)

            # fields = model._meta.get_fields()
            # for f in fields:
            #     print(f.name)
            #     print(f.get_internal_type())
        data['models'] = model_list

        # queryset = self.model.objects.all()
        # data = list(models)
        # print(data)
        # data = serializers.serialize('json', model_list )
        # data = json.dumps(list(models))

        # returning httpresponse instead of jsonresponse to avoid double encoding
        # return HttpResponse(json.dumps(data), content_type='application/json')
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super(AppModelListView, self).get_context_data(**kwargs)
        # If extra contex parameters are required
        # context['now'] = timezone.now()
        return context


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    https://docs.djangoproject.com/en/2.0/topics/class-based-views/mixins/#jsonresponsemixin-example
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        Of course if context is
        """
        return HttpResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """

        # Just serializing single object to json
        context = serializers.serialize('json', [context['object']], ensure_ascii=False)
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context


class AppModelDetailView(JSONResponseMixin, DetailView):
    model = AppModel
    http_method_names = ['get']

    # Override render_to_response with the JSONResponseMixin's render_to_json_response using the same method signature

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    # If you want to change the context
    def get_context_data(self, **kwargs):
        context = super(AppModelDetailView, self).get_context_data(**kwargs)
        # If extra contex parameters are required
        # context['now'] = timezone.now()
        return context


@login_required
class ApplicationUpdate(UpdateView):
    model = Application
    form_class = CreateApplicationForm

    success_url = reverse_lazy('applicationManager:applications')
    template_name_suffix = '_update_form'

    #
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super(ApplicationUpdate, self).get_context_data(**kwargs)
    #     # Add in a QuerySet of all the books
    #     context['models'] = get_application_models()
    #     return context

    #
    # def form_valid(self, form):
    #     print(form['active'].value())
    #
    #     t = loader.get_template('applicationManager/applicationFileTemplates/apps.py.txt')
    #     c = {'appName': form['appName'].value(), 'verbose_name': form['verbose_name'].value(), 'url': form['url'].value(), 'namedUrl': form['namedUrl'].value(), 'active': form['active'].value(),
    #                  'readmeContent': form['readmeContent'].value()}
    #     rendered = t.render(c)
    #     print(rendered)
    #     open(settings.SITE_ROOT + "/" + form['appName'].value() + "/apps.py", "w+").write(rendered)
    #
    #     self.object = form.save()
    #     return super(ModelFormMixin, self).form_valid(form)

    # def post(self, request, *args, **kwargs):
    #     logger.info('Will serialize the settings into the apps.py')
    #
    #     self.object = self.get_object()
    #     return super(BaseUpdateView, self).post(request, *args, **kwargs)


# def model_list(request,id):
#     pass
#
#
# def model_details(request,id,model_id):
#     pass
#
#
# def model_delete(request,id,model_id):
#     pass
#
#
#
# def model_field_list(request,id):
#     pass
#
#
# def model_field_details(request,id,model_id,field_id):
#     pass
#
#
# def model_field_delete(request,id,model_id,field_id):
#     pass


class FieldListView(JSONResponseMixin, ListView):
    model = Field
    http_method_names = ['get']

    def render_to_response(self, context, **response_kwargs):
        queryset = self.model.objects.all()
        data = serializers.serialize('json', queryset)
        return HttpResponse(data, content_type='application/json')

    # Bu metodu override etme sebebi donecek olan object listesini degistirmek ve
    # sadece modele ait olanlari donmek
    def get_queryset(self):
        queryset = super(FieldListView, self).get_queryset()
        # batchelors degrees only
        queryset = queryset.filter(owner_model_id=self.kwargs['model_id'])
        # filter by state
        # queryset = queryset.filter(school__city__state__slug=self.kwargs['state_slug'])
        return queryset

    # Asagidaki metodu override etme sebebi template icinde gerekli olan bazi parameterelleri contexte eklemek
    def get_context_data(self, **kwargs):
        context = super(FieldListView, self).get_context_data(**kwargs)
        model = AppModel.objects.get(id=self.kwargs['model_id'])
        context['model'] = model
        return context


class ModelCreateView(CreateView):
    model = AppModel
    form_class = CreateModelForm

    # fields = ['modelName','app']
    # success_url = reverse_lazy('applicationManager:application-management-page',args={'id':})
    # def get_form_kwargs(self):
    #     kwargs = self.form_class.helper.
    #     # return super(ModelCreateView, self).get_form_kwargs()

    def get_form(self, form_class=form_class):
        form = super(ModelCreateView, self).get_form(form_class)
        # print(form.fields['app'].initial)
        form.fields['app'].initial = self.kwargs['id']
        from django.forms.widgets import HiddenInput
        form.fields['app'].widget = HiddenInput()
        form.helper.form_action = reverse('applicationManager:model-create', kwargs={'id': self.kwargs['id']})

        return form

    def get_success_url(self):
        # Asagidaki bize path donmeli ve bu path icinde id yerine self.kwargs degerini kullaniyor olmali
        self.success_url = reverse('applicationManager:application-management-page', kwargs={'id': self.kwargs['id']})
        # print(self.success_url)
        return super(ModelCreateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ModelCreateView, self).get_context_data(**kwargs)
        context['model_form'] = self.get_form()
        return context


class FieldCreateView(CreateView):
    model = Field
    form_class = CreateFieldForm

    def get_success_url(self):
        # Asagidaki bize path donmeli ve bu path icinde id yerine self.kwargs degerini kullaniyor olmali
        self.success_url = reverse('applicationManager:application-management-page',
                                   kwargs={'id': self.kwargs['app_id']})
        print(self.success_url)
        return super(FieldCreateView, self).get_success_url()

    def get_form(self, form_class=CreateFieldForm):
        form = super(FieldCreateView, self).get_form(form_class)
        print(form.helper.form_action)

        # form.helper.form_action = "new_Action"
        form.helper.form_action = reverse('applicationManager:field-create',
                                          kwargs={'app_id': self.kwargs['app_id'], 'model_id': self.kwargs['model_id']})

        return form

    # def get_success_url(self):
    #     # Asagidaki bize path donmeli ve bu path icinde id yerine self.kwargs degerini kullaniyor olmali
    #     self.success_url = reverse('applicationManager:application-management-page',kwargs={'app_id': self.kwargs['app_id'], 'model_id': self.kwargs['model_id']})
    #     print('success url '+self.success_url)
    #     # print(self.success_url)
    #     return super(FieldCreateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        print('a')
        # Call the base implementation first to get a context
        context = super(FieldCreateView, self).get_context_data(**kwargs)
        # Burada yeni bir form uretim contextte onu dondugumuz icin yukarida overrride edilen formu gormuyoruz. dolayaisi
        # ile eger degistirilmis formu kullanamak istiyorsak, ya burada onu donmenin bir yolunu bulacagiz ya da burada donen
        # formu modifiye edecegiz ya da mevcut formun template icinde field_form ismi ile erisilebilmesini saglayacagiz.
        # context['field_form'] = CreateFieldForm
        if 'field_form' not in context:
            context['field_form'] = self.get_form()
        return context


class FieldDetailView(JSONResponseMixin, DetailView):
    model = Field
    http_method_names = ['get']

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(FieldDetailView, self).get_context_data(**kwargs)
        # If extra contex parameters are required
        # context['now'] = timezone.now()
        return context


class ModelUpdate(UpdateView):
    model = AppModel
    fields = ['name']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        # Asagidaki bize path donmeli ve bu path icinde id yerine self.kwargs degerini kullaniyor olmali
        self.success_url = reverse('applicationManager:application-management-page', kwargs={'id': self.kwargs['id']})
        return super(ModelUpdate, self).get_success_url()


class FieldUpdateView(UpdateView):
    model = Field
    form_class = UpdateFieldForm

    # fields = ['name', 'type', 'type_parameter']
    # template_name_suffix = '_update_form'

    def get_success_url(self):
        # Asagidaki bize path donmeli ve bu path icinde id yerine self.kwargs degerini kullaniyor olmali
        self.success_url = reverse('applicationManager:application-management-page',
                                   kwargs={'id': self.kwargs['app_id']})
        return super(FieldUpdateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        print('a')
        # Call the base implementation first to get a context
        context = super(FieldUpdateView, self).get_context_data(**kwargs)
        # Burada yeni bir form uretim contextte onu dondugumuz icin yukarida overrride edilen formu gormuyoruz. dolayaisi
        # ile eger degistirilmis formu kullanamak istiyorsak, ya burada onu donmenin bir yolunu bulacagiz ya da burada donen
        # formu modifiye edecegiz ya da mevcut formun template icinde field_form ismi ile erisilebilmesini saglayacagiz.
        # context['field_form'] = CreateFieldForm
        if 'field_form' not in context:
            context['field_form'] = self.get_form()
        return context


class ModelDelete(DeleteView):
    model = AppModel

    # success_url = reverse_lazy('applicationManager:model-list')

    def get_success_url(self):
        print(self.kwargs['id'])
        # Asagidaki bize path donmeli ve bu path icinde id yerine self.kwargs degerini kullaniyor olmali
        self.success_url = reverse('applicationManager:application-management-page', kwargs={'id': self.kwargs['id']})
        print(self.success_url)
        return super(ModelDelete, self).get_success_url()


class FieldDeleteView(DeleteView):
    '''Delete the given field'''
    model = Field

    def get_success_url(self):
        # Asagidaki bize path donmeli ve bu path icinde id yerine self.kwargs degerini kullaniyor olmali
        # self.success_url = reverse('applicationManager:field-list',
        #                            kwargs={'app_id': self.kwargs['app_id'], 'model_id': self.kwargs['model_id']})

        self.success_url = reverse('applicationManager:application-management-page',
                                   kwargs={'id': self.kwargs['app_id']})
        print(self.success_url)
        return super(FieldDeleteView, self).get_success_url()


def add_application_model(request, pk):
    if request.method == "GET":
        form = AddApplicationModelForm()
    elif request.method == "POST":
        pass
    else:
        pass

    return render(request,
                  'applicationManager/application_modelManagement_form.html', {'user': request.user, 'form': form}
                  # 'applicationManager/index_page.html', {'user': request.user}, extraContext
                  )


@login_required
def download_app(request, id):
    app = Application.objects.get(id=id)

    clean_folder(os.path.join(settings.SITE_ROOT, app.app_name))

    response = HttpResponse(content_type='application/x-gzip')  # mimetype is replaced by content_type for django 1.7
    response['Content-Disposition'] = 'attachment; filename=%s' % app.app_name + ".tar.gz"

    tar = tarfile.open(fileobj=response, mode="w:gz")
    tar.add(os.path.join(settings.SITE_ROOT, app.app_name),
            arcname=os.path.basename(os.path.join(settings.SITE_ROOT, app.app_name)))
    tar.close()
    return response


@login_required
def package_app(request, id):
    app = Application.objects.get(id=id)
    version = '0.1'
    dest = os.path.join(settings.FILESYSTEM_DIR, "wbdap_" + app.app_name)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    # os.mkdir(dest, mode=0o755)

    from shutil import copytree
    source = os.path.join(settings.PROJECT_PATH, app.app_name)
    copytree(source, dest)

    template_dir = os.path.join(settings.PROJECT_PATH,
                                "applicationManager/templates/applicationManager/applicationFileTemplates")

    # Create README.rst
    readme = open(os.path.join(dest, "README.rst"), "w+")
    readme_temp_file = open(os.path.join(template_dir, "readme.rst.tmp"), "r")
    readme_temp_content = readme_temp_file.read()
    readme_temp_file.close()
    readme_temp_obj = Template(readme_temp_content)

    context = Context({'applicationName': app.app_name, 'applicationDescription': app.description})
    rendered_temp = readme_temp_obj.render(context)
    readme.write(rendered_temp)
    readme.close()

    # Create license file

    lic = open(os.path.join(dest, "LICENSE"), "w+")
    lic_temp_file = open(os.path.join(template_dir, "BSD_Lic.txt.tmp"), "r")
    lic_temp_content = lic_temp_file.read()
    lic_temp_file.close()
    lic_temp_obj = Template(lic_temp_content)

    import django

    context = Context({'year': datetime.datetime.now().year,
                       'copyright_holder': settings.COMPANY_NAME,
                       'django_version': django.VERSION,
                       'version': version})
    rendered_temp = lic_temp_obj.render(context)
    lic.write(rendered_temp)
    lic.close()

    # Create setup.py

    setup = open(os.path.join(dest, "setup.py"), "w+")
    setup_temp_file = open(os.path.join(template_dir, "setup.py.tmp"), "r")
    setup_temp_content = setup_temp_file.read()
    setup_temp_file.close()
    setup_temp_obj = Template(setup_temp_content)

    context = Context({'applicationName': app.app_name,
                       'applicationDescription': app.description,
                       'authorName': app.owner.username,
                       'authorEmail': app.owner.email,
                       'version': version
                       })

    rendered_temp = setup_temp_obj.render(context)
    setup.write(rendered_temp)
    setup.close()

    os.chmod(os.path.join(dest, "setup.py"), 0o744)

    # Create MANIFEST.in

    manifest = open(os.path.join(dest, "MANIFEST.in"), "w+")
    manifest_temp_file = open(os.path.join(template_dir, "manifest.in.tmp"), "r")
    manifest_temp_content = manifest_temp_file.read()
    manifest_temp_file.close()
    manifest_temp_obj = Template(manifest_temp_content)

    context = Context({'applicationName': app.app_name,
                       'applicationDescription': app.description,
                       'authorName': app.owner.username,
                       'authorEmail': app.owner.email})
    rendered_temp = manifest_temp_obj.render(context)
    manifest.write(rendered_temp)
    manifest.close()

    # Run the packaging command

    fpath = "wbdap_" + app.app_name

    cwd = os.path.join(settings.PROJECT_PATH, 'filesystem/wbdap_' + app.app_name)

    os.chdir(cwd)

    from setuptools import sandbox

    setup_script = os.path.join(cwd, 'setup.py')

    args = ['sdist']

    try:
        command = ["python3", setup_script, "sdist"]
        # f = open('/tmp/readme.txt', 'w+')
        # f2 = open('/tmp/readme2.txt', 'w+')
        subprocess.call(command, stdout=None, stderr=None, shell=False)
        # p = subprocess.Popen(["python3", setup_script, "sdist"], stdout=subprocess.DEVNULL, shell=False,
        #                      preexec_fn=os.setsid)


    except SystemExit as v:
        raise DistutilsError("Setup script exited with %s" % (v.args[0],))
    except Exception as e:
        print(e)

    output_name = "django-" + app.app_name + "-" + version + ".tar.gz"
    # response = FileResponse(filename=os.path.join(cwd,"dist/"+ output_name),as_attachment = False)  # mimetype is replaced by content_type for django 1.7
    # response['Content-Type'] = 'x-gzip'

    # output = tarfile.open('GeneratedGraph.tar.gz', mode='w')
    # try:
    #     output.add(filename)
    # except Exception, e:
    #   logger.warning("Unable to write to tar")
    #   raise OCPCAError("Unable to write to tar")
    # finally:
    #     output.close()
    tar_file_path = os.path.join(cwd, "dist/" + output_name)
    print(tar_file_path)
    with tarfile.open(tar_file_path, mode='r:gz') as fh:
        # wrapper = FileWrapper(tar_file_path)
        #
        # print(wrapper.__class__)

        response = HttpResponse(content=fh.fileobj.read(), content_type='application/x-gzip')
        # response['Content-Length'] = os.path.getsize(os.path.join(cwd,"dist/"+ output_name))
        response['Content-Disposition'] = 'attachment; filename=%s' % output_name

        # response['Content-Disposition'] = 'attachment; filename=%s' % "django-"+app.app_name+"-"+version+".tar.gz"
        #     response['Content-Encoding'] = 'tar'
        #
        # tar = tarfile.open(fileobj=response, mode="w:gz")
        # tar.add(os.path.join(cwd,"dist/"+"django-"+app.app_name+"-"+version+".tar.gz"))
        # # tar.add(os.path.join(settings.SITE_ROOT, app.app_name),
        # #         arcname=os.path.basename(os.path.join(settings.SITE_ROOT, app.app_name)))
        # tar.close()
        return response


# If we are calling this ,method we are sure that there exist a application holding the mo
@login_required
def scaffold(request, app_id, model_id):
    # fields = "char:title  text:body int:posts"
    #
    # scaffold = Scaffold('app', 'moddy', fields)
    # scaffold.run()
    #
    scaffolder = DjangoApplicationCreator(Application.objects.get(id=app_id))
    scaffolder.create_model(model_id)
    # return HttpResponse('ok')
    model_form = CreateModelForm()
    model_form.helper.form_action = reverse("applicationManager:model-create", kwargs={'id': app_id})

    model_changed.send(sender=Application.__class__, test="testString",
                       application=Application.objects.get(id=app_id))

    return render(request, 'applicationManager/application_management_page.html',
                  {'app_form': CreateApplicationForm, 'model_form': model_form,
                   'app': Application.objects.get(id=app_id)})


def model_list_from_app_config(request, id):
    app = Application.objects.get(id=id)
    app = apps.get_app_config(app.appName)


# class ApplicationViewSet(ModifiedViewSet):
#     """
#     API endpoint that allows users to view existing exams
#     """
#     queryset = Application.objects.all()
#     serializer_class = ApplicationSerializer


def editors(request):
    return render(request, 'applicationManager/draganddropedit.html')


FORMS = [("Basic Info", ApplicationCreateForm1),
         ("Description", ApplicationCreateForm4),
         ("UI Libs", ApplicationCreateForm2),
         ("Default Pages", ApplicationCreateForm3),
         ]

TEMPLATES = {"Basic Info": "applicationManager/forms/formpage.html",
             "UI Libs": "applicationManager/forms/formpage.html",
             "Description": "applicationManager/forms/formpage.html",
             "Default Pages": "applicationManager/forms/formpage.html",
             }


class ApplicationCreateWizard(SessionWizardView):

    def get_template_names(self):
        logger.info(self.steps.current)
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(ApplicationCreateWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'layout':
            context.update({'layouts': ApplicationLayout.objects.all()})
            print(context)
        return context

    @transaction.atomic
    def done(self, form_list, form_dict, **kwargs):
        # form_data= [form.cleaned_data for form in form_list]
        # print(form_data)
        # print(form_data[0])
        basic_info_data = form_dict['Basic Info'].cleaned_data
        ui_libs_data = form_dict['UI Libs'].cleaned_data
        description_info_data = form_dict['Description'].cleaned_data
        default_pages_data = form_dict['Default Pages'].cleaned_data
        app = Application(  # Zorunlu alanlar
            app_name=basic_info_data['app_name'],
            verbose_name=basic_info_data['verbose_name'],
            active=basic_info_data['active'],
            core_app=basic_info_data['core_app'],
            owner_id=self.request.user.id,
            uuid=uuid.uuid4(),
            # Zorunlu olmayan alanlar
            url=basic_info_data['app_name'],
            namedUrl=basic_info_data['app_name'],
            soft_app=True,

        )

        app.save()

        project_metadata_created_signal.send(sender=Application.__class__, test="testString",
                                             application=app)
        # Following redirection done only after the last commit
        return HttpResponseRedirect(reverse('applicationManager:applications'))


def test(request):
    print('test')

    from applicationManager.util.soft_application_creator import SoftApplicationCreator
    sac = SoftApplicationCreator(application=Application.objects.get(app_name='examApp'))
    sac.load_urls()

    #
    # for up in get_resolver().url_patterns:
    #     print(up)
    #     # URLPattern()

    return HttpResponse('response')
