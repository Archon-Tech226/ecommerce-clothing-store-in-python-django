from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.utils.text import slugify
from .models import Product, Category, Order, OrderItem
import json


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_cart(request):
    return request.session.get('cart', {})

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def admin_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('admin_login')
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ─────────────────────────────────────────────
# STORE VIEWS
# ─────────────────────────────────────────────

def home(request):
    featured = Product.objects.filter(is_active=True).select_related('category')[:8]
    categories = Category.objects.annotate(product_count=Count('products'))
    return render(request, 'store/home.html', {'featured': featured, 'categories': categories})


def shop(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()
    q = request.GET.get('q', '')
    cat = request.GET.get('category', '')
    tag = request.GET.get('tag', '')
    sort = request.GET.get('sort', 'newest')

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if cat:
        products = products.filter(category__slug=cat)
    if tag:
        products = products.filter(tag=tag)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    return render(request, 'store/shop.html', {
        'products': products, 'categories': categories,
        'q': q, 'selected_cat': cat, 'selected_tag': tag, 'sort': sort,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=pk)[:4]
    return render(request, 'store/product_detail.html', {'product': product, 'related': related})


def cart(request):
    cart_data = get_cart(request)
    items = []
    subtotal = 0
    for pid, qty in cart_data.items():
        try:
            p = Product.objects.get(pk=int(pid), is_active=True)
            line = p.price * qty
            subtotal += line
            items.append({'product': p, 'qty': qty, 'line_total': line})
        except Product.DoesNotExist:
            pass
    shipping = 0 if subtotal >= 5000 else 299
    total = subtotal + shipping
    return render(request, 'store/cart.html', {
        'items': items, 'subtotal': subtotal, 'shipping': shipping, 'total': total
    })


def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart_data = get_cart(request)
    pid = str(pk)
    cart_data[pid] = cart_data.get(pid, 0) + 1
    save_cart(request, cart_data)
    messages.success(request, f'"{product.name}" added to your bag.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)


def cart_remove(request, pk):
    cart_data = get_cart(request)
    cart_data.pop(str(pk), None)
    save_cart(request, cart_data)
    return redirect('cart')


def cart_update(request):
    if request.method == 'POST':
        cart_data = get_cart(request)
        for key, val in request.POST.items():
            if key.startswith('qty_'):
                pid = key.replace('qty_', '')
                try:
                    qty = int(val)
                    if qty > 0:
                        cart_data[pid] = qty
                    else:
                        cart_data.pop(pid, None)
                except ValueError:
                    pass
        save_cart(request, cart_data)
    return redirect('cart')


def checkout(request):
    cart_data = get_cart(request)
    if not cart_data:
        return redirect('cart')

    items = []
    subtotal = 0
    for pid, qty in cart_data.items():
        try:
            p = Product.objects.get(pk=int(pid), is_active=True)
            line = p.price * qty
            subtotal += line
            items.append({'product': p, 'qty': qty, 'line_total': line, 'price': p.price})
        except Product.DoesNotExist:
            pass

    shipping = 0 if subtotal >= 5000 else 299
    total = subtotal + shipping

    if request.method == 'POST':
        order = Order.objects.create(
            customer_name=request.POST['name'],
            customer_email=request.POST['email'],
            customer_phone=request.POST['phone'],
            address=request.POST['address'],
            city=request.POST['city'],
            pincode=request.POST['pincode'],
            total_amount=total,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                price=item['price'],
                quantity=item['qty'],
            )
        request.session['cart'] = {}
        return redirect('order_success', order_id=order.id)

    return render(request, 'store/checkout.html', {
        'items': items, 'subtotal': subtotal, 'shipping': shipping, 'total': total
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'store/order_success.html', {'order': order})


# ─────────────────────────────────────────────
# ADMIN VIEWS
# ─────────────────────────────────────────────

def admin_login(request):
    if request.session.get('is_admin'):
        return redirect('admin_dashboard')
    error = None
    if request.method == 'POST':
        pwd = request.POST.get('password', '')
        if pwd == settings.ADMIN_PASSWORD:
            request.session['is_admin'] = True
            return redirect('admin_dashboard')
        error = 'Incorrect password. Please try again.'
    return render(request, 'store/admin_login.html', {'error': error})


def admin_logout(request):
    request.session.pop('is_admin', None)
    return redirect('admin_login')


@admin_required
def admin_dashboard(request):
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(t=Sum('total_amount'))['t'] or 0
    total_products = Product.objects.filter(is_active=True).count()
    pending_orders = Order.objects.filter(status='pending').count()
    recent_orders = Order.objects.order_by('-created_at')[:5]
    low_stock = Product.objects.filter(stock__lte=5, is_active=True)
    return render(request, 'store/admin_dashboard.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'low_stock': low_stock,
    })


@admin_required
def admin_products(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    return render(request, 'store/admin_products.html', {'products': products})


@admin_required
def product_add(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        p = Product(
            name=request.POST['name'],
            brand=request.POST.get('brand', 'Maison Elara'),
            description=request.POST.get('description', ''),
            price=request.POST['price'],
            tag=request.POST.get('tag', ''),
            stock=request.POST.get('stock', 10),
            is_active=bool(request.POST.get('is_active')),
        )
        cat_id = request.POST.get('category')
        if cat_id:
            p.category_id = cat_id
        op = request.POST.get('original_price')
        if op:
            p.original_price = op
        if request.FILES.get('image'):
            p.image = request.FILES['image']
        p.save()
        messages.success(request, 'Product added successfully.')
        return redirect('admin_products')
    return render(request, 'store/admin_product_form.html', {'categories': categories, 'action': 'Add'})


@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        product.name = request.POST['name']
        product.brand = request.POST.get('brand', 'Maison Elara')
        product.description = request.POST.get('description', '')
        product.price = request.POST['price']
        product.tag = request.POST.get('tag', '')
        product.stock = request.POST.get('stock', 10)
        product.is_active = bool(request.POST.get('is_active'))
        cat_id = request.POST.get('category')
        product.category_id = cat_id if cat_id else None
        op = request.POST.get('original_price')
        product.original_price = op if op else None
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('admin_products')
    return render(request, 'store/admin_product_form.html', {
        'product': product, 'categories': categories, 'action': 'Edit'
    })


@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
    return redirect('admin_products')


@admin_required
def admin_categories(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    return render(request, 'store/admin_categories.html', {'categories': categories})


@admin_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST['name']
        Category.objects.create(
            name=name,
            slug=slugify(name),
            description=request.POST.get('description', ''),
        )
        messages.success(request, 'Category added.')
    return redirect('admin_categories')


@admin_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST['name']
        category.slug = slugify(request.POST['name'])
        category.description = request.POST.get('description', '')
        category.save()
        messages.success(request, 'Category updated.')
    return redirect('admin_categories')


@admin_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
    return redirect('admin_categories')


@admin_required
def admin_orders(request):
    orders = Order.objects.prefetch_related('items').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'store/admin_orders.html', {'orders': orders, 'status_filter': status_filter})


@admin_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'store/admin_order_detail.html', {'order': order})


@admin_required
def order_status_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.status = request.POST['status']
        order.save()
        messages.success(request, f'Order #{pk} status updated.')
    return redirect('admin_order_detail', pk=pk)
