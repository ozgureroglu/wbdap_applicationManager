import django.dispatch

# Detailed tutorial: http://sabinemaennel.ch/django/signals-in-django/

soft_application_created_signal = django.dispatch.Signal(providing_args=["test", "application"])
soft_application_removed_signal = django.dispatch.Signal(providing_args=["test", "application"])
application_created_signal = django.dispatch.Signal(providing_args=["test", "application"])
application_removed_signal = django.dispatch.Signal(providing_args=["test", "application"])
application_creation_failed_signal = django.dispatch.Signal(providing_args=["test", "application"])
model_changed_signal = django.dispatch.Signal(providing_args=["test", "application"])


project_metadata_created_signal = django.dispatch.Signal(providing_args=["test", "application"])
project_metadata_removed_signal = django.dispatch.Signal(providing_args=["test", "application"])

project_started = django.dispatch.Signal(providing_args=["application"])
project_stopped = django.dispatch.Signal(providing_args=["application"])
