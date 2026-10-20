from django.apps import AppConfig


class PartnershipsConfig(AppConfig):
    name = 'partnerships'

    def ready(self):
        from . import signals  # noqa: F401
