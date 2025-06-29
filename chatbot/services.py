from dataclasses import asdict
from typing import Any, List
import base64
from chatbot.models import ChatMessage, ChatSummarize
from clients.gemini_client import GeminiClient
from clients.imgur_client import ImgurClient
from .entities import Message, ChatThread
from .repositories import DjangoChatRepository
from .tasks import summarize_chat

INTRODUCTION = """
You are a personal learning assistant. Only answer questions that are educational in nature.
If the question is not relevant to learning or education, politely decline to answer.
Always respond using the same language the user used in their question.
Format your answer in well-structured and clean **Markdown** for better readability.
"""


class ChatService:
    def __init__(self, repo: DjangoChatRepository | None = None):
        self.repo = repo or DjangoChatRepository()

    def _to_gemini_format(self, content: str, image_data=None) -> List[dict[str, Any]]:
        payload = [{"role": "user", "text": content}]
        if image_data:
            try:
                mime_type = image_data.content_type
                base64_str = base64.b64encode(image_data.read()).decode("utf-8")
                payload.append({
                    "role": "user",
                    "image": {
                        "mimeType": mime_type,
                        "data": base64_str,
                    },
                })
            except Exception as e:
                print(f"Failed to prepare image for Gemini: {e}")
        return payload

    def send_message(
        self,
        *,
        session_id: int | None,
        owner,
        content: str,
        image_data = None,
    ) -> dict[str, Any]:
        final_prompt = INTRODUCTION + "\n\n Question:\n" + content
        if session_id and session_id != 0:
            messages = ChatMessage.objects.filter(session_id=session_id).order_by("created_at")
            conversation_history = "\n".join(
                f"{m.role}: {m.content}"
                for m in messages
            )
            if conversation_history:
                final_prompt = f"""
{INTRODUCTION}

You have had previous conversations with this user. Here is the full transcript:

{conversation_history}

Now, the next question is:
{content}
"""
                
                print(final_prompt)


        # 1) Call Gemini first using user message + image (if any)
        formatted = self._to_gemini_format(final_prompt, image_data)
        reply = GeminiClient.chat(formatted)

        # 2) Find or create session
        thread = self.repo.get_or_create_thread(owner, session_id=session_id, title=content)

        # Schedule background summary ==============================
        summarize_chat.delay(
            session_id=thread.id,
            user_content=content,
            assistant_content=reply.get("content", "" )
        ) # Schedule background summary ==============================

        # 3) Save user message
        message_id = self.repo.add_user_message(thread.id, content=content)

        # 4) Optional: upload image to IMGBB and store URL
        if image_data:
            try:
                image_data.seek(0)  # Reset pointer
                image_bytes = image_data.read()
                url = ImgurClient.upload_image_from_bytes(image_bytes)
                self.repo.append_image_url(message_id, url)
            except Exception as e:
                print(f"Image upload failed: {e}")


        # 5) Save assistant message
        assistant_id = self.repo.add_assistant_message(thread.id, content=reply.get("content", ""))

        user_message = self.repo.get_message(message_id)
        assistant_message = self.repo.get_message(assistant_id)

        return {
            "session": {
                "id": thread.id,
                "title": thread.title,
                "created_at": thread.created_at,
            },
            "user_message": asdict(user_message),
            "assistant_message": asdict(assistant_message),
        }