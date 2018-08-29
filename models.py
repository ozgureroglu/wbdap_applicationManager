from dill import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from ckeditor.fields import RichTextField

import logging

logger = logging.getLogger('applicationManager_models')




# Sifreler ile ilgili ayarlarin yapilmasi icin kullanilacak olan model.
class PasswordSetting(models.Model):
    minLength = models.IntegerField()
    maxLength = models.IntegerField()

@admin.register(PasswordSetting)
class PasswordSettingsAdmin(admin.ModelAdmin):
    pass


class PageLayout(models.Model):
    layout_name = models.CharField(max_length=25, blank=False, null=False)
    content = RichTextField()


    def __str__(self):
        return self.layout_name


    def __unicode__(self):
        return self.layout_name

@admin.register(PageLayout)
class PageLayoutAdmin(admin.ModelAdmin):
    pass



# model for applications that have been created by this applicationManager.
class Application(models.Model):
    app_name = models.CharField(max_length=25,null=False, blank=False) # app_name parameter for urls.py
    verbose_name = models.CharField(max_length=50, null=False, blank=False) #Human readable form of the name
    url = models.CharField(max_length=30) #relative path to this application
    namedUrl = models.CharField(max_length=30) # name field of the urlconfig entry for reverse resolutions

    active = models.BooleanField(default=True, blank=True)
    description = models.TextField(max_length=500) # Description of the application
    coming_soon_page = models.BooleanField(default=True, blank=False) # want to include a coming_soon page

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING) # Owner of this application
    core_app = models.BooleanField(default=False, null=False,blank=False)
    # uuid = models.UUIDField(primary_key=False, editable=True, blank=True,null=True)
    uuid = models.UUIDField(primary_key=False, blank=True,null=True)



    def __str__(self):
        return self.app_name

    class Meta:
        permissions = (
            ("has_access", "Has access to application pages"),
        )

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    pass


class ApplicationViewMethod(models.Model):
    view_name = models.CharField(max_length=50,null=True, blank=True)
    view_code = models.TextField(max_length=500,null=True, blank=True,default=None)
    #TODO: it is really important to integrate ace_editor, as thois rich text editor is not very usable.
    # view_code = RichTextField()
    app = models.ForeignKey(Application, null=False, blank=False, on_delete=models.CASCADE, related_name='views62')


    def __str__(self):
        return self.view_name

@admin.register(ApplicationViewMethod)
class ApplicationViewMethodAdmin(admin.ModelAdmin):
    pass




class ApplicationUrl(models.Model):
    url_pattern = models.CharField(max_length=50,null=True, blank=True)
    view_method = models.ForeignKey(ApplicationViewMethod, on_delete=models.CASCADE,related_name='mapped_view')
    url_name = models.CharField(max_length=50,null=True, blank=True)

    def __str__(self):
        return self.url_name

@admin.register(ApplicationUrl)
class ApplicationUrlAdmin(admin.ModelAdmin):
    pass



PAGE_TYPES =   (
    ('predefined','Predefined Template'),
    ('empty','Empty Page'),
    ('landing', 'Landing Page'),
    ('index', 'Application Index Page'),
    ('about', 'About Page'),
    ('contact', 'Contact Page'),
)
class ApplicationPage(models.Model):
    app = models.OneToOneField(Application, null=False, blank=False, on_delete=models.CASCADE, related_name='pages')
    page_type = models.CharField(max_length=25,choices=PAGE_TYPES, default='predefined')
    page_name = models.CharField(max_length=25, blank=False, null=False)
    page_layout = models.ForeignKey(PageLayout, blank=False, null=False,on_delete=models.DO_NOTHING)


    def __str__(self):
        return self.page_name


    def __unicode__(self):
        return self.page_name

@admin.register(ApplicationPage)
class ApplicationPageAdmin(admin.ModelAdmin):
    pass


SETTING_TYPES = (
    ('boolean','Boolean Type'),
    ('text','Text Input Type'),
)


class SettingDefinition(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, default=None)
    verbose_name = models.CharField(max_length=60, blank=False, null=False, default=None)
    # type = models.CharField(max_length=30, choices=SETTING_TYPES, blank=False, null=False, default='boolean')
    # value = models.BooleanField(max_length=30, blank=False, null=False, default=False)
    definition = models.CharField(max_length=100, blank=False, null=False, default=None)

    def __str__(self):
        return self.name


    def __unicode__(self):
        return self.name

@admin.register(SettingDefinition)
class SettingDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'definition')

class ApplicationSettingsList(models.Model):
    app = models.ForeignKey(Application, null=False, blank=False, on_delete=models.DO_NOTHING,related_name='settings_list')
    setting = models.ForeignKey(SettingDefinition, null=False, blank=False, on_delete=models.DO_NOTHING)
    value = models.BooleanField(default=False)

    def __str__(self):
        return self.app.app_name+'_settings'


    def __unicode__(self):
        return self.app.app_name + '_settings'


    def toogle_setting(self):

        # print(getattr(self.setting, ttype))

        try:
            # setting = ApplicationSettingsList.objects.get(app_id=id, setting_id=setting_id)
            # val = setting.value
            # setting.value = not val
            # # setattr(self.setting, ttype, not val)
            # setting.save()

            self.value = not self.value
            self.save()

        except AttributeError as e:
            logger.fatal(e)

    class Meta:
        unique_together = ("app", "setting")

@admin.register(ApplicationSettingsList)
class ApplicationSettingsListAdmin(admin.ModelAdmin):
    list_display = ('app', 'setting', 'value')


#
# class ApplicationSettings(models.Model):
#     app = models.OneToOneField(Application, null=False, blank=False, on_delete=models.CASCADE)
#     api_enabled = models.BooleanField(default=False, blank=False, help_text='If checked, enables the DRF API for the app')
#     display_wbdap_admin_menu = models.BooleanField(default=False, blank=False, help_text='If checked, enables the global WBDAP admin menu on each page of the application')
#     display_app_admin_menu = models.BooleanField(default=False, blank=False, help_text='If checked, enables app specific admin menu on each page of the application')
#
#
#     def toogle_setting(self, ttype):
#         print(ttype)
#         print(getattr(self, ttype))
#         try:
#             val = getattr(self, ttype)
#
#             setattr(self, ttype, not val)
#             self.save()
#
#         except AttributeError as e:
#             logger.fatal(e)
#
#
#     def __unicode__(self):
#         return self.app.app_name+"_settings"
#
#     def __str__(self):
#         return self.app.app_name+"_settings"


#
# @admin.register(ApplicationSettings)
# class AppSettingsAdmin(admin.ModelAdmin):
#         pass



class DataDump(models.Model):
    application = models.ForeignKey(Application,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class AppModel(models.Model):
    name = models.CharField(max_length=30)
    definition = models.TextField(max_length=250,blank=True,null=False)
    owner_app = models.ForeignKey(Application,on_delete=models.CASCADE,related_name="models", blank=False,null=False)

    def __str__(self):
        return self.name

@admin.register(AppModel)
class AppModelAdmin(admin.ModelAdmin):
    pass


class Field(models.Model):
    fields = models.fields_all
    flist=[]
    for field in fields:

        fkey = field
        fval = field
        f = (fkey, fval)
        flist.append(f)

    name = models.CharField(max_length=30)
    field_type = models.CharField(max_length=30, choices=tuple(flist))
    type_parameter = models.TextField(max_length=150,blank=True,null=True)
    definition = models.TextField(max_length=250,blank=True,null=False)
    owner_model = models.ForeignKey(AppModel,on_delete=models.CASCADE,related_name='fields')

    def __str__(self):
        return self.name


@admin.register(Field)
class ModelFieldAdmin(admin.ModelAdmin):
    pass


class ApplicationLayout(models.Model):
    name = models.CharField(max_length=50)
    # image_url = models.URLField()
    # live_url = models.URLField()

    def __unicode__(self):
        return self.name





