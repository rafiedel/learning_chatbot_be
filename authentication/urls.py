from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import UserLoginView, UserRegisterView

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="auth-register"),
    path("login/", UserLoginView.as_view(),     name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
]
