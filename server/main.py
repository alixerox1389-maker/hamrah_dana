import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

app = FastAPI(title="Hamrah Dana API")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(body: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise HTTPException(status_code=503, detail="API key is missing.")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=(
                "به زبان فارسی، روشن و دقیق پاسخ بده. "
                "پرسش کاربر: " + body.message
            )
        )
        return {"answer": response.text}
    except Exception:
        raise HTTPException(status_code=502, detail="AI service request failed.")
