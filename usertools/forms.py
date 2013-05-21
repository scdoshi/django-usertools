###############################################################################
## Imports
###############################################################################
# Django
from django import forms
from django.contrib.auth.models import User


###############################################################################
## Forms
###############################################################################
class ChangeEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs=dict(maxlength=75)),
        label='New email')

    def __init__(self, user, *args, **kwargs):
        """
        The current ``user`` is needed for initialisation of this form so
        that we can check if the email address is still free and not always
        returning ``True`` for this query because it's the users own e-mail
        address.
        """
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        if not isinstance(user, User):
            raise TypeError("user must be an instance of User")
        else:
            self.user = user

    def clean_email(self):
        """
        Validate that the email is not already registered with another user
        """
        if self.cleaned_data['email'].lower() == self.user.email:
            raise forms.ValidationError('This is already your email address.')
        if User.objects.filter(email__iexact=self.cleaned_data['email'])\
            .exclude(email__iexact=self.user.email):
            raise forms.ValidationError('This email address is already in use.')
        return self.cleaned_data['email']

    def save(self):
        """
        Save method calls :func:`user.change_email()` method which sends out an
        email with an verification key to verify and with it enable this new
        email address.
        """
        return self.user.usertools.change_email(self.cleaned_data['email'])
