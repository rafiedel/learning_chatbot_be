from django.db import models
from django.db import models
from django.contrib.auth import get_user_model

class ChatSession(models.Model):
    """One conversation thread."""
    title       = models.CharField(max_length=120, blank=True)
    owner       = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="chat_sessions"
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"ChatSession {self.pk}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [("user","User"),("assistant","Assistant")]

    session     = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content     = models.TextField(blank=True)
    image_url  = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.image_data:
            return f"{self.role}: [image]"
        return f"{self.role}: {self.content[:30]}…"
    
    
class ChatSummarize(models.Model):
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="summaries"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary {self.pk} ({self.session_id})"