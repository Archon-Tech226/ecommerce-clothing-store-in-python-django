# Maison Elara — Luxury Fashion Ecommerce
### Built with Django + HTML/CSS/JS

---

## 🔗 Access URLs

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | **Buyer Store** — Homepage, Shop, Cart, Checkout |
| `http://127.0.0.1:8000/admin-panel/` | **Admin Dashboard** — Full CRUD |

**Admin Password:** `elara2026`
*(Change in `maison_elara/settings.py` → `ADMIN_PASSWORD`)*

---

## ⚡ Quick Setup (5 minutes)

### 1. Install Python
Make sure Python 3.9+ is installed: https://python.org

### 2. Create virtual environment
```bash
cd maison_elara
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up the database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. (Optional) Create sample data
```bash
python manage.py shell
```
Then paste:
```python
from store.models import Category, Product

c1 = Category.objects.create(name='Dresses', slug='dresses')
c2 = Category.objects.create(name='Outerwear', slug='outerwear')
c3 = Category.objects.create(name='Essentials', slug='essentials')

Product.objects.create(name='The Silk Column Dress', brand='Maison Elara', category=c1, price=18500, tag='new', stock=12, is_active=True, description='A fluid silk column dress that moves beautifully.')
Product.objects.create(name='Merino Longline Coat', brand='Maison Elara', category=c2, price=32000, stock=8, is_active=True, description='A luxurious merino wool coat with a relaxed, longline silhouette.')
Product.objects.create(name='Cashmere Turtleneck', brand='Maison Elara', category=c3, price=14200, original_price=18500, tag='sale', stock=15, is_active=True, description='Pure cashmere turtleneck in a relaxed fit.')
Product.objects.create(name='Draped Midi Dress', brand='Maison Elara', category=c1, price=16500, tag='new', stock=10, is_active=True)
exit()
```

### 6. Run the server
```bash
python manage.py runserver
```

Open: **http://127.0.0.1:8000/**

---

## 🏗️ Project Structure

```
maison_elara/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← auto-created after migrate
├── media/                  ← uploaded product images
│   └── products/
├── maison_elara/
│   ├── settings.py         ← ADMIN_PASSWORD is here
│   └── urls.py
└── store/
    ├── models.py           ← Category, Product, Order, OrderItem
    ├── views.py            ← All store + admin views
    ├── urls.py             ← All URL routes
    ├── context_processors.py
    └── templates/store/
        ├── base.html           ← Store base layout
        ├── home.html           ← Homepage
        ├── shop.html           ← Collection/shop page
        ├── product_detail.html ← Single product
        ├── cart.html           ← Shopping bag
        ├── checkout.html       ← Checkout form
        ├── order_success.html  ← Order confirmation
        ├── admin_login.html    ← Admin login
        ├── admin_base.html     ← Admin sidebar layout
        ├── admin_dashboard.html
        ├── admin_products.html
        ├── admin_product_form.html
        ├── admin_categories.html
        ├── admin_orders.html
        └── admin_order_detail.html
```

---

## ✅ Features

### Buyer Store (`/`)
- Homepage with hero, categories, featured products
- Shop page with search, filter by category/tag, sort by price
- Product detail page with related products
- Shopping cart with quantity update & remove
- Checkout with customer info & address form
- Order confirmation page

### Admin Panel (`/admin-panel/`)
- **Dashboard** — revenue, orders, products, pending count, low stock alerts
- **Products CRUD** — add, edit, delete, image upload, stock management
- **Categories CRUD** — add, edit, delete with inline modal
- **Orders** — list with status filter, detail view, status update

---

## 🔧 Customisation

### Change Admin Password
In `maison_elara/settings.py`:
```python
ADMIN_PASSWORD = 'your-new-password'
```

### Change Store Name
Search and replace `Maison Elara` across templates.

### Add Payment Gateway (Razorpay)
1. `pip install razorpay`
2. Add Razorpay keys to `settings.py`
3. Update `checkout` view in `views.py`

---

## 📦 Tech Stack
- **Backend:** Python 3.9+, Django 4.2
- **Database:** SQLite (swap to PostgreSQL for production)
- **Frontend:** Pure HTML/CSS/JS — no frameworks
- **Fonts:** Cormorant Garamond + Montserrat (Google Fonts)
- **Images:** Django media files with Pillow
