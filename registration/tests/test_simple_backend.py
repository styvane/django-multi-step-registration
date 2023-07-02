from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse


from registration.forms import RegistrationForm

User = get_user_model()


@override_settings(ROOT_URLCONF="test_app.urls_simple")
class SimpleBackendViewTests(TestCase):
    @override_settings(REGISTRATION_OPEN=True)
    def test_registration_open(self):
        """
        The setting ``REGISTRATION_OPEN`` appropriately controls
        whether registration is permitted.

        """
        resp = self.client.get(reverse("registration_register"))
        self.assertEqual(200, resp.status_code)

    @override_settings(REGISTRATION_OPEN=False)
    def test_registration_closed(self):
        # Now all attempts to hit the register view should redirect to
        # the 'registration is closed' message.
        resp = self.client.get(reverse("registration_register"))
        self.assertRedirects(resp, reverse("registration_disallowed"))

        resp = self.client.post(
            reverse("registration_register"),
            data={
                "user-username": "bob",
                "user-email": "bob@example.com",
                "user-password1": "secret",
                "user-password2": "secret",
                "registration_view-current_step": "user",
            },
        )
        self.assertRedirects(resp, reverse("registration_disallowed"))

    def test_registration_get(self):
        """
        HTTP ``GET`` to the registration view uses the appropriate
        template and populates a registration form into the context.

        """
        resp = self.client.get(reverse("registration_register"))
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, "registration/registration_form.html")
        self.assertIsInstance(resp.context["form"], RegistrationForm)

    def test_registration(self):
        """
        Registration creates a new account and logs the user in.

        """
        resp = self.client.post(
            reverse("registration_register"),
            data={
                "user-username": "bob",
                "user-email": "bob@example.com",
                "user-password1": "secret",
                "user-password2": "secret",
                "registration_view-current_step": "user",
            },
        )

        self.assertEqual(302, resp.status_code)
        new_user = User.objects.get(username="bob")

        self.assertIn(
            getattr(settings, "SIMPLE_BACKEND_REDIRECT_URL", "/"), resp["Location"]
        )

        self.assertTrue(new_user.check_password("secret"))
        self.assertEqual(new_user.email, "bob@example.com")

        # New user must be active.
        self.assertTrue(new_user.is_active)

        # New user must be logged in.
        resp = self.client.get(reverse("registration_register"), follow=True)
        self.assertTrue(resp.context["user"].is_authenticated)

    def test_registration_failure(self):
        """
        Registering with invalid data fails.

        """
        resp = self.client.post(
            reverse("registration_register"),
            data={
                "user-username": "bob",
                "user-email": "bob@example.com",
                "user-password1": "secret",
                "user-password2": "notsecret",
                "registration_view-current_step": "user",
            },
        )
        self.assertEqual(200, resp.status_code)
        self.assertFalse(resp.context["form"].is_valid())
