from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Reset, Button, HTML
from django import forms
from django.forms import ModelForm
from django.urls import reverse
from openpyxl.chart import label

from applicationManager.models import Application, AppModel, Field

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
        model= AppModel
        fields=('name',)


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



class CreateModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(('Model Parameters'), 'name', 'owner_app'),
            HTML("<hr>"),
            FormActions(
                Submit('save', ('Submit'), css_class='btn btn-primary '),
                Button('close', ('Close'), css_class='btn btn-default',data_dismiss='modal')
            )
        )

        # self.helper.add_input(Submit('submit', 'Submit'))
        super(CreateModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AppModel
        fields = ['name', 'owner_app']



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
        fields = ['name', 'field_type','type_parameter','owner_model']





class UpdateFieldForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        # self.helper.form_action = '.'
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
        super(UpdateFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Field
        fields = ['name', "field_type", 'type_parameter', 'owner_model']



