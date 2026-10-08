# قواعد داده

## جداول
- users: id, email, hashed_password, role, is_active, created_at, updated_at
- categories: id, name, slug, is_active, created_at, updated_at
- products: id, name, slug, description, price, stock, category_id, is_active, created_at, updated_at
- carts: id, user_id, created_at, updated_at
- cart_items: id, cart_id, product_id, quantity, created_at, updated_at
- orders: id, user_id, total, status, created_at, updated_at
- order_items: id, order_id, product_id, quantity, unit_price, created_at, updated_at
- refresh_tokens: id, user_id, token_hash, expires_at, revoked, created_at

## قواعد
- همه جداول: created_at, updated_at
- حذف محصولات = Soft Delete (is_active=False)
- قیمت‌ها: Decimal، نه Float
- تراکنش‌ها برای ثبت سفارش
- Migration با Alembic
- ایندکس روی: users.email, products.slug, categories.slug

## روابط
- User 1—N Order
- User 1—1 Cart
- Cart 1—N CartItem
- Category 1—N Product
- Order 1—N OrderItem