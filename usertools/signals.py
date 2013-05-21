###############################################################################
## Imports
###############################################################################
# Django
from django.dispatch import Signal


###############################################################################
## Signals
###############################################################################
verification_complete = Signal(providing_args=["instance", ])
confirmation_complete = Signal(providing_args=["instance", "old_email"])
