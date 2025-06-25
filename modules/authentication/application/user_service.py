from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

DomainUser = User  # use Django's built-in directly

class UserService:
    @staticmethod
    def register(username: str, email: str, password: str) -> DomainUser:
        return get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
        )

    @staticmethod
    def generate_token_pair(user: DomainUser) -> dict[str, str]:
        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    @staticmethod
    def authenticate_and_get_tokens(username: str, password: str) -> dict | None:
        user = authenticate(username=username, password=password)
        if not user:
            return None
        return UserService.generate_token_pair(user)
