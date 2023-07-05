"""
Views which allow users to create and activate accounts.

"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView
from django.views.generic import TemplateView
from formtools.wizard.views import SessionWizardView

from .forms import ResendActivationForm

REGISTRATION_FORM_PATH = getattr(
    settings, "REGISTRATION_FORM", "registration.forms.RegistrationForm"
)
REGISTRATION_FORM = import_string(REGISTRATION_FORM_PATH)
ACCOUNT_AUTHENTICATED_REGISTRATION_REDIRECTS = getattr(
    settings, "ACCOUNT_AUTHENTICATED_REGISTRATION_REDIRECTS", True
)

WizardView = getattr(settings, "REGISTRATION_WIZARDVIEW", SessionWizardView)


class BaseRegistrationView(WizardView):
    """
    Base class for user registration views.
    """

    disallowed_url = "registration_disallowed"
    form_list = [("user", REGISTRATION_FORM)]
    user_form_step = "user"
    http_method_names = ["get", "post", "head", "options", "trace"]
    success_url = None
    template_name = "registration/registration_form.html"

    @method_decorator(sensitive_post_parameters("password1", "password2"))
    def dispatch(self, request, *args, **kwargs):
        """
        Check that user signup is allowed and if user is logged in before even bothering to
        dispatch or do other processing.

        """

        if ACCOUNT_AUTHENTICATED_REGISTRATION_REDIRECTS:
            if self.request.user.is_authenticated:
                if settings.LOGIN_REDIRECT_URL is not None:
                    return redirect(settings.LOGIN_REDIRECT_URL)
                else:
                    raise Exception(
                        (
                            "You must set a URL with LOGIN_REDIRECT_URL in "
                            "settings.py or set "
                            "ACCOUNT_AUTHENTICATED_REGISTRATION_REDIRECTS=False"
                        )
                    )

        if not self.registration_allowed():
            return redirect(self.disallowed_url)

        return super().dispatch(request, *args, **kwargs)

    def done(self, form_list, form_dict, **kwargs):
        user_form = form_dict.get(self.user_form_step)
        if user_form is None:
            raise Exception(
                "Invalid 'user_form_step' name. Please set the correct user_form_step_name"
            )

        new_user = self.register(user_form)

        success_url = self.get_success_url(new_user)

        if hasattr(self.request, "session"):
            self.request.session["registration_email"] = user_form.cleaned_data["email"]

        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
        except ValueError:
            return redirect(success_url)
        else:
            return redirect(to, *args, **kwargs)

    def registration_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.

        """
        return True

    def register(self, form):
        """
        Implement user-registration logic here.

        """
        raise NotImplementedError

    def get_success_url(self, user=None):
        """
        Return the URL to redirect to after processing a valid form.
        Use the new user when constructing success_url.
        """
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)  # success_url may be lazy


class BaseActivationView(TemplateView):
    """
    Base class for user activation views.

    """

    http_method_names = ["get"]
    template_name = "registration/activate.html"

    def get(self, request, *args, **kwargs):
        activated_user = self.activate(*args, **kwargs)
        if activated_user:
            success_url = self.get_success_url(activated_user)
            try:
                to, args, kwargs = success_url
            except ValueError:
                return redirect(success_url)
            else:
                return redirect(to, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def activate(self, *args, **kwargs):
        """
        Implement account-activation logic here.

        """
        raise NotImplementedError

    def get_success_url(self, user):
        raise NotImplementedError


class BaseResendActivationView(FormView):
    """
    Base class for resending activation views.
    """

    form_class = ResendActivationForm
    template_name = "registration/resend_activation_form.html"

    def form_valid(self, form):
        """
        Regardless if resend_activation is successful, display the same
        confirmation template.

        """
        self.resend_activation(form)
        return self.render_form_submitted_template(form)

    def resend_activation(self, form):
        """
        Implement resend activation key logic here.
        """
        raise NotImplementedError

    def render_form_submitted_template(self, form):
        """
        Implement rendering of confirmation template here.

        """
        raise NotImplementedError


class BaseApprovalView(TemplateView):
    http_method_names = ["get"]
    template_name = "registration/admin_approve.html"

    def get(self, request, *args, **kwargs):
        approved_user = self.approve(*args, **kwargs)
        if approved_user:
            success_url = self.get_success_url(approved_user)
            try:
                to, args, kwargs = success_url
            except ValueError:
                return redirect(success_url)
            else:
                return redirect(to, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def approve(self, *args, **kwargs):
        """
        Implement admin-approval logic here.

        """
        raise NotImplementedError

    def get_success_url(self, user):
        raise NotImplementedError
