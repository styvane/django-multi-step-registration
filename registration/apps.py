from django.apps import AppConfig


class RegistrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "Django-multi-registration provides multi-step user registration"
    "functionality for Django websites."
    name = "registration"
