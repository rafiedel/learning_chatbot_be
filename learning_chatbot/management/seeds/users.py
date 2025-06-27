from django.contrib.auth.hashers import make_password

users_data = [
    {
        'username': 'user1',
        'email': 'user1@example.com',
        'password': make_password('password1')
    },
]
