from django.urls import path
from .views import RegisterView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(),     name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
]
