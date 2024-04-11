from django.apps import AppConfig


class BannersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'banners'

    def ready(self):
        import banners.signals
