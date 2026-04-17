from django.urls import path
from . import views

urlpatterns = [
    # ---- STORE (Buyer) ----
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),

    # ---- ADMIN ----
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),

    # Products CRUD
    path('admin-panel/products/', views.admin_products, name='admin_products'),
    path('admin-panel/products/add/', views.product_add, name='product_add'),
    path('admin-panel/products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('admin-panel/products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # Categories CRUD
    path('admin-panel/categories/', views.admin_categories, name='admin_categories'),
    path('admin-panel/categories/add/', views.category_add, name='category_add'),
    path('admin-panel/categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('admin-panel/categories/delete/<int:pk>/', views.category_delete, name='category_delete'),

    # Orders
    path('admin-panel/orders/', views.admin_orders, name='admin_orders'),
    path('admin-panel/orders/<int:pk>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin-panel/orders/<int:pk>/status/', views.order_status_update, name='order_status_update'),
]
