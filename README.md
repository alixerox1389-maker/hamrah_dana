# همراه دانا

اپلیکیشن Flutter برای دستیار آموزشی فارسی با تمرکز اصلی بر برق و الکترونیک.

## ساخت APK
گردش‌کار GitHub Actions مستقیماً از سورس همین مخزن استفاده می‌کند؛ فایل‌های ZIP قدیمی در فرایند ساخت نقشی ندارند.
با هر Push به شاخه `main` یا اجرای دستی Workflow، تحلیل کد، تست رابط و ساخت APK انجام می‌شود.
خروجی با نام `hamrah-dana-apk` در بخش Artifacts اجرای موفق قابل دریافت است.

## Backend
سرویس FastAPI در پوشه `server` اجرا می‌شود. تنظیمات سرویس Render:
- Root Directory: `server`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

متغیرهای محیطی موردنیاز در Render:
- `OPENAI_API_KEY`: کلید API محرمانه؛ فقط در Environment سرویس Render ذخیره شود.
- `OPENAI_MODEL`: نام مدل مجاز در حساب API؛ در صورت تنظیم‌نشدن، مقدار پیش‌فرض کد استفاده می‌شود.

آدرس پیش‌فرض API در اپ: `https://hamrah-dana.onrender.com`.
مجوز Android برای اینترنت در زمان ساخت کنترل و در صورت نیاز اضافه می‌شود.
