import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Hamrah Dana API")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(body: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")
    if not api_key or not model:
        raise HTTPException(
            status_code=503,
            detail="Server is not configured. Set OPENAI_API_KEY and OPENAI_MODEL."
        )
    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search"}],
            input=(
                "پاسخ را به فارسی، روشن و دقیق بده. اگر از وب استفاده کردی "
                "منابع را در پاسخ معرفی کن.\n\nپرسش کاربر: " + body.message
            ),
        )
        return {"answer": response.output_text}
    except Exception:
        raise HTTPException(status_code=502, detail="AI service request failed.")
