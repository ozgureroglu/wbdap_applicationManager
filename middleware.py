from django.contrib.auth.views import redirect_to_login

class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.


        if request.path.startswith('/applicationManager/'):
            if not request.user.is_superuser:
                return redirect_to_login(request.path)
            # Continue processing the request as usual:



        response = self.get_response(request)

        print('after view')

        # Code to be executed for each request/response after
        # the view is called.

        return response
