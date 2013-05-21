###############################################################################
## Imports
###############################################################################
# Python
import hashlib
import random

# Django
from django.conf import settings
from django.contrib.auth.models import SiteProfileNotAvailable
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model
from django.utils.decorators import method_decorator
from django.utils.timezone import now


###############################################################################
## Utils
###############################################################################
def get_profile_model():
    """
    Return the model class for the currently-active user profile
    model, as defined by the ``AUTH_PROFILE_MODULE`` setting.

    This is valid for django <= 1.4.x
    """
    if (not hasattr(settings, 'AUTH_PROFILE_MODULE')) or \
           (not settings.AUTH_PROFILE_MODULE):
        raise SiteProfileNotAvailable

    profile_mod = get_model(*settings.AUTH_PROFILE_MODULE.split('.'))
    if profile_mod is None:
        raise SiteProfileNotAvailable
    return profile_mod


def get_user_model():
    """
    Return the User model that is active in this project.

    For django > 1.5, use ``AUTH_USER_MODEL`` setting,
    otherwise default to `auth.User`
    """

    AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

    try:
        app_label, model_name = AUTH_USER_MODEL.split('.')
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    user_model = get_model(app_label, model_name)

    return user_model


def generate_hash(user):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    username = user.username
    if isinstance(username, unicode):
        username = username.encode('utf-8')

    return hashlib.sha1("%s%s%s" % (now(),
        salt, username)).hexdigest()


###############################################################################
## Decorators
###############################################################################
def class_view_decorator(function_decorator):
    """Convert a function based decorator into a class based decorator usable
    on class based Views.

    Can't subclass the `View` as it breaks inheritance (super in particular),
    so we monkey-patch instead.
    """

    def simple_decorator(View):
        View.dispatch = method_decorator(function_decorator)(View.dispatch)
        return View

    return simple_decorator
