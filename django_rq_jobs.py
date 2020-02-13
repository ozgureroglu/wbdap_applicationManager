import os
from django_rq import job
from applicationManager.util.django_application_creator import DjangoApplicationCreator


@job(func_or_queue='default',failure_ttl=60)
def addrq(x, y):
    print(os.getcwd())
    return x+y


addrq.delay()


@job(func_or_queue='default',failure_ttl=60)
def create_app(app):
    print("Create app method starting")
    creator = DjangoApplicationCreator(app)
    try:
        creator.create()
        return True
    except Exception as e:
        return e



create_app.delay()
