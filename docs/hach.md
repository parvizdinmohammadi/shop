# Hash

## پسورد
- الگوریتم: bcrypt
- کتابخانه: passlib[bcrypt]
- cost factor: 12
- salt: خودکار per-user (bcrypt خودش اضافه می‌کند)
- طول hash: 60 کاراکتر

## توکن‌ها
- refresh token در DB فقط به‌صورت hash (sha256) ذخیره می‌شود
- access token stateless است (در DB ذخیره نمی‌شود)
- هنگام refresh، توکن قدیمی revoke و توکن جدید صادر می‌شود

## داده حساس
- در صورت نیاز به امضا: HMAC-SHA256 با SECRET_KEY

## ممنوع
- md5 / sha1 برای پسورد
- ذخیره plain password
- لاگ کردن پسورد یا توکن
- استفاده از SHA256 خالی برای پسورد (نیاز به salt و cost دارد)