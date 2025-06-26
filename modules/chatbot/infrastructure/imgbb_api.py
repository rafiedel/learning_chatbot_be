import os, requests

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
UPLOAD_URL = "https://api.imgbb.com/1/upload"

def upload_image(base64_str: str) -> str:
    resp = requests.post(
        UPLOAD_URL,
        data={"key": IMGBB_API_KEY, "image": base64_str}
    )
    resp.raise_for_status()
    return resp.json()["data"]["url"]