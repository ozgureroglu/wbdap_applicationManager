__author__ = 'ozgur'

from django.urls import path, include

# Uncomment the next two lines to enable the admin:
from applicationManager import views
from django.contrib import admin
from rest_framework import routers
from applicationManager.views import *

#Admin 4
admin.autodiscover()
#
# # Serve the exams rest api
# router = routers.DefaultRouter()
# router.register(r'applications', views.ApplicationViewSet)
# router.register(r'appmodels', views.AppModelViewSet, base_name='appmodel')
# router.register(r'fields', views.FieldViewSet)


app_name = 'applicationManager'
urlpatterns = [


    path('apps/<uuid:uuid>/', redirect_to_app, name="redirect-to-app"),


    path('', landing_page, name='landing'),
    path('cdt/', countdown_test_page, name='cdt'),
    path('dashboard/', dashboard, name='dashboard'),
    # ---------------------------------------------------

    path('generatedata/<int:appid>/', generate_data, name='generate-data'),
    path('dumpall/', dump_all_data, name='dump-all-data'),
    path('genuuidall/', genuuid_all, name='genuuid-all'),
    path('reindexApps/', reindexApps, name='reindexApps'),

    path('createApplication/', createApplication, name='createApplication'),
    path('ca2/', ApplicationCreateWizard.as_view(FORMS), name='createApplication2'),
    # path('deleteApplication/<pk>/', ApplicationDelete.as_view(), name='deleteApplication'),

    path('application/<int:id>/', application_info, name='application-info'),
    path('application/<int:id>/genuuid/', genuuid_app, name='genuuid-app'),
    path('application/<int:id>/delete/', delete_application, name='delete-application'),
    path('application/<int:id>/dumpdata/', dump_app_data, name='dump-app-data'),
    path('application/<int:id>/loaddata/', load_data, name='load-data'),
    path('application/<int:id>/download/', download_app, name='download-app'),
    path('application/<int:id>/newfile/', create_file, name='create-file'),
    path('application/<int:id>/trigger/', trigger, name='trigger'),
    path('application/<int:id>/activate/', application_activate, name='application-activate'),
    path('application/<int:id>/models/', AppModelListView.as_view(), name='model-list'),
    path('application/<int:id>/models/add/', ModelCreateView.as_view(), name='model-create'),
    path('application/<int:id>/models/<int:pk>/', AppModelDetailView.as_view(), name='model-details'),
    path('application/<int:id>/models/<int:model_id>/scaffold/', scaffold, name='model-scaffold'),
    path('application/<int:id>/models/<int:model_id>/update/', ModelUpdate.as_view(), name='model-update'),
    path('application/<int:id>/models/<int:model_id>/delete/', ModelDelete.as_view(), name='model-delete'),
    path('application/<int:id>/models/<int:model_id>/fields/', FieldListView.as_view(), name='field-list'),
    path('application/<int:id>/models/<int:model_id>/fields/add/', FieldCreateView.as_view(), name='field-create'),
    path('application/<int:id>/models/<int:model_id>/fields/<int:pk>/', FieldDetailView.as_view(), name='field-details'),
    path('application/<int:id>/models/<int:model_id>/fields/<int:field_id>/update/', FieldUpdateView.as_view(), name='field-update'),
    # path('application/<app_id>/model/<model_id>/field/<pk>/update/', field_update, name='field-update'),
    path('application/<int:app_id>/models/<int:model_id>/field/<pk>/delete/', FieldDeleteView.as_view(),
        name='field-delete'),

    # path('addApplicationModel/<int:pk>/', add_application_model, name='addApplicationModel'),

    # path('application/<int:id>/model/<model_id>/field/', model_field_list, name='field-list'),
    # path('application/<int:id>/model/<model_id>/field/<field_id>/', model_field_details, name='field-details'),
    # path('application/<int:id>/model/<model_id>/field/<field_id>/delete/', model_field_delete, name='field-delete'),

    # path('application/<int:id>/model/', model_list, name='model-list'),
    # path('application/<int:id>/model/<model_id>/', model_details, name='model-details'),
    # path('application/<int:id>/model/<model_id>/delete/', model_delete, name='model-delete'),
    #
    #
    # path('application/<int:id>/model/<model_id>/field/', model_field_list, name='field-list'),
    # path('application/<int:id>/model/<model_id>/field/<field_id>/', model_field_details, name='field-details'),
    # path('application/<int:id>/model/<model_id>/field/<field_id>/delete/', model_field_delete, name='field-delete'),


    path('updateAppsDB/', updateAppsDB, name='updateAppsDB'),
    path('serializeConfs/', serializeConfs, name='serializeConfs'),
    path('deserializeConfs/', deserializeConfs, name='deserializeConfs'),

    path('editor/', editors, name='editors'),

]
