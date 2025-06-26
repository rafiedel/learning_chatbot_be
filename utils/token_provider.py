from rest_framework_simplejwt.tokens import RefreshToken

class TokenProvider:
    @staticmethod
    def tokens_for(django_user) -> dict[str, str]:
        refresh = RefreshToken.for_user(django_user)
        return {"access": str(refresh.access_token),
                "refresh": str(refresh)}