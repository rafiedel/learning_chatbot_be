from rest_framework import serializers
from modules.chatbot.models import ChatSession, ChatMessage

class ChatRequestSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(required=False, allow_null=True)
    message    = serializers.CharField(required=False, allow_blank=True)
    image      = serializers.ImageField(required=False, allow_null=True)

class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    role       = serializers.CharField()
    content    = serializers.CharField()
    image_urls = serializers.ListField(child=serializers.URLField(), read_only=True)
    
class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatSession
        fields = ["id", "title", "created_at"]

class ChatSessionTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatSession
        fields = ["title"]

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatMessage
        fields = ["id", "role", "content", "created_at"]