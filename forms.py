import random

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Reset, Button, HTML
from django import forms
from django.forms import ModelForm, RadioSelect
from django.urls import reverse
from openpyxl.chart import label

from applicationManager.models import Application, AppModel, AppModelField, ApplicationDefaultPages, DjangoProject

__author__ = 'ozgur'

FAVORITE_COLORS_CHOICES = (
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('black', 'Black'),
)

class CreateAppForm_OLD(ModelForm):
    appName = forms.CharField(label="Short Application Name", widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'appName'}))
    verbose_name = forms.CharField(label="Long Application Name", widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'verbose_name'}))
    url = forms.CharField(label="Application Access URL", widget=forms.TextInput(attrs={'class': 'form-control'}))
    namedUrl = forms.CharField(label="Application Named Access URL ", widget=forms.TextInput(attrs={'class': 'form-control'}))
    # active = forms.BooleanField(required=False,label="Activate", widget=forms.CheckboxInput(attrs={'class': 'checkbox'}))
    description = forms.CharField(label="Application Definition", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}))
    # model = forms.MultipleChoiceField(
    #     required=False,
    #     widget=forms.CheckboxSelectMultiple,
    #     choices=FAVORITE_COLORS_CHOICES,
    # )


    class Meta:
        exclude = []
        model = Application
        # Edit sayfasindan girilecek olan attributelar
        exclude = ['model','active','owner']

        # widgets = {
        #     'models': forms.widgets.CheckboxSelectMultiple(),
        # }


class AddApplicationModelForm(ModelForm):
    class Meta:
        model = AppModel
        fields = ('name',)


class CreateApplicationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset((''), 'app_name', 'verbose_name','url', 'namedUrl',  'description', 'core_app' ), # Birinci parantezin ici doldurulursa for uzerinde bir title alani beliriyor
            ButtonHolder(
                Submit('save', ('Submit'), css_class='btn btn-primary '),
                Reset('reset', ('Cancel'), css_class='btn')
            )
        )

        # self.helper.add_input(Submit('submit', 'Submit'))
        super(CreateApplicationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Application
        fields = ["app_name", 'verbose_name', 'url', 'namedUrl', "description", "core_app"]


class CreateProjectForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('', 'name', 'port','description'),
            ButtonHolder(
                Submit('save', ('Submit'), css_class='btn btn-primary '),
                Reset('reset', ('Cancel'), css_class='btn')
            )
        )

        # self.helper.add_input(Submit('submit', 'Submit'))
        super(CreateProjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DjangoProject
        fields = ["name", "port", "description"]


class CreateModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(('Model Parameters'), 'name', 'owner_app', 'definition'),
            HTML("<hr>"),
            FormActions(
                Submit('save', ('Submit'), css_class='btn btn-primary '),
                Button('close', ('Close'), css_class='btn btn-default', data_dismiss='modal')
            )
        )

        # self.helper.add_input(Submit('submit', 'Submit'))
        super(CreateModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AppModel
        fields = ['name', 'owner_app','definition']


class CreateAppModelFieldForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(('Model Parameters'), 'name', 'field_type','type_parameter','owner_model'),
            HTML("<hr>"),
            FormActions(
                Submit('save', ('Submit'), css_class='btn btn-primary '),
                Button('close', ('Close'), css_class='btn btn-default',data_dismiss='modal')
            )
        )

        # self.helper.add_input(Submit('submit', 'Submit'))
        super(CreateAppModelFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AppModelField
        fields = ['name', 'field_type', 'type_parameter', 'owner_model']


class UpdateAppModelFieldForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        # self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(('Model Parameters'), 'name', 'field_type', 'type_parameter', 'owner_model'),
            HTML("<hr>"),
            FormActions(
                Submit('save', ('Submit'), css_class='btn btn-primary '),
                Button('close', ('Close'), css_class='btn btn-default', data_dismiss='modal')
            )
        )

        # self.helper.add_input(Submit('submit', 'Submit'))
        super(UpdateAppModelFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AppModelField
        fields = ['name', "field_type", 'type_parameter', 'owner_model']


class ProjectCreateForm1(ModelForm):
    form_desc = "Enter basic information about the Project that will be created."
    def __init__(self, *args, **kwargs):

        # If you pass FormHelper constructor a form instance
        # It builds a default layout with all its fields
        self.helper = FormHelper()
        self.helper.attrs = {'novalidate': 'novalidate'}
        # self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'text-center col-lg-4'
        # self.helper.field_class = 'col-lg-8'

        # set initial value to a modelform field
        initial = kwargs.pop('initial', {})

        initial['port'] = random.randint(1000, 10000)
        kwargs['initial'] = initial

        super(ProjectCreateForm1, self).__init__(*args, **kwargs)

    class Meta:
        model = DjangoProject
        fields = ['name', 'port', 'description']
        # exclude = ['pid', 'status', ]



class ProjectCreateForm2(ModelForm):
    form_desc = "Enable a sample application"
    class Meta:
        fields = ['sample_app']
        model = DjangoProject


class ProjectCreateForm3(ModelForm):
    form_desc = "Enter the details for the sample application"
    class Meta:
        fields = ['enable_drf_api', 'enable_messages']
        model = DjangoProject


class ApplicationCreateForm1(ModelForm):
    """
    Application create form for step 1
    """
    form_desc = "Enter the details for the application. Some of these can be changed later from the application management page"
    name = "Basic Information"
    class Meta:
        # fields = ['app_name', 'verbose_name', 'description', 'url', 'namedUrl', 'active','published']
        fields = '__all__'
        exclude = ['verbose_name','url','namedUrl', 'owner', 'uuid']
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'A brief explanation of this application.'})
        }
        model = Application


class ApplicationCreateForm3(forms.Form):
    form_desc = "Select the libraries that should be enabled for this application."
    name = "Default Libs"

    BS_VERS=(
        ('4.1', 'Bootstrap v4.1'),
        ('4.0', 'Bootstrap v4.0.0'),
        ('3.7.1', 'Bootstrap v3.3.7'),
    )

    JQUERY_VERS=(
        ('3.3.1', 'jQuery Core 3.3.1'),
        ('3.3.0', 'jQuery Core 3.3.0'),
        ('3.2.1', 'jQuery Core 3.2.1'),
        ('3.2.0', 'jQuery Core 3.2.0'),
        ('3.1.1', 'jQuery Core 3.1.1'),
        ('3.1.0', 'jQuery Core 3.1.0'),
        ('3.0.0', 'jQuery Core 3.0.0'),
        ('2.2.4', 'jQuery Core 2.2.4'),
        ('2.2.3', 'jQuery Core 2.2.3'),
        ('2.2.2', 'jQuery Core 2.2.2'),
        ('2.2.1', 'jQuery Core 2.2.1'),
        ('2.2.0', 'jQuery Core 2.2.0'),
    )

    bootsrap_version = forms.CharField(label='Bootstrap version', widget=forms.Select(choices=BS_VERS))
    jquery_version = forms.CharField(label='JQuery version', widget=forms.Select(choices=JQUERY_VERS))


class ApplicationCreateForm4(ModelForm):
    form_desc = "Enter basic information about the Application Models that will be created."
    def __init__(self, *args, **kwargs):
        super(ApplicationCreateForm4, self).__init__(*args, **kwargs)



        # If you pass FormHelper constructor a form instance
        # It builds a default layout with all its fields
        self.helper = FormHelper()
        self.helper.attrs = {'novalidate': 'novalidate'}
        # self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'text-center col-lg-4'
        # self.helper.field_class = 'col-lg-8'

        # set initial value to a modelform field
        # initial = kwargs.pop('initial', {})
        #
        # initial['port'] = random.randint(1000, 10000)
        # kwargs['initial'] = initial


    class Meta:
        fields = ['name', 'definition']
        model = AppModel



#
# class CustomRadioSelect(RadioSelect):
#     template_name = 'applicationManager/forms/template.html'
#     option_template_name = 'applicationManager/forms/radio_option_custom.html'


class ApplicationCreateForm2(ModelForm):
    form_desc = "Enter the pages that should be created for this application."
    name = "Default Pages"
    class Meta:
        fields = ['coming_soon_page','about_us_page','contact_us_page','landing_page','maintenance_page']
        model = ApplicationDefaultPages



# factory here is creating a class
ModelFormSet = forms.models.modelformset_factory(AppModel, fields='__all__')
FieldFormSet = forms.models.modelformset_factory(AppModelField, fields='__all__')



