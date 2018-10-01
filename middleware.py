from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render, redirect
import logging
logger = logging.getLogger("wbdap.debug")

class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.


        if request.path.startswith('/applicationManager/'):
            if not request.user.is_superuser:
                # return redirect_to_login(request.path)
                logger.info(self.__class__.__name__+ ' redirecting request to logging')
                return redirect('login')
            # Continue processing the request as usual:



        # this is the seperation point between req and resp
        response = self.get_response(request)


        # Code to be executed for each request/response after
        # the view is called.
        print('after view')

        return response
