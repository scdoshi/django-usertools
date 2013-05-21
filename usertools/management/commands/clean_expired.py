###############################################################################
## Import Django
###############################################################################
from django.core.management.base import NoArgsCommand


###############################################################################
## Inport User
###############################################################################
from usertools.models import UserTools


###############################################################################
## Command
###############################################################################
class Command(NoArgsCommand):
    """
    Search for users that still haven't verified their email after
    ``VERIFICATION_DAYS`` and delete them.

    """
    help = 'Deletes expired users.'

    def handle_noargs(self, **options):
        UserTools.objects.delete_expired_users()
