from applicationManager.util.django_application_creator import DjangoApplicationCreator


def addrq(x,y):
    # print("The output is: ", x + y)
    return x+y


def create_app(app):
    print("The output is: %s"% app.description)
    creator = DjangoApplicationCreator(app)
    creator.create()