from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

class AppSetting(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    defaultSettings = models.BooleanField(default=True)

    def __unicode__(self):
        return self.title

@admin.register(AppSetting)
class AppSettingsAdmin(admin.ModelAdmin):
        pass

# Sifreler ile ilgili ayarlarin yapilmasi icin kullanilacak olan model.
class PasswordSetting(models.Model):
    minLength = models.IntegerField()
    maxLength = models.IntegerField()

@admin.register(PasswordSetting)
class PasswordSettingsAdmin(admin.ModelAdmin):
    pass


# model for applications that have been created by this applicationManager.
class Application(models.Model):
    app_name =  models.CharField(max_length=25) # app_name parameter for urls.py
    verbose_name = models.CharField(max_length=50) #Human readable form of the name
    url = models.CharField(max_length=30) #relative path to this application
    namedUrl = models.CharField(max_length=30) # name field of the urlconfig entry for reverse resolutions

    active = models.BooleanField(default=True,blank=True)
    description = models.CharField(max_length=500) # Description of the application
    coming_soon_page = models.BooleanField(default=True,blank=False) # want to include a coming_soon page

    owner = models.ForeignKey(User,on_delete=models.CASCADE) # Owner of this application
    core_app = models.BooleanField(default=False, blank=False)
    # uuid = models.UUIDField(primary_key=False, editable=True, blank=True,null=True)
    uuid = models.UUIDField(primary_key=False, blank=True,null=True)

    # model = models.ForeignKey(AppModel, null=True,blank=True)

    def __str__(self):
        return self.app_name

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    pass


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