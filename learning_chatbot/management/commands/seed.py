from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from chatbot.models import ChatSession, ChatMessage
from learning_chatbot.management.seeds.users import users_data
from learning_chatbot.management.seeds.chat_session import chatsessions_data
from learning_chatbot.management.seeds.chat_message import chatmessages_data

class Command(BaseCommand):
    help = "Seed 1 user, 20 chatsessions, and 200 chatmessages."

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Create user1
        user_data = users_data[0]
        user, created = User.objects.get_or_create(
            username=user_data["username"],
            defaults={
                "email": user_data["email"],
                "password": user_data["password"],
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created user1"))
        else:
            self.stdout.write(self.style.WARNING("User1 already exists"))

        # Create 20 ChatSessions
        sessions = []
        for data in chatsessions_data:
            session = ChatSession.objects.create(
                title=data["title"],
                owner=user
            )
            sessions.append(session)
            self.stdout.write(self.style.SUCCESS(f"Created {session.title}"))

        # For each session, create 10 ChatMessages
        for session in sessions:
            for message_data in chatmessages_data:
                ChatMessage.objects.create(
                    session=session,
                    role=message_data["role"],
                    content=message_data["content"],
                    image_url=message_data["image_url"]
                )
            self.stdout.write(self.style.SUCCESS(f"Added 10 messages to {session.title}"))
