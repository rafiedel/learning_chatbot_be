from django.contrib.auth import get_user_model, authenticate

class UserRepository:
    def __init__(self):
        self.UserModel = get_user_model()

    def add_user(self, username: str, email: str, password: str):
        return self.UserModel.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

    def get_user(self, username: str, password: str):
        return authenticate(username=username, password=password)
