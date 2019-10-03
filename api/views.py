# Create your views here.
from rest_framework import filters, viewsets, status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    RetrieveUpdateAPIView,
    DestroyAPIView
)
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from applicationManager.models import DjangoProject, Application
from applicationManager.signals.signals import project_started
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    DjangoProjectCreateSerializer,
    DjangoProjectListSerializer,
    DjangoProjectDetailSerializer,
)

from projectCore.datatable_viewset import ModifiedViewSet
import logging

logger = logging.getLogger("api.views")


# Instead of using ViewSets we can create all CRUD views seperately and manualy using Generic Views:
# these views are accessed by Router Based Paths in api.urls.py instead of routers which provide the
# necessary paths automatically (which enables us to access views in a predefined path structrue)
# ----------- APPLICATION MANAGER ------------------------------

class ApplicationCreateAPIView(CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationCreateSerializer


class ApplicationListAPIView(ListAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationListSerializer


class ApplicationDetailAPIView(RetrieveAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class ApplicationUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class ApplicationDeleteAPIView(DestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


# ----------- PROJECT ------------------------------

class DjangoProjectCreateAPIView(CreateAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectCreateSerializer



class DjangoProjectListAPIView(ListAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectListSerializer


class DjangoProjectDetailAPIView(RetrieveAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class DjangoProjectUpdateAPIView(RetrieveUpdateAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class DjangoProjectDeleteAPIView(DestroyAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


# Following is a simple function based view decorated with api_view
# to let function return Response object. For class based views only viewsets can have
# custom actions
@api_view(['get', 'post'])
def startProject(request, pk):
    app = DjangoProject.objects.get(id=pk)
    # try to run app
    project_started.send(sender=DjangoProject.__class__, test="testString",
                                         project=app)

    return Response({'port': app.port})




