
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
        # Build contents list for generate_content
        try:
            contents = []
            for msg in messages:
                # Text part
                if msg.get('text'):
                    final_message = f"""
You are a personal learning assistant. Only answer questions that are educational in nature, such as those related to college courses or school subjects (elementary, middle, and high school).

If the question is not relevant to learning or education, politely decline to answer.

Always respond using the same language the user used in their question.

Format your answer in well-structured and clean **Markdown** for better readability.

Question:
{msg.get('text')}
"""
                    contents.append(final_message)
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
            print(e)
