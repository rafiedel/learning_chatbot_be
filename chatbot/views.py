from dataclasses import asdict
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from chatbot.serializers import *
from chatbot.services import ChatService
from utils.wierd_json_parser import LenientJSONParser
from .repositories import DjangoChatRepository
from rest_framework.permissions import IsAuthenticated


class ChatCompletionView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CompletionIn, responses={200: dict})
    def post(self, request):
        flat_data = {k: v[0] if isinstance(v, list) else v for k, v in request.data.lists()}
        ser = CompletionIn(data=flat_data)
        ser.is_valid(raise_exception=True)

        svc = ChatService()
        reply = svc.send_message(owner=request.user, **ser.validated_data)
        return Response(reply, status=status.HTTP_200_OK)

class ChatSessionListView(APIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]

    @extend_schema(parameters=[SessionQuery], responses={200: list})
    def get(self, request):
        q = SessionQuery(data=request.query_params)
        q.is_valid(raise_exception=True)
        repo = DjangoChatRepository()
        sessions= repo.list_threads(
            request.user,
            title_filter=q.validated_data.get("title"),
            before_id=q.validated_data.get("before_id"),
        )
        return Response({
            "results": [asdict(s) for s in sessions],
        })


class ChatSessionRenameView(APIView):
    http_method_names = ["patch"]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=RenameIn, responses={204: None})
    def patch(self, request, session_id: int):
        data = RenameIn(data=request.data)
        data.is_valid(raise_exception=True)
        DjangoChatRepository().update_thread_title(
            session_id, request.user, new_title=data.validated_data["title"])
        return Response({
            "results" : True
        },status=status.HTTP_200_OK)


class ChatSessionDeleteView(APIView):
    http_method_names = ["delete"]
    permission_classes = [IsAuthenticated]

    def delete(self, request, session_id: int):
        DjangoChatRepository().delete_thread(session_id, request.user)
        return Response({
            "results" : True
        },status=status.HTTP_200_OK)


class ChatMessageListView(APIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]

    @extend_schema(parameters=[MessagesQuery], responses={200: list})
    def get(self, request):
        q = MessagesQuery(data=request.query_params)
        q.is_valid(raise_exception=True)

        repo = DjangoChatRepository()
        msgs = repo.list_messages(
            q.validated_data["session_id"],
            request.user,
            before_id=q.validated_data.get("before_id")
        )

        return Response({
            "results": [asdict(m) for m in msgs]
        })