import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learning_chatbot.settings")

app = Celery("chatbot")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()