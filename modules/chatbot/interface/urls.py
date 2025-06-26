from django.urls import path
from .views.views import *

urlpatterns = [
    path("chat/completions/", ChatCompletionView.as_view(), name="chat-completions"),
    path("sessions/", ChatSessionListView.as_view(), name="session-list"),
    path("sessions/<int:pk>/title/", ChatSessionUpdateTitleView.as_view(), name="session-update-title"),
    path("sessions/<int:pk>/", ChatSessionDeleteView.as_view(), name="session-delete"),
    path("sessions/<int:session_id>/messages/", ChatMessageListView.as_view(), name="message-list"),
]