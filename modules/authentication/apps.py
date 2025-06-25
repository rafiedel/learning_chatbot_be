from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.authentication"   # full dotted path
    label = "authentication"          # must match the folder’s slug