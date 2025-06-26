import re
import json
from django.utils.text import Truncator
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema
from modules.chatbot.infrastructure.models.chat_message_model import ChatSession, ChatMessage
from modules.chatbot.interface.serializers.serializers import (
    ChatRequestSerializer, ChatResponseSerializer,
    ChatSessionSerializer, ChatMessageSerializer, ChatSessionTitleSerializer
)
from modules.chatbot.interface.pagination import ChatSessionPagination, ChatMessagePagination
from modules.chatbot.application.services.chat_service import ChatService


class LenientJSONParser(JSONParser):
    """
    JSON parser that strips trailing commas before loading.
    """
    def parse(self, stream, media_type=None, parser_context=None):
        raw = stream.read().decode('utf-8')
        cleaned = re.sub(r',\s*}', '}', raw)
        cleaned = re.sub(r',\s*\]', ']', cleaned)
        return json.loads(cleaned)

class ChatCompletionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, LenientJSONParser]
    http_method_names  = ['post']  

    @extend_schema(request=ChatRequestSerializer, responses={200: ChatResponseSerializer})
    def post(self, request):
        ser = ChatRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sess_id = ser.validated_data.get("session_id")
        message = ser.validated_data.get("message")
        image   = ser.validated_data.get("image")

        if sess_id is None:
            session = ChatSession.objects.create(
                owner=request.user,
                title=Truncator(message or "[image]").chars(40)
            )
        else:
            try:
                session = ChatSession.objects.get(id=sess_id, owner=request.user)
            except ChatSession.DoesNotExist:
                raise ValidationError({"session_id": "Chat session not found"})

        try:
            reply = ChatService.send_and_store(session, message, image)
        except Exception as e:
            print("💥 ChatService error →", e)
            raise ValidationError({"detail": str(e)})

        return Response({"session_id": session.id, **reply})

class ChatSessionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ChatSessionSerializer
    pagination_class   = ChatSessionPagination
    http_method_names  = ['get']  

    def get_queryset(self):
        qs = ChatSession.objects.filter(owner=self.request.user)
        title = self.request.query_params.get("title")
        if title is not None:
            return qs.filter(title__icontains=title)
        return qs

class ChatSessionUpdateTitleView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ChatSessionTitleSerializer
    http_method_names  = ['put']  

    def get_queryset(self):
        return ChatSession.objects.filter(owner=self.request.user)

class ChatSessionDeleteView(generics.DestroyAPIView):
    permission_classes  = [IsAuthenticated]
    http_method_names   = ['delete']

    def get_queryset(self):
        return ChatSession.objects.filter(owner=self.request.user)

class ChatMessageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ChatMessageSerializer
    pagination_class   = ChatMessagePagination
    http_method_names  = ['get']

    def get_queryset(self):
        session_id = self.kwargs.get('session_id')
        return ChatMessage.objects.filter(session_id=session_id).order_by('created_at')
class ChatMessageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ChatMessageSerializer
    pagination_class   = ChatMessagePagination

    def get_queryset(self):
        session_id = self.kwargs.get('session_id')
        return ChatMessage.objects.filter(session_id=session_id).order_by('created_at')
