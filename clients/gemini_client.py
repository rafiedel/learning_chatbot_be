
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyBMWrl_5PxOIbraT-DeovjMvUsKd657Ddo"))

class GeminiClient:
    @staticmethod
    def chat(messages):
        """
        Send text and image inputs to Gemini via the google-generativeai SDK.
        `messages` is a list of dicts:
            - {'role': 'user'|'assistant', 'text': str}
            - {'role': 'user'|'assistant', 'image': {'mimeType': str, 'data': base64_str}}
        """
        # print("DEBUG GeminiClient.chat received messages:", messages)
        try:
            contents = []
            for msg in messages:
                # Text part
                if msg.get('text'):
                    contents.append(msg.get('text'))
                # Image part
                if msg.get('image'):
                    img = msg['image']
                    contents.append({
                        'mime_type': img.get('mimeType', ''),
                        'data': img.get('data', '')
                    })
            if not contents:
                raise ValueError("No content to send to Gemini")
            # Initialize model
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            model = genai.GenerativeModel(model_name)
            # Send contents list as expected by SDK
            response = model.generate_content(contents=contents)
            return {"role": "assistant", "content": response.text}
        except Exception as e :
            print("❌ Exception in GeminiClient.chat:", e)
            # Return an error response you can detect
            return {"role": "assistant", "content": ""}
