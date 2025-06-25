from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, LoginSerializer
from .application.user_service import UserService

class RegisterView(APIView):
    @extend_schema(request=RegisterSerializer, responses={201: RegisterSerializer})
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = UserService.register(**ser.validated_data)
        return Response(
            {"id": user.id, "username": user.username, "email": user.email},
            status=status.HTTP_201_CREATED,
        )

class LoginView(APIView):
    @extend_schema(request=LoginSerializer, responses={200: dict})
    def post(self, request):
        print("kucing")
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        tokens = UserService.authenticate_and_get_tokens(**ser.validated_data)
        if not tokens:
            return Response({"detail": "Invalid credentials"},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(tokens)
