import os
import base64
import requests

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
IMGUR_UPLOAD_URL = "https://api.imgur.com/3/image"

class ImgurClient:
    @staticmethod
    def upload_image_from_bytes(image_bytes: bytes) -> str:
        base64_str = base64.b64encode(image_bytes).decode("utf-8")
        headers = {
            "Authorization": f"Client-ID {IMGUR_CLIENT_ID}",
        }
        resp = requests.post(
            IMGUR_UPLOAD_URL,
            headers=headers,
            data={
                "image": base64_str,
                "type": "base64",
            },
            timeout=20
        )

        resp.raise_for_status()
        data = resp.json()
        return data["data"]["link"]