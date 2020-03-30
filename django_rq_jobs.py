import os
from django_rq import job
from applicationManager.util.django_application_creator import DjangoApplicationCreator
from applicationManager.util.django_project_generator import DjangoProjectGenerator


@job(func_or_queue='default', failure_ttl=20)
def addrq(x, y):
    print(os.getcwd())
    return x+y


addrq.delay()

# Job nesnesi icin alinabilecek parametreler icin RQ dokumanlarina bak.
@job(func_or_queue='default', failure_ttl=20)
def create_app(app):
    """Method will either return True or False. It will not propagate the exceptions for now """
    creator = DjangoApplicationCreator(app)
    try:
        creator.create()
        return True
    except Exception as e:
        # TODO : Change what you do depending on the exception
        # I am receving different exceptions here
        return False


create_app.delay()



# Job nesnesi icin alinabilecek parametreler icin RQ dokumanlarina bak.
@job(func_or_queue='default', failure_ttl=20)
def create_project(project):
    """Method will either return True or False. It will not propagate the exceptions for now """
    generator = DjangoProjectGenerator(project)
    try:
        generator.create()
        return True
    except Exception as e:
        # TODO : Change what you do depending on the exception
        # I am receving different exceptions here
        return False


create_app.delay()

