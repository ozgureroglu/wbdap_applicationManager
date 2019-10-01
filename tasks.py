# coding=utf-8
from celery import shared_task
from django.core import serializers

from applicationManager.models import Application, DjangoProject
from applicationManager.util.django_project_manager import DjangoProjectManager
from wbdap.celery import app


@app.task()
def appList():
    return serializers.serialize('json', Application.objects.all())

@app.task
def add2(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def create_django_project(project: DjangoProject):
    dpm = DjangoProjectManager(project=project)
    dpm.create()

