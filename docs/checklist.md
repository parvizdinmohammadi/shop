# Checklist پروژه فروشگاه

## زیرساخت
- [x] ساختار پوشه‌ها
- [x] virtual environment
- [x] requirements.txt
- [x] .env و config
- [ ] مستندات ۵ گانه

## دیتابیس
- [ ] مدل‌ها (User, Category, Product, Cart, CartItem, Order, OrderItem)
- [ ] Alembic migration
- [ ] Seed اولیه

## امنیت
- [ ] hash پسورد (bcrypt)
- [ ] JWT (access + refresh)
- [ ] RBAC (customer, admin)
- [ ] Rate limiting
- [ ] CORS
- [ ] اعتبارسنجی ورودی (Pydantic)
- [ ] مدیریت خطا بدون افشای جزئیات

## Auth
- [ ] ثبت‌نام
- [ ] ورود
- [ ] refresh token
- [ ] خروج (blacklist)
- [ ] بازیابی رمز

## فروشگاه
- [ ] CRUD محصولات (admin)
- [ ] لیست/جستجوی محصولات (public)
- [ ] سبد خرید
- [ ] ثبت سفارش
- [ ] تاریخچه سفارش

## تست و مستندات
- [ ] تست واحد
- [ ] Swagger UI
- [ ] README
