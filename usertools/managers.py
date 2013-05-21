###############################################################################
## Imports
###############################################################################
# Python
import re

# Django
from django.contrib.auth.models import (User, Permission)
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models

# External
from guardian.shortcuts import assign, get_perms

# User
from usertools.utils import get_profile_model, generate_hash
from usertools import signals as usertools_signals


###############################################################################
## Code
###############################################################################
SHA1_RE = re.compile('^[a-f0-9]{40}$')

ASSIGNED_PERMISSIONS = {
    'profile': (
        ('view_profile', 'Can view profile'),
        ('change_profile', 'Can change profile'),
    ),
    'user': (
        ('change_user', 'Can change user'),
    )
}


###############################################################################
## Managers
###############################################################################
class UserToolsManager(models.Manager):
    def create_user(self, username, email, password, active=False,
                    send_email=True):
        """
        A simple wrapper that creates a new :class:`User`.

        :param username:
            String containing the username of the new user.

        :param email:
            String containing the email address of the new user.

        :param password:
            String containing the password for the new user.

        :param active:
            Boolean that defines what the active field on the user object
            should be. Defaults to ``False``.

        :param send_email:
            Boolean that defines if the user should be send an email. You could
            set this to ``False`` when you want to create a user in your own
            code, but don't want the user to verify through email.

        :return: :class:`User` instance representing the new user.
        """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = active
        new_user.save()

        usertools = self.create_usertools(new_user)

        # All users have an empty profile
        profile_model = get_profile_model()
        try:
            new_profile = new_user.get_profile()
        except profile_model.DoesNotExist:
            new_profile = profile_model(user=new_user)
            new_profile.save()

        # Give permissions to view and change profile
        for perm in ASSIGNED_PERMISSIONS['profile']:
            assign(perm[0], new_user, new_profile)

        # Give permissions to view and change itself
        for perm in ASSIGNED_PERMISSIONS['user']:
            assign(perm[0], new_user, new_user)

        if send_email:
            usertools.send_verification_email()

        return new_user

    def create_usertools(self, user):
        """
        Creates an :class:`UserTools` instance for this user.

        :param user:
            Django :class:`User` instance.

        :return: The newly created :class:`UserTools` instance.

        """
        verification_key = generate_hash(user)
        return self.create(user=user, verification_key=verification_key)

    def verify_email(self, verification_key):
        """
        Verify an email address by supplying a valid ``verification_key``.

        If the key is valid and a user is found, verifies the email address and
        returns the usertools object. Also sends the ``verification_complete``
        signal.

        :param verification_key:
            String containing the secret SHA1 for a valid verification.

        :return:
            The ``UserTools`` instance if found, ``True`` found but already
            verified and ``False`` if not found.

        """
        if SHA1_RE.search(verification_key):
            try:
                usertools = self.get(verification_key=verification_key)
            except self.model.DoesNotExist:
                return False

            if (not usertools.verified
                    and not usertools.verification_key_expired()):
                usertools.verified = True
                usertools.save()

                # Send the verification_complete signal
                usertools_signals.verification_complete.send(sender=None,
                    instance=usertools)
                return usertools
            return True
        return False

    def confirm_email(self, confirmation_key):
        """
        Confirm an email address by checking a ``confirmation_key``.

        A valid ``confirmation_key`` will set the newly wanted e-mail
        address as the current e-mail address. Returns the user after
        success or ``False`` when the confirmation key is
        invalid. Also sends the ``confirmation_complete`` signal.

        :param confirmation_key:
            String containing the secret SHA1 that is used for verification.

        :return:
            The verified :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(confirmation_key):
            try:
                usertools = self.get(email_confirmation_key=confirmation_key,
                                   email_unconfirmed__isnull=False)
            except self.model.DoesNotExist:
                return False
            else:
                user = usertools.user
                old_email = user.email
                user.email = usertools.email_unconfirmed
                usertools.email_unconfirmed, usertools.email_confirmation_key = '', ''
                usertools.save()
                user.save()

                # Send the confirmation_complete signal
                usertools_signals.confirmation_complete.send(sender=None,
                    instance=usertools, old_email=old_email)

                return user
        return False

    def delete_expired_users(self):
        """
        Checks for expired users and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        :return: A list containing the deleted users.

        """
        deleted_users = []
        for user in User.objects.filter(is_staff=False):
            if (not user.usertools.verified
                    and user.usertools.verification_key_expired()):
                deleted_users.append(user)
                user.delete()
        return deleted_users

    def check_permissions(self):
        """
        Checks that all permissions are set correctly for the users.

        :return: A set of users whose permissions was wrong.
        """
        # Variable to supply some feedback
        changed_permissions = []
        changed_users = []
        warnings = []

        # Check that all the permissions are available.
        for model, perms in ASSIGNED_PERMISSIONS.items():
            if model == 'profile':
                model_obj = get_profile_model()
            else:
                model_obj = User
            model_content_type = ContentType.objects.get_for_model(model_obj)
            for perm in perms:
                try:
                    Permission.objects.get(codename=perm[0],
                                           content_type=model_content_type)
                except Permission.DoesNotExist:
                    changed_permissions.append(perm[1])
                    Permission.objects.create(name=perm[1],
                                              codename=perm[0],
                                              content_type=model_content_type)

        # it is safe to rely on settings.ANONYMOUS_USER_ID since it is a
        # requirement of django-guardian
        for user in User.objects.exclude(id=settings.ANONYMOUS_USER_ID):
            try:
                user_profile = user.get_profile()
            except get_profile_model().DoesNotExist:
                warnings.append('No profile found for %s' % user)
            else:
                all_permissions = (get_perms(user, user_profile)
                    + get_perms(user, user))

                for model, perms in ASSIGNED_PERMISSIONS.items():
                    if model == 'profile':
                        perm_object = user.get_profile()
                    else:
                        perm_object = user

                    for perm in perms:
                        if perm[0] not in all_permissions:
                            assign(perm[0], user, perm_object)
                            changed_users.append(user)

        return (changed_permissions, changed_users, warnings)
