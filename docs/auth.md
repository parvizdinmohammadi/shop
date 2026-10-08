# احراز هویت

## جریان
1. ثبت‌نام: email + password → hash → ذخیره
2. ورود: email + password → verify → access + refresh
3. دسترسی: Authorization: Bearer <access>
4. انقضا: با refresh توکن جدید بگیر
5. خروج: refresh در blacklist

## نقش‌ها
- customer: خرید، سبد، سفارش
- admin: مدیریت محصولات، کاربران، سفارش‌ها

## قواعد
- email یکتا
- پسورد حداقل ۸ کاراکتر، شامل حرف و رقم
- توکن‌ها هرگز در URL نمی‌آیند
- refresh rotation فعال (هر بار refresh، توکن قبلی باطل)
- refresh token در DB به‌صورت hash ذخیره می‌شود

## Endpoint ها
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- POST /api/auth/logout
- GET  /api/auth/me