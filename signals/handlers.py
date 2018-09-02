from applicationManager.util.soft_application_creator import SoftApplicationCreator

__author__ = 'ozgur'

import logging

from applicationManager.signals.signals import application_created_signal, application_creation_failed_signal, \
    application_removed_signal, model_changed_signal, soft_application_created_signal, soft_application_removed_signal

from django.dispatch import receiver

from applicationManager.util.django_application_creator import DjangoApplicationCreator
from applicationManager.util.django_application_remover import DjangoApplicationRemover

logger = logging.getLogger(name="wbdap.debug")


# Called when he application is created
@receiver(application_created_signal)
def application_created(sender, **kwargs):
    logger.info("application_created signal receieved")

    dj_app_creator = DjangoApplicationCreator(kwargs['application'])
    dj_app_creator.create()


# Called when he application is created
@receiver(soft_application_created_signal)
def soft_application_created(sender, **kwargs):
    logger.info("soft_application_created signal receieved")
    app = kwargs['application']

    sac = SoftApplicationCreator(app)
    sac.create_settings()
    sac.create_default_views()
    sac.create_default_urls()






# Called when he application is created
@receiver(soft_application_removed_signal)
def soft_application_removed(sender, **kwargs):
    logger.info("soft_application_removed signal receieved")


@receiver(application_creation_failed_signal)
def rollback_setup(sender, **kwargs):
    logger.warning("Application creating steps will be roll-backed")

    djAppC = DjangoApplicationCreator(kwargs['application'])
    djAppC.rollback()


@receiver(application_removed_signal)
def removeApplication(sender, **kwargs):
    logger.warning("Application removing process started")

    djAppC = DjangoApplicationRemover(kwargs['application'])
    djAppC.removeApp()


@receiver(model_changed_signal)
def dump_all_app_data(sender, **kwargs):
    logger.info("Dumping all application data")
