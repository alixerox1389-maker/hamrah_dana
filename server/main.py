import os
from typing import Annotated

from fastapi import FastAPI, HTTPException
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)
from pydantic import BaseModel, Field

app = FastAPI(title="Hamrah Dana API", version="1.1.0")

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
_client: OpenAI | None = None


class ChatRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=8000)]


def get_client() -> OpenAI:
    global _client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured on the server.",
        )
    if _client is None:
        _client = OpenAI(api_key=api_key, timeout=90.0, max_retries=1)
    return _client


@app.get("/")
def root():
    return {
        "service": "Hamrah Dana API",
        "status": "ok",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "model": MODEL,
    }


@app.post("/chat")
def chat(body: ChatRequest):
    prompt = (
        "تو دستیار آموزشی همراه دانا هستی. "
        "تمرکز اصلی تو آموزش برق و الکترونیک است و در کنار آن به پرسش‌های عمومی "
        "نیز پاسخ می‌دهی. به فارسی روان، دقیق و قابل فهم پاسخ بده. "
        "برای مسائل آموزشی، مرحله‌به‌مرحله توضیح بده و اگر داده‌ای کافی نیست "
        "شفاف سؤال تکمیلی بپرس. پاسخ‌ها باید متناسب با سن کاربر و ایمن باشند.\n\n"
        + body.message.strip()
    )

    try:
        client = get_client()
        result = client.responses.create(
            model=MODEL,
            input=prompt,
        )
        answer = (result.output_text or "").strip()
        if not answer:
            raise HTTPException(
                status_code=502,
                detail="AI service returned an empty response.",
            )
        return {"answer": answer}
    except HTTPException:
        raise
    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="AI service timed out.",
        )
    except APIConnectionError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to AI service.",
        )
    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="AI service rate limit or quota reached.",
        )
    except APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="AI service rejected the request.",
        )
