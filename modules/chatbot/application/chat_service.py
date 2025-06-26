from modules.chatbot.infrastructure.gemini_api import GeminiClient
from modules.chatbot.infrastructure.imgbb_api import upload_image
from modules.chatbot.models import ChatSession, ChatMessage

class ChatService:
    @staticmethod
    def _history(session: ChatSession) -> list[dict]:
        msgs = session.messages.order_by('created_at')
        history = []
        for m in msgs:
            entry = {"role": m.role}
            if m.content:
                entry["text"] = m.content
            if m.image_data:
                entry["image"] = {"mimeType": "", "data": m.image_data}
            history.append(entry)
        return history

    @staticmethod
    def send_and_store(session: ChatSession, message: str = None, image: str = None) -> dict:
        # Save user input
        if image:
            ChatMessage.objects.create(
                session=session, role="user", image_data=image
            )
        else:
            ChatMessage.objects.create(
                session=session, role="user", content=message
            )

        # Build full history
        history = ChatService._history(session)

        # Send to Gemini
        reply = GeminiClient.chat(history)

        # Upload user image to imgbb and record URL
        if image:
            url = upload_image(image)
            session.image_urls.append(url)
            session.save()

        # Save assistant reply
        ChatMessage.objects.create(
            session=session, role=reply["role"], content=reply.get("content","")
        )

        return {
            "role": reply["role"],
            "content": reply.get("content",""),
            "image_urls": session.image_urls,
        }
