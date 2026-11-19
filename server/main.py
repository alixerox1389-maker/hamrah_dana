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
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="API key is not configured."
        )

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search"}],
            input=(
                "تو دستیار هوشمند همراه دانا هستی. "
                "به فارسی روان، دقیق و قابل فهم پاسخ بده. "
                "اگر لازم بود از جست‌وجوی وب استفاده کن. "
                "پاسخ را متناسب با سن کاربر و ایمن ارائه بده.\n\n"
                + body.message
            )
        )

        return {"answer": response.output_text}

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI service request failed."
        )
