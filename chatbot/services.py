from typing import Any, List
import base64
from clients.gemini_client import GeminiClient
from clients.imgbb_client import IMGBBClient
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
        thread = self.repo.get_or_create_thread(owner, session_id=session_id)

        # 3) Save user message
        message_id = self.repo.add_user_message(thread.id, content=content)

        # 4) Optional: upload image to IMGBB and store URL
        if image_data:
            try:
                base64_str = ""
                for msg in formatted:
                    if "image" in msg:
                        base64_str = msg["image"]["data"]
                        break
                url = IMGBBClient.upload_image(base64_str)
                self.repo.append_image_url(message_id, url)
            except Exception as e:
                print(f"Image upload failed: {e}")

        # 5) Save assistant message
        self.repo.add_assistant_message(thread.id, content=reply.get("content", ""))

        return {
            "session_id": thread.id,
            "role": reply.get("role", "assistant"),
            "content": reply.get("content", ""),
        }