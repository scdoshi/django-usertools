###############################################################################
## Imports
###############################################################################
# Djangi
from django.conf.urls import url, patterns

# User
from usertools import views as usertools_views


###############################################################################
## URL Patterns
###############################################################################
urlpatterns = patterns('',
    url(r'^verify-email/(?P<verification_key>\w+)/$',
        usertools_views.EmailVerify.as_view(), name='usertools-verify'),

    url(r'^confirm-email/(?P<confirmation_key>\w+)/$',
        usertools_views.email_confirm,
        {'success_url': 'email_confirm_complete',
        'template_name': 'desktop/pages/email_confirm_fail.html',
        'extra_context': {'layout': layout}},
        name='usertools-email-confirm'),
)
