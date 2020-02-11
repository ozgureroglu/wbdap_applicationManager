from django_rq import job
import os


from applicationManager.util.django_application_creator import DjangoApplicationCreator


@job
def addrq(x, y):
    print(os.getcwd())
    return x+y


addrq.delay()


@job
def create_app(app):
    print("Create app method starting")
    creator = DjangoApplicationCreator(app)
    try:
        creator.create()
    except Exception as e:
        print(e)
    return True


create_app.delay()
