from django.contrib.admin import helpers
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from registration.models import RegistrationProfile

User = get_user_model()


@override_settings(
    REGISTRATION_DEFAULT_FROM_EMAIL="registration@email.com",
    REGISTRATION_EMAIL_HTML=True,
    DEFAULT_FROM_EMAIL="django@email.com",
)
class AdminCustomActionsTestCase(TestCase):
    """
    Test the available admin custom actions
    """

    def setUp(self):
        admin_user = User.objects.create_superuser("admin", "admin@test.com", "admin")
        self.client.login(username=admin_user.get_username(), password=admin_user)

        self.user_info = {
            "username": "alice",
            "password": "swordfish",
            "email": "alice@example.com",
        }

    def test_activate_users(self):
        """
        Test the admin custom command 'activate users'

        """
        new_user = User.objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)

        assert not profile.activated

        registrationprofile_list = reverse(
            "admin:registration_registrationprofile_changelist"
        )
        post_data = {
            "action": "activate_users",
            helpers.ACTION_CHECKBOX_NAME: [profile.pk],
        }
        self.client.post(registrationprofile_list, post_data, follow=True)

        profile = RegistrationProfile.objects.get(user=new_user)
        assert profile.activated

    def test_resend_activation_email(self):
        """
        Test the admin custom command 'resend activation email'
        """
        new_user = User.objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)

        registrationprofile_list = reverse(
            "admin:registration_registrationprofile_changelist"
        )
        post_data = {
            "action": "resend_activation_email",
            helpers.ACTION_CHECKBOX_NAME: [profile.pk],
        }
        self.client.post(registrationprofile_list, post_data, follow=True)

        assert 1 == len(mail.outbox)
        assert mail.outbox[0].to == [self.user_info["email"]]
