from django.apps import AppConfig


# Class representing BusinessMetaConfig
class BusinessMetaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'business_meta'
    verbose_name = 'Business & schema metadata'
