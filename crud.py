from crudbuilder.abstract import BaseCrudBuilder

from applicationManager.models import ApplicationLayout


class ApplicationLayoutCrud(BaseCrudBuilder):
        model = ApplicationLayout
        search_fields = ['name']
        tables2_fields = ('name', 'image_url', 'live_url')
        tables2_css_class = "table table-bordered table-condensed"
        tables2_pagination = 20  # default is 10
        modelform_excludes = []
        login_required=True
        permission_required=True
        # permissions = {
        #   'list': 'example.person_list',
        #       'create': 'example.person_create'
        # }