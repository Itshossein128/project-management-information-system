from django.apps import AppConfig


class AlertsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alerts'

    def ready(self):
        import alerts.signals  # noqa: F401
        import alerts.services.checkers  # noqa: F401, register checkers
