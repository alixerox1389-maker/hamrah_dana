import json
import os
import re
import urllib.error
import urllib.request
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Hamrah Dana API", version="1.2.0")


class ChatRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=8000)]


def normalize(text: str) -> str:
    table = str.maketrans("ي ك۰۱٢۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "ی ک۰۱23456789۰۱۲۳۴۵۶۷۸۹")
    return re.sub(r"\s+", " ", text.translate(table).strip().lower())


def offline_answer(message: str) -> str:
    q = normalize(message)

    if any(x in q for x in ("سلام", "درود", "خوبی", "چطوری")):
        return "سلام! من همراه دانا هستم. در حال حاضر در حالت رایگانِ آموزشی کار می‌کنم و می‌توانم درباره مباحث پایه برق و الکترونیک راهنمایی بدهم. سوالت را بپرس."

    if any(x in q for x in ("قانون اهم", "ohm", "محاسبه جریان", "جریان چقدر", "ولتاژ چقدر")):
        return (
            "قانون اهم رابطه ولتاژ، جریان و مقاومت را نشان می‌دهد:\n"
            "V = I × R\n"
            "V ولتاژ بر حسب ولت، I جریان بر حسب آمپر و R مقاومت بر حسب اهم است.\n"
            "برای پیدا کردن جریان: I = V ÷ R\n"
            "مثال: اگر ولتاژ ۱۲ ولت و مقاومت ۶ اهم باشد، جریان برابر ۲ آمپر است. "
            "اگر مقادیر مسئله‌ات را بفرستی، مرحله‌به‌مرحله حل می‌کنم."
        )

    # Specific LED questions must be checked before generic diode/resistor matches.
    if (("مدار" in q or "بساز" in q or "ببند" in q) and
            any(x in q for x in ("led", "ال ای دی", "ال‌ای‌دی"))):
        return (
            "برای یک مدار تمرینی کم‌ولتاژ می‌توانی از باتری ۳ تا ۵ ولت، یک LED و یک مقاومت سری استفاده کنی.\\n"
            "۱) پایه بلند LED معمولاً آند (+) و پایه کوتاه‌تر کاتد (−) است.\\n"
            "۲) مقاومت را با LED به‌صورت سری قرار بده تا جریان محدود شود؛ برای منبع ۵ ولت، "
            "مقاومت ۲۲۰ تا ۳۳۰ اهم معمولاً نقطه شروع مناسبی برای یک LED معمولی است.\\n"
            "۳) آند LED را از مسیر مقاومت به مثبت باتری و کاتد را به منفی باتری وصل کن. "
            "اگر LED روشن نشد، باتری را جدا کن و جهت LED و اتصالات را بررسی کن. "
            "هرگز LED را بدون محدودکننده جریان مستقیم به باتری وصل نکن."
        )

    if ("تفاوت" in q and "دیود" in q and any(x in q for x in ("led", "ال ای دی", "ال‌ای‌دی"))):
        return (
            "LED خودش نوعی دیود است، اما تفاوت اصلی در کاربرد آن‌هاست:\\n"
            "• دیود معمولی عمدتاً برای یکسوسازی و عبور جریان در یک جهت به کار می‌رود و معمولاً نور قابل‌مشاهده تولید نمی‌کند.\\n"
            "• LED یا دیود نورگسیل، هنگام عبور جریان در جهت صحیح نور تولید می‌کند.\\n"
            "هر دو قطب آند و کاتد دارند و برای جلوگیری از عبور جریان بیش از حد، LED معمولاً به مقاومت سری نیاز دارد."
        )

    if any(x in q for x in ("ال ای دی", "ال‌ای‌دی", "led")):
        return (
            "LED نوعی دیود نورگسیل است؛ با عبور جریان در جهت صحیح نور تولید می‌کند. "
            "برای استفاده در مدار معمولاً باید جریان آن محدود شود؛ این کار اغلب با مقاومت سری انجام می‌شود. "
            "اتصال مستقیم LED معمولی به منبع ولتاژ بدون محدودکننده جریان می‌تواند به آن آسیب بزند."
        )

    if "مقاومت" in q or "resistor" in q:
        return (
            "مقاومت قطعه‌ای است که در برابر عبور جریان الکتریکی محدودیت ایجاد می‌کند. "
            "واحد آن اهم (Ω) است. مقاومت‌ها برای محدودکردن جریان، تقسیم ولتاژ و تنظیم شرایط کار مدار استفاده می‌شوند.\n"
            "نکته: در یک مقاومت ثابت، با افزایش ولتاژ دو سر آن، جریان نیز طبق قانون اهم افزایش می‌یابد."
        )

    if "خازن" in q or "capacitor" in q:
        return (
            "خازن قطعه‌ای است که انرژی الکتریکی را در میدان الکتریکی ذخیره می‌کند. "
            "واحد ظرفیت آن فاراد (F) است. خازن‌ها در صاف‌کردن ولتاژ، فیلترکردن نویز و مدارهای زمان‌ساز کاربرد دارند.\n"
            "دو نوع رایج: سرامیکی و الکترولیتی. خازن الکترولیتی قطب مثبت و منفی دارد و باید درست نصب شود."
        )

    if "دیود" in q or "diode" in q:
        return (
            "دیود قطعه‌ای نیمه‌رساناست که در حالت عادی جریان را عمدتاً در یک جهت عبور می‌دهد. "
            "پایه آند و کاتد دارد. در بسیاری از دیودهای معمولی، نوار روی بدنه سمت کاتد را نشان می‌دهد. "
            "کاربردها: یکسوسازی، محافظت در برابر اتصال معکوس و جداسازی مسیرهای جریان."
        )

    if "ال ای دی" in q or "led" in q or "لامپ smd" in q or "لامپ اس ام دی" in q:
        return (
            "LED نوعی دیود نورگسیل است؛ با عبور جریان در جهت صحیح نور تولید می‌کند. "
            "برای استفاده در مدار معمولاً باید جریان آن محدود شود؛ این کار اغلب با مقاومت سری انجام می‌شود. "
            "اتصال مستقیم LED معمولی به منبع ولتاژ بدون محدودکننده جریان می‌تواند به آن آسیب بزند."
        )

    if "ترانزیستور" in q or "transistor" in q:
        return (
            "ترانزیستور قطعه نیمه‌رسانایی است که معمولاً برای تقویت سیگنال یا قطع‌و‌وصل الکترونیکی به کار می‌رود. "
            "در نوع BJT سه پایه بیس، کلکتور و امیتر دارد. جریان کوچک بیس می‌تواند جریان بزرگ‌تری بین کلکتور و امیتر را کنترل کند. "
            "پایه‌بندی دقیق را باید از دیتاشیت همان شماره قطعه بررسی کرد."
        )

    if "مدار سری" in q or "سری" == q:
        return (
            "در اتصال سری، قطعات پشت سر هم در یک مسیر قرار می‌گیرند. جریان عبوری از همه قطعات یکسان است "
            "و ولتاژ منبع بین آن‌ها تقسیم می‌شود. مقاومت معادل مقاومت‌های سری برابر مجموع آن‌هاست: "
            "Rکل = R1 + R2 + ..."
        )

    if "موازی" in q:
        return (
            "در اتصال موازی، دو سر هر قطعه به دو گره مشترک وصل می‌شود. ولتاژ دو سر شاخه‌ها یکسان است "
            "و جریان بین شاخه‌ها تقسیم می‌شود. برای دو مقاومت موازی: "
            "Rکل = (R1 × R2) ÷ (R1 + R2)."
        )

    if "توان" in q and ("الکتریکی" in q or "مدار" in q or "وات" in q):
        return (
            "توان الکتریکی نرخ مصرف یا انتقال انرژی است و با وات (W) سنجیده می‌شود. "
            "در مدارهای ساده: P = V × I. همچنین برای مقاومت: P = I² × R یا P = V² ÷ R. "
            "هنگام انتخاب مقاومت باید توان نامی آن از توان تلف‌شده در مدار بیشتر باشد."
        )

    if "برد" in q and ("چاپی" in q or "pcb" in q):
        return (
            "برد مدار چاپی (PCB) صفحه‌ای عایق است که مسیرهای رسانا روی آن، قطعات الکترونیکی را به هم متصل می‌کنند. "
            "برد چاپی باعث نظم، استحکام و تکرارپذیری بهتر مدار می‌شود. قبل از لحیم‌کاری، جای قطعات و جهت قطعات قطب‌دار را بررسی کن."
        )

    if "لحیم" in q or "هویه" in q:
        return (
            "لحیم‌کاری برای ایجاد اتصال الکتریکی و مکانیکی بین پایه قطعه و سطح مسی برد انجام می‌شود. "
            "نوک هویه و محل اتصال باید تمیز باشند؛ حرارت را فقط به اندازه لازم اعمال کن و از تهویه مناسب استفاده کن. "
            "به نوک هویه داغ دست نزن و پس از کار آن را در پایه مخصوص قرار بده."
        )

    if any(x in q for x in ("برق گرفتگی", "برق شهر", "۲۲۰ ولت", "220 ولت", "برق شهری")):
        return (
            "هشدار ایمنی: برق شهر می‌تواند بسیار خطرناک و حتی مرگبار باشد. برای تمرین‌های آموزشی از باتری کم‌ولتاژ و مدارهای ایمن استفاده کن. "
            "بدون نظارت فرد متخصص، دستگاه را به برق شهر وصل نکن و داخل منبع تغذیه یا وسیله متصل به برق شهر را باز نکن."
        )

    if any(x in q for x in ("الکترونیک چیست", "برق چیست")):
        return (
            "الکترونیک شاخه‌ای از دانش مهندسی است که رفتار و کنترل جریان الکتریکی را در قطعات و مدارها بررسی می‌کند. "
            "با مدارهای الکترونیکی می‌توان سیگنال‌ها را دریافت، پردازش، تقویت و کنترل کرد."
        )

    return (
        "می‌خواهم درست راهنمایی‌ات کنم. در حال حاضر نسخه رایگان همراه دانا بدون اتصال به سرویس هوش مصنوعی بیرونی اجرا می‌شود؛ "
        "بنابراین دانش آن محدود به پاسخ‌های آموزشی پایه است.\n"
        "لطفاً سوالت را دقیق‌تر بنویس یا نام قطعه، موضوع درسی، فرمول یا متن مسئله را بفرست تا در حد اطلاعات موجود کمک کنم. "
        "برای پاسخ هوشمند و آزاد به همه موضوعات، بعداً باید یک موتور هوش مصنوعی مجاز به سرور متصل شود."
    )


@app.get("/")
def root():
    return {
        "service": "Hamrah Dana API",
        "status": "ok",
        "health": "/health",
    }


def cloudflare_answer(message: str) -> str:
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    api_token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    if not account_id or not api_token:
        raise RuntimeError("Cloudflare credentials are not configured")

    endpoint = (
        "https://api.cloudflare.com/client/v4/accounts/"
        + account_id
        + "/ai/run/@cf/meta/llama-3.1-8b-instruct"
    )
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Hamrah Dana, a helpful Persian-speaking tutor. "
                    "Prioritize beginner electricity/electronics education. "
                    "Explain concepts simply and step by step. For calculations, "
                    "show formulas, units, and intermediate steps. Do not invent facts. "
                    "Give concise general-knowledge answers when asked. For mains "
                    "electricity or hazardous circuits, give safety-first high-level "
                    "guidance and direct the learner to a qualified adult."
                ),
            },
            {"role": "user", "content": message},
        ],
        "max_tokens": 900,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=75) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("success"):
        raise RuntimeError("Cloudflare API returned an unsuccessful response")
    answer = (result.get("result") or {}).get("response")
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Cloudflare returned an empty response")
    return answer.strip()


@app.get("/health")
def health():
    configured = bool(
        os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
        and os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    )
    return {
        "status": "ok",
        "ai_configured": configured,
        "mode": "cloudflare_workers_ai" if configured else "offline_educational",
    }


@app.post("/chat")
def chat(body: ChatRequest):
    try:
        return {
            "answer": cloudflare_answer(body.message),
            "mode": "cloudflare_workers_ai",
        }
    except Exception:
        return {
            "answer": offline_answer(body.message),
            "mode": "offline_fallback",
        }
