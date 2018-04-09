__author__ = 'ozgur'


import django.dispatch

application_created = django.dispatch.Signal(providing_args=["test","application"])
application_removed = django.dispatch.Signal(providing_args=["test","application"])
application_creation_failed = django.dispatch.Signal(providing_args=["test","application"])
model_changed = django.dispatch.Signal(providing_args=["test","application"])