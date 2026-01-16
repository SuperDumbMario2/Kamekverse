from django.apps import AppConfig


class KamekverseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kamekverse'

    def ready(self):
        import kamekverse.signals