###############################################################################
## Imports
###############################################################################
# Django
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.conf import settings
from django.contrib import messages
from django.views.decorators.cache import never_cache

# User
from usertools.models import UserTools
from usertools.utils import class_view_decorator


###############################################################################
## Views
###############################################################################
@class_view_decorator(never_cache)
class EmailVerify(View):
    redirect_success = getattr(settings, 'LOGIN_REDIRECT_URL', '')
    redirect_failure = getattr(settings, 'LOGIN_URL', '')

    def get(self, request, verification_key=None, *args, **kwargs):
        # Logout any signedin user.
        if request.user.is_authenticated():
            logout(request)

        usertools = UserTools.objects.verify_email(verification_key)
        if usertools:
            # If Already Activated
            if not isinstance(usertools, UserTools):
                messages.info(request,
                    'Your account has already been verified. Please login to continue.')
                return redirect(self.redirect_failure)

            # Else: Sign the user in.
            auth_user = authenticate(identification=usertools.user.username,
                                     check_password=False)
            login(request, auth_user)

            messages.info(request,
                'Your email has been verified.')

            return redirect(self.redirect_success)

        messages.error(request,
            'The verification link is invalid or has expired.')
        return redirect(self.redirect_failure)


@class_view_decorator(never_cache)
class EmailConfirm(View):
    redirect_success = getattr(settings, 'LOGIN_REDIRECT_URL', '')
    redirect_failure = getattr(settings, 'LOGIN_URL', '')

    def get(self, request, confirmation_key=None, *args, **kwargs):
        # Logout any signedin user.
        if request.user.is_authenticated():
            logout(request)

        user = UserTools.objects.confirm_email(confirmation_key)
        if user:
            messages.success(request, 'Your email address has been changed.',
                fail_silently=True)

            return redirect(self.redirect_success)

        else:
            messages.error(request,
                'The confirmation link is invalid.')
            return redirect(self.redirect_failure)
