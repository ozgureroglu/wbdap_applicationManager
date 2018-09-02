# coding=utf-8
"""
Wrapper for loading templates from the database.
"""

from django.core.exceptions import SuspiciousFileOperation
from django.template import Origin, TemplateDoesNotExist
from django.utils._os import safe_join

from django.template.loaders.base import Loader as BaseLoader

from applicationManager.models import ApplicationComponentTemplate


class DatabaseLoader(BaseLoader):


    def get_contents(self, origin):
        try:
            # print(origin.template_name)
            if ApplicationComponentTemplate.objects.filter(temp_name=origin.template_name).exists():
                return ApplicationComponentTemplate.objects.get(temp_name=origin.template_name)
        except KeyError:
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


        print(template_name)
        yield Origin(
            name=template_name,
            template_name=template_name,
            loader=self,
        )