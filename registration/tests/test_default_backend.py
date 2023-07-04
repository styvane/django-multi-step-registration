import datetime
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.db import DatabaseError
from django.test import TransactionTestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationForm
from registration.models import RegistrationProfile

User = get_user_model()


@override_settings(ROOT_URLCONF="test_app.urls_default")
class DefaultBackendViewTests(TransactionTestCase):
    """
    Test the default registration backend.

    Running these tests successfully will require two templates to be
    created for the sending of activation emails; details on these
    templates and their contexts may be found in the documentation for
    the default backend.

    """

    registration_profile = RegistrationProfile

    registration_view = RegistrationView

    @override_settings(REGISTRATION_OPEN=True)
    def test_registration_open(self):
        """
        The setting ``REGISTRATION_OPEN`` appropriately controls
        whether registration is permitted.

        """
        resp = self.client.get(reverse("registration_register"))
        assert 200 == resp.status_code

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
        assert 200 == resp.status_code
        self.assertTemplateUsed(resp, "registration/registration_form.html")
        assert isinstance(resp.context["form"], RegistrationForm)

    def test_registration(self):
        """
        Registration creates a new inactive account and a new profile
        with activation key, populates the correct account data and
        sends an activation email.

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
        self.assertRedirects(resp, reverse("registration_complete"))

        new_user = User.objects.get(username="bob")

        assert new_user.check_password("secret")
        assert "bob@example.com" == new_user.email

        # New user must not be active.
        assert not new_user.is_active

        # A registration profile was created, and an activation email
        # was sent.
        assert 1 == self.registration_profile.objects.count()
        assert 1 == len(mail.outbox)

    def test_registration_no_email(self):
        """
        Overridden Registration view does not send an activation email if the
        associated class variable is set to ``False``

        """

        class RegistrationNoEmailView(self.registration_view):
            SEND_ACTIVATION_EMAIL = False

        request_factory = RequestFactory()
        view = RegistrationNoEmailView.as_view()
        request = request_factory.post(
            "/",
            data={
                "user-username": "bob",
                "user-email": "bob@example.com",
                "user-password1": "secret",
                "user-password2": "secret",
                "registration_no_email_view-current_step": "user",
            },
        )
        request.user = AnonymousUser()

        def dummy_get_response(request):  # pragma: no cover
            return None

        middleware = SessionMiddleware(dummy_get_response)
        middleware.process_request(request)
        view(request)

        User.objects.get(username="bob")
        # A registration profile was created, and no activation email was sent.
        assert 1 == self.registration_profile.objects.count()
        assert 0 == len(mail.outbox)
        assert "bob@example.com" == request.session.get("registration_email")

    @override_settings(
        INSTALLED_APPS=(
            "django.contrib.auth",
            "formtools",
            "registration",
        )
    )
    def test_registration_no_sites(self):
        """
        Registration still functions properly when
        ``django.contrib.sites`` is not installed; the fallback will
        be a ``RequestSite`` instance.

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
        assert 302 == resp.status_code

        new_user = User.objects.get(username="bob")

        assert new_user.check_password("secret")
        assert "bob@example.com" == new_user.email
        assert not new_user.is_active

        assert 1 == self.registration_profile.objects.count()
        assert 1 == len(mail.outbox)

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
        self.assertEqual(0, len(mail.outbox))

    @patch("registration.models.RegistrationManager.create_inactive_user")
    def test_registration_exception(self, create_inactive_user):
        """
        User is not created beforehand if an exception occurred at
        creating registration profile.
        """
        create_inactive_user.side_effect = DatabaseError()
        valid_data = {
            "user-username": "bob",
            "user-email": "bob@example.com",
            "user-password1": "secret",
            "user-password2": "secret",
            "registration_view-current_step": "user",
        }
        with self.assertRaises(DatabaseError):
            self.client.post(reverse("registration_register"), data=valid_data)
        assert not User.objects.filter(username="bob").exists()

    def test_activation(self):
        """
        Activation of an account functions properly.

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

        profile = self.registration_profile.objects.get(user__username="bob")

        resp = self.client.get(
            reverse(
                "registration_activate",
                args=(),
                kwargs={"activation_key": profile.activation_key},
            )
        )
        self.assertRedirects(resp, reverse("registration_activation_complete"))

    def test_activation_expired(self):
        """
        An expired account can't be activated.

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

        profile = self.registration_profile.objects.get(user__username="bob")
        user = profile.user
        user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        user.save()

        resp = self.client.get(
            reverse(
                "registration_activate",
                args=(),
                kwargs={"activation_key": profile.activation_key},
            )
        )

        assert 200 == resp.status_code
        self.assertTemplateUsed(resp, "registration/activate.html")
        user = User.objects.get(username="bob")
        assert not user.is_active

    def test_resend_activation(self):
        """
        Resend activation functions properly.

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

        profile = self.registration_profile.objects.get(user__username="bob")

        resp = self.client.post(
            reverse("registration_resend_activation"),
            data={"email": profile.user.email},
        )
        self.assertTemplateUsed(resp, "registration/resend_activation_complete.html")
        assert resp.context["email"] == profile.user.email

    def test_resend_activation_invalid_email(self):
        """
        Calling resend with an invalid email shows the same template.

        """
        resp = self.client.post(
            reverse("registration_resend_activation"),
            data={"email": "invalid@example.com"},
        )
        self.assertTemplateUsed(resp, "registration/resend_activation_complete.html")
