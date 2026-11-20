from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Hamrah Dana API")


class ChatRequest(BaseModel):
    message: str


RESPONSES = {
    "سلام": "سلام! من همراه دانا هستم؛ دستیار آموزشی تو در دنیای برق و الکترونیک.",
    "درود": "درود! خوش آمدی. چطور می‌توانم کمکت کنم؟",
    "قانون اهم": "قانون اهم: V = I × R. ولتاژ برابر حاصل‌ضرب جریان در مقاومت است.",
    "مقاومت": "مقاومت قطعه‌ای است که در برابر عبور جریان الکتریکی مخالفت می‌کند. واحد آن اهم است.",
    "خازن": "خازن قطعه‌ای است که انرژی الکتریکی را در میدان الکتریکی ذخیره می‌کند.",
    "دیود": "دیود قطعه‌ای نیمه‌رساناست که معمولاً جریان را در یک جهت عبور می‌دهد.",
    "ترانزیستور": "ترانزیستور برای تقویت سیگنال یا کنترل جریان الکتریکی استفاده می‌شود.",
    "ولتاژ": "ولتاژ اختلاف پتانسیل الکتریکی بین دو نقطه است. واحد آن ولت است.",
    "جریان": "جریان الکتریکی مقدار بار الکتریکی عبوری در واحد زمان است. واحد آن آمپر است.",
    "الکترونیک": "الکترونیک شاخه‌ای از دانش برق است که به بررسی قطعات و مدارهای الکترونیکی می‌پردازد."
}


DEFAULT_ANSWER = (
    "من همراه دانا هستم. هنوز پاسخ این سؤال در پایگاه آموزشی من ثبت نشده است. "
    "فعلاً نسخه آزمایشی من فعال است."
)


def answer_question(message):
    text = message.strip().lower()

    for keyword, answer in RESPONSES.items():
        if keyword in text:
            return answer

    return DEFAULT_ANSWER


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(body: ChatRequest):
    return {"answer": answer_question(body.message)}
