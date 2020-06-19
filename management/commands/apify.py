import os
from pathlib import Path
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from io import StringIO
from mako.runtime import Context
from mako.template import Template
from mako import exceptions



class Command(BaseCommand):
    help = 'Creates DRF API for the given application'

    def add_arguments(self, parser):
        parser.add_argument('app', nargs=1, type=str,
                            help='Name of the application in which DRF Api will be created')

    def handle(self, *args, **options):
        if len(options['app']) == 0:
            print("You must provide app name. For example:\n\npython manage.py apify my_app\n")
            return

        app = options['app'][0]

        if Path(settings.SITE_ROOT).joinpath(app).joinpath('api').is_dir():
            self.stderr.write(self.style.ERROR('API folder exists'))
        else:
            Path(settings.SITE_ROOT).joinpath(app).joinpath('api').mkdir()

        if Path(settings.SITE_ROOT).joinpath(app).joinpath('api').joinpath('serializers').is_dir():
            self.stderr.write(self.style.ERROR('Serializers folder exists'))
        else:
            Path(settings.SITE_ROOT).joinpath(app).joinpath('api').joinpath('serializers').mkdir()

        app_models = apps.get_app_config(app).get_models()

        for model in app_models:
            # print(model.__name__)
            template_file = os.path.join(settings.SITE_ROOT,'applicationManager/templates/applicationManager/applicationFileTemplates/drf_api_serializer.txt')
            context = {'app': str(app), 'model': str(model.__name__)}
            loc = Path(settings.SITE_ROOT) / app / 'api' / 'serializers' / (model.__name__+'_serializer.py')

            print(template_file)
            print(context)
            print(loc.__class__)

            self.create_file_from_template(template_file, context, loc)

        # scaffold = Scaffold(app_name, model_name, fields)
        # scaffold.run()

        self.stdout.write(self.style.SUCCESS('Successfully created api for app :{0}').format(app))

    def create_file_from_template(self, template_file, context, loc):
        try:
            t = Template(filename=template_file, strict_undefined=True)
            buf = StringIO()
            c = Context(buf,**context )
            t.render_context(c)
            loc.write_text(buf.getvalue())

        except Exception as e:

            self.stderr.write(self.style.ERROR("Exception occurred while creating file : {0}").format(e))

            raise Exception('creation of file failed: ' + str(e))


