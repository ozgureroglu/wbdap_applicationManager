class StageException(Exception):
    def __init___(self, error_arguments):
        Exception.__init__(self, "An exception occured in the stage with arguments {0}".format(error_arguments))
        self.dErrorArguments = error_arguments

class UrlPyCreationException(StageException):
    def __init___(self, error_arguments):
        Exception.__init__(self, "Url.py file creating failed with arguments {0}".format(error_arguments))
        self.dErrorArguments = error_arguments



class SiteRootNotSetException(Exception):
    def __init___(self, error_arguments):
        Exception.__init__(self, "Either settings.SCAFFOLDS_APPS_DIR or site_root not set")
        self.dErrorArguments = error_arguments


class ApplicationFolderExistsException(Exception):
    def __init___(self, error_arguments):
        Exception.__init__(self, "The application folder already exits in the project directory")
        self.dErrorArguments = error_arguments


class ManagePyStartAppException(Exception):
    def __init___(self, error_arguments):
        Exception.__init__(self, "Manage.py was unsuccessful to create the django application")
        self.dErrorArguments = error_arguments