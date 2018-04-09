from applicationManager.signals import application_created, application_creation_failed, application_removed, \
    model_changed

__author__ = 'ozgur'

import logging

from django.dispatch import receiver

from applicationManager.util.django_application_creator import DjangoApplicationCreator
from applicationManager.util.django_application_remover import DjangoApplicationRemover

logger= logging.getLogger("wbdap.debug")


# Called when he application is created
@receiver(application_created)
def my_callback(sender, **kwargs):
    logger.info("application_created signal receieved")
    djAppC = DjangoApplicationCreator(kwargs['application'])

    djAppC.create_application()


@receiver(application_creation_failed)
def rollback_setup(sender, **kwargs):
    logger.warning("Application creating steps will be roll-backed")

    djAppC = DjangoApplicationCreator(kwargs['application'])
    djAppC.rollback()


@receiver(application_removed)
def removeApplication(sender, **kwargs):
    logger.warning("Application removing process started")

    djAppC = DjangoApplicationRemover(kwargs['application'])
    djAppC.removeApp()


@receiver(model_changed)
def dump_all_app_data(sender,**kwargs):
    logger.info("Dumping all application data")


