from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from modules.authentication.application.services.user_service import UserService
from modules.authentication.interface.serializers.user_serializer import RegisterSerializer, LoginSerializer

class UserRegisterView(APIView):
    http_method_names  = ['post']  
    @extend_schema(request=RegisterSerializer, responses={201: RegisterSerializer})
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = UserService().register(**ser.validated_data)
        return Response(
            {"id": user.id, "username": user.username, "email": user.email},
            status=status.HTTP_201_CREATED,
        )

class UserLoginView(APIView):
    http_method_names  = ['post']  
    @extend_schema(request=LoginSerializer, responses={200: dict})
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        tokens = UserService().login(**ser.validated_data)
        if not tokens:
            return Response({"detail": "Invalid credentials"},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(tokens)
