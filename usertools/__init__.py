###############################################################################
## Django User Tools
###############################################################################
"""
Django User Tools adds common features to use with contib.auth:
- Authentication backend that works with both email and username
- Email Verification
- Email address change with confirmation
- Per objects permissions for User and Profile models
"""
VERSION = (0, 1, 0)

__version__ = '.'.join((str(each) for each in VERSION[:3]))


def get_version():
    """
    Returns string with digit parts only as version.
    """
    return __version__
