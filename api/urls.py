from rest_framework_nested import routers

from applicationManager.api.views import startProject
from .views import (
    ApplicationCreateAPIView,
    ApplicationDeleteAPIView,
    ApplicationDetailAPIView,
    ApplicationListAPIView,
    ApplicationUpdateAPIView,
    DjangoProjectCreateAPIView,
    DjangoProjectListAPIView,
    DjangoProjectUpdateAPIView,
    DjangoProjectDetailAPIView,
    DjangoProjectDeleteAPIView,
)



from django.urls import include, path
app_name = 'applicationManager-api'

# ------ Identity Manager Router Configuration-----------------------------------------------------------
# Router conf. gives us the luxury to not define paths manually, instead router enables all CRUD paths with accordance
# to a predifined path structure.


urlpatterns = [

    # --------- Router Based Paths ------------
    # path('', include(identitymanager_router.urls)),

    # --------- Custom paths -------------------
    # Following paths are just for application API
    path('application/', ApplicationListAPIView.as_view(), name='application-list'),
    path('application/create/', ApplicationCreateAPIView.as_view(), name='application-create'),
    path('application/<int:pk>/', ApplicationDetailAPIView.as_view(), name="application-detail"),
    path('application/<int:pk>/edit/', ApplicationUpdateAPIView.as_view(), name="application-edit"),
    path('application/<int:pk>/delete/', ApplicationDeleteAPIView.as_view(), name="application-delete"),

    # Following paths are just for djangoproject API
    path('djangoproject/', DjangoProjectListAPIView.as_view(), name='djangoproject-list'),
    path('djangoproject/create/', DjangoProjectCreateAPIView.as_view(), name='djangoproject-create'),
    path('djangoproject/<int:pk>/', DjangoProjectDetailAPIView.as_view(), name="djangoproject-detail"),
    path('djangoproject/<int:pk>/start/', startProject, name="djangoproject-start"),
    path('djangoproject/<int:pk>/edit/', DjangoProjectUpdateAPIView.as_view(), name="djangoproject-edit"),
    path('djangoproject/<int:pk>/delete/', DjangoProjectDeleteAPIView.as_view(), name="djangoproject-delete"),

]
