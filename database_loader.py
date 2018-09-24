# coding=utf-8
"""
Wrapper for loading templates from the database.
"""

from django.core.exceptions import SuspiciousFileOperation, MultipleObjectsReturned
from django.template import Origin, TemplateDoesNotExist
from django.utils._os import safe_join

from django.template.loaders.base import Loader as BaseLoader

from applicationManager.models import ApplicationComponentTemplate


class DatabaseLoader(BaseLoader):


    def get_contents(self, origin):
        print('origin.name : '+str(origin.name))
        print('origin.temp_name : ' + str(origin.template_name))
        try:
            name, type = origin.template_name.split('__')
        except ValueError as e:
            print(e)
            name=type = None
            raise TemplateDoesNotExist(origin)


        try:
            # print('template_name: '+str(ApplicationComponentTemplate.objects.get(temp_name=origin.template_name)))
            #
            # print('count: '+str(ApplicationComponentTemplate.objects.get(temp_name=origin.template_name).count()))
            temp = ApplicationComponentTemplate.objects.get(temp_name=name, temp_type=type)
            return temp.temp_content

        except MultipleObjectsReturned as e:
            print(e.__class__.__name__)
            raise MultipleObjectsReturned
        except TemplateDoesNotExist as e:
            raise TemplateDoesNotExist(origin)

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Return an Origin object pointing to an absolute path in each directory
        in template_dirs. For security reasons, if a path doesn't lie inside
        one of the template_dirs it is excluded from the result set.
        """
        # for template_dir in self.get_dirs():
            # try:
            #     name = safe_join(template_dir, template_name)
            # except SuspiciousFileOperation:
            #     # The joined path was located outside of this template_dir
            #     # (it might be inside another one, so this isn't fatal).
            #     continue




        yield Origin(
            name=template_name,
            template_name=template_name,
            loader=self,
        )