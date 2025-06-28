from dataclasses import asdict
from typing import Any, List
import base64
from clients.gemini_client import GeminiClient
from clients.imgur_client import ImgurClient
from .entities import Message, ChatThread
from .repositories import DjangoChatRepository


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
        # 1) Call Gemini first using user message + image (if any)
        formatted = self._to_gemini_format(content, image_data)
        reply = GeminiClient.chat(formatted)
        
        # 2) Find or create session
        thread = self.repo.get_or_create_thread(owner, session_id=session_id, title=content)

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