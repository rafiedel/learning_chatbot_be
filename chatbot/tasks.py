# chat/tasks.py

from celery import shared_task

from clients.gemini_client import GeminiClient
from .models import ChatSession, ChatSummarize

@shared_task
def summarize_chat(session_id, user_content, assistant_content):
    # print("🟢 summarize_chat task started")
    # print("Session ID:", session_id)
    # print("User Content:", user_content)
    # print("Assistant Content:", assistant_content)
    
    summary_prompt = (
        "You are creating a short, factual summary of the following exchange for your own future reference. "
        "Capture every concrete point (numbers, definitions, steps, etc.) exactly as stated. "
        "Do **NOT** add, infer, or omit information. "
        "Present the result as concise bullet points.\n\n"
        f"User said:\n{user_content}\n\n"
        f"Assistant replied:\n{assistant_content}\n\n"
        "Bullet-point summary:"
    )
    try:
        result = GeminiClient.chat([
            {"role": "user", "text": summary_prompt}
        ])
        # print("Gemini Response:", result)
        summary_text = result.get("content", "").strip()
        if summary_text:
            ChatSummarize.objects.create(
                session_id=session_id,
                content=summary_text
            )
            print("✅ ChatSummarize created successfully")
        else:
            print("⚠️ Empty summary text")
    except Exception as e:
        print("❌ Exception in summarize_chat:", e)
