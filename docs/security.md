# قواعد امنیتی

## پسورد
- الگوریتم: bcrypt (passlib)
- cost factor: 12
- هیچ‌جا plain ذخیره نمی‌شود
- در پاسخ‌های API برنمی‌گردد
- در لاگ‌ها چاپ نمی‌شود

## JWT
- access: 30 دقیقه
- refresh: 7 روز
- الگوریتم: HS256
- SECRET_KEY از env، حداقل ۶۴ کاراکتر
- refresh token ها در DB ذخیره (hash شده) و قابل revoke

## ورودی
- همه ورودی‌ها با Pydantic اعتبارسنجی می‌شوند
- ORM = جلوگیری از SQL Injection
- محدودیت طول رشته‌ها (max_length)

## Rate Limiting
- slowapi روی endpoint های حساس (login/register)
- محدودیت: 5/minute برای login، 3/hour برای register

## CORS
- فقط origin های مجاز از env (ALLOWED_ORIGINS)

## خطاها
- پیام عمومی به کاربر
- جزئیات فقط در لاگ سرور
- هرگز traceback به کاربر نشان نده

## HTTPS
- در production اجباری

## مدیریت رازها
- هیچ پسورد/username/secret در کد hardcode نمی‌شود
- همه از .env خوانده می‌شوند
- .env در .gitignore