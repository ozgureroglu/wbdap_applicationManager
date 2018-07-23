# coding=utf-8

import os
import shutil
from io import StringIO

from django.template import loader
from mako.template import Template

from applicationManager.models import Application
from wbdap.settings import development as settings
from ast import literal_eval


def create_model(self, app, model):
    self._info("   Model   ")
    self._info("===========")

    # Open models.py to read
    with open('{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 'r') as fp:
        self.models_file = fp

        # Check if model already exists
        for line in self.models_file.readlines():
            if 'class {0}'.format(self.model) in line:
                self._info('exists\t{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)
                return

        self._info('create\t{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 1)

        # Prepare fields
        self.imports = []
        fields = []

        for field in self.fields:
            new_field = self.get_field(field)

            if new_field:
                fields.append(new_field)
                self._info('added\t{0}{1}/models.py\t{2} field'.format(
                    self.SCAFFOLD_APPS_DIR, self.app, field.split(':')[1]), 1)

    # Open models.py to append
    with open('{0}{1}/models.py'.format(self.SCAFFOLD_APPS_DIR, self.app), 'a') as fp:
        fp.write(''.join([import_line for import_line in self.imports]))
        fp.write(MODEL_TEMPLATE % (self.model, ''.join(field for field in fields)))


def create_api_views(appname):
    appfolder = os.path.join(settings.API_DIR, appname)
    with open('{0}/views.py'.format(appfolder), 'a') as fp:
        fp.write()


def create_api(app, **kwargs):
    # if create_api_folder(app):
    create_views_file(app)


def get_models(app: Application):
    from django.apps import apps
    apps.get_models()
    app_conf = apps.get_app_config(app.app_name)

    models = app_conf.get_models()
    return models


def create_views_file(appname):

    appfolder = os.path.join(settings.API_DIR, appname)
    if not os.path.exists(os.path.join(appfolder, 'views.py')):
        search_fields = None
        ordering_fields = None
        models = None

        t = loader.get_template('projectCore/file_templates/api_view.txt')

        c = {'applicationName': appname}

        try:
            search_fields = {}
            ordering_fields = {}

            app = Application.objects.get(app_name=appname)
            models = get_models(app)
            data = []
            for m in models:

                triple = ()
                triple = triple + (m.__name__,)
                fields = m._meta.get_fields()
                model_fields = ()

                for f in fields:

                    if f.name != 'id':
                        model_fields = model_fields + (f.name,)

                triple = triple + (model_fields,)
                triple = triple + (model_fields,)

                data.append(triple)
            c['data'] = data

        except Exception as e:
            print('%s %s' % (e, type(e)))
            return False


        rendered = t.render(c)

        try:
            with open('{0}/views.py'.format(appfolder), 'wb') as f:
                f.write(rendered.encode("UTF-8"))

        except FileNotFoundError as e:
            print(e)


def create_serializers_file(appname):
    pass

def rewrite_api_urls():
    pass

def create_api_folder(appname):
    try:
        os.mkdir(os.path.join(settings.API_DIR, appname))
    except FileExistsError as e:
        print(e)
    else:
        return False

    return True
