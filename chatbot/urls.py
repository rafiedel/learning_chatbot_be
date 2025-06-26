from django.urls import path
from .views import (
    ChatCompletionView,
    ChatSessionListView,
    ChatSessionRenameView,
    ChatSessionDeleteView,
    ChatMessageListView,
)

urlpatterns = [
    path("completions/", ChatCompletionView.as_view(), name="chat-completion"),
    path("sessions/", ChatSessionListView.as_view(), name="chat-session-list"),
    path("sessions/<int:session_id>/title/", ChatSessionRenameView.as_view(), name="chat-session-rename"),
    path("sessions/<int:session_id>/", ChatSessionDeleteView.as_view(), name="chat-session-delete"),
    path("messages/", ChatMessageListView.as_view(), name="chat-message-list"),
]
