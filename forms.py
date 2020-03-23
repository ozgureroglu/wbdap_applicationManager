from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Reset, Button, HTML
from django import forms
from django.forms import ModelForm, RadioSelect
from django.urls import reverse
from openpyxl.chart import label

from applicationManager.models import Application, AppModel, Field, ApplicationDefaultPages, DjangoProject

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


class CreateFieldForm(ModelForm):
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
        super(CreateFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Field
        fields = ['name', 'field_type', 'type_parameter', 'owner_model']


class UpdateFieldForm(ModelForm):
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
        super(UpdateFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Field
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

        super(ProjectCreateForm1, self).__init__(*args, **kwargs)

    class Meta:
        model = DjangoProject
        exclude = ['pid', 'status', ]



class ProjectCreateForm2(ModelForm):
    form_desc = "test form desc2"
    class Meta:
        fields = ['port']
        model = DjangoProject


class ApplicationCreateForm1(ModelForm):
    class Meta:
        exclude = ['description', 'url', 'namedUrl', 'owner', 'uuid']
        model = Application


class ApplicationCreateForm2(forms.Form):
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
    class Meta:
        fields = ['description']
        model = Application



#
# class CustomRadioSelect(RadioSelect):
#     template_name = 'applicationManager/forms/template.html'
#     option_template_name = 'applicationManager/forms/radio_option_custom.html'


class ApplicationCreateForm3(ModelForm):
    class Meta:
        fields = ['coming_soon_page','about_us_page','contact_us_page','landing_page','maintenance_page']
        model = ApplicationDefaultPages

