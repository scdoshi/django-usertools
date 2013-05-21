###############################################################################
## Imports
###############################################################################
# Python
from datetime import timedelta

# Django
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.utils.timezone import now

# User
from usertools import settings as usertools_settings
from usertools.managers import UserToolsManager
from usertools.utils import generate_hash, get_user_model


###############################################################################
## Code
###############################################################################
USER_MODEL = get_user_model()


###############################################################################
## Models
###############################################################################
class BaseProfile(models.Model):
    class Meta:
        abstract = True
        permissions = (
            ('view_profile', 'Can view profile'),
        )


class UserTools(models.Model):
    user = models.OneToOneField(USER_MODEL)
    verification_key = models.CharField(max_length=40, null=True,
        blank=True)
    verified = models.BooleanField(default=False)
    email_unconfirmed = models.EmailField('unconfirmed email address',
        null=True, blank=True,
        help_text='Temporary email address when the user requests an email change.')
    email_confirmation_key = models.CharField(
        'unconfirmed email verification key',
        max_length=40, blank=True)
    email_confirmation_key_created = models.DateTimeField(
        'creation date of email confirmation key',
        null=True, blank=True)
    objects = UserToolsManager()

    class Meta:
        verbose_name = "User Tools"
        verbose_name_plural = "User Tools"

    def __unicode__(self):
        return '%s' % self.user

    def change_email(self, email):
        """
        Changes the email address for a user.

        A user needs to verify this new email address before it becomes
        active. By storing the new email address in a temporary field --
        ``temporary_email`` -- we are able to set this email address after the
        user has verified it by clicking on the verification URI in the email.
        This email gets send out by ``send_verification_email``.

        :param email:
            The new email address that the user wants to use.

        """
        self.email_unconfirmed = email

        self.email_confirmation_key = generate_hash(self.user)
        self.email_confirmation_key_created = now()
        self.save()

        # Send email for confirmation
        self.send_confirmation_email()

    def send_confirmation_email(self):
        """
        Sends an email to confirm the new email address.

        This method sends out two emails. One to the new email address that
        contains the ``email_confirmation_key`` which is used to verify this
        this email address.

        The other email is to the old email address to let the user know that
        a request is made to change this email address.

        """
        context = {'user': self.user,
                  'new_email': self.email_unconfirmed,
                  'https': usertools_settings.USE_HTTPS,
                  'confirmation_key': self.email_confirmation_key,
                  'site': Site.objects.get_current()}

        # Email to the old address
        subject_old = render_to_string('usertools/confirmation_email_subject_old.txt',
            context)
        subject_old = ''.join(subject_old.splitlines())
        message_old = render_to_string('usertools/confirmation_email_message_old.txt',
            context)

        send_mail(subject_old, message_old, settings.DEFAULT_FROM_EMAIL,
            [self.user.email])

        # Email to the new address
        subject_new = render_to_string('usertools/confirmation_email_subject_new.txt',
            context)
        subject_new = ''.join(subject_new.splitlines())
        message_new = render_to_string('usertools/confirmation_email_message_new.txt',
            context)

        send_mail(subject_new, message_new, settings.DEFAULT_FROM_EMAIL,
            [self.email_unconfirmed])

    def verification_key_expired(self):
        """
        Checks if verification key is expired.

        Returns ``True`` when the ``verification_key`` of the user is expired
        and ``False`` if the key is still valid.

        The key is expired when it is not used for the
        number of days in ``VERIFICATION_DAYS``.
        """
        expiration_days = timedelta(days=usertools_settings.VERIFICATION_DAYS)
        expiration_date = self.user.date_joined + expiration_days
        if now() >= expiration_date:
            return True
        return False

    def send_verification_email(self):
        """
        Sends a verification email to the user.

        This email is sent when the user wants to verify the email
        address on a new account.
        """
        context = {'user': self.user,
                  'https': usertools_settings.USE_HTTPS,
                  'verification_days': usertools_settings.VERIFICATION_DAYS,
                  'verification_key': self.verification_key,
                  'site': Site.objects.get_current()}

        subject = render_to_string('usertools/verification_email_subject.txt',
            context)
        subject = ''.join(subject.splitlines())
        message = render_to_string('usertools/verification_email_message.txt',
            context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
            [self.user.email])
