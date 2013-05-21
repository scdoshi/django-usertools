###############################################################################
## Imports
###############################################################################
# Django
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


###############################################################################
## App Settings
###############################################################################
VERIFICATION_REQUIRED = getattr(settings,
    'USERTOOLS_VERIFICATION_REQUIRED', True)
VERIFICATION_DAYS = getattr(settings, 'USERTOOLS_VERIFICATION_DAYS', 7)
VERIFICATION_NOTIFY = getattr(settings, 'USERTOOLS_VERIFICATION_NOTIFY', True)
VERIFICATION_NOTIFY_DAYS = getattr(settings,
    'USERTOOLS_VERIFICATION_NOTIFY_DAYS', 5)

USE_HTTPS = getattr(settings, 'USERTOOLS_USE_HTTPS', True)
