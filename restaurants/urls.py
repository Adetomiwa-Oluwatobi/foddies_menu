"""
URL configuration for restaurants project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('auth/', include('social_django.urls', namespace='social')), # Social auth URLs
    path('menu/', views.menu, name='menu'),  # Menu view
    path('api/order/', views.order_item, name='order_item'),  # Fixed API order endpoint
    path('orders/', views.view_orders, name='view_orders'),  # View orders
    path('mark-delivered/<int:order_id>/', views.mark_as_delivered, name='mark_as_delivered'),  # Mark order as delivered
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),  # Payment processing
    path('add-to-order/<int:item_id>/', views.add_to_order, name='add_to_order'),  # Add item to order
    path('order-list/', views.view_order_list, name='view_order_list'),  # View order list
    path('checkout/', views.checkout, name='checkout'),  # Checkout view
    path('payment/initialize/', views.initialize_payment, name='initialize_payment'),
    path('payment/pos/<int:order_id>/', views.request_pos_payment, name='request_pos_payment'),
    
    path('payment/verify/', views.verify_payment, name='verify_payment'),  # Verify payment
    path('pos/manage/', views.manage_pos_payments, name='manage_pos_payments'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('pos/mark-paid/<int:order_id>/', views.mark_as_paid, name='mark_as_paid'),
    path('manage-bank-payments/', views.manage_bank_payments, name='manage_bank_payments'),
    path('mark-as-paid/<int:payment_id>/', views.mark_as_paidy, name='mark_as_paidy'),
     path('payment/transfer/<int:order_id>/', views.bank_details_view, name='bank_details'),
     
    path('menu/manage', views.menu_management, name='menu_management'),
    path('menu/item/<int:item_id>/', views.get_menu_item, name='get_menu_item'),
    path('menu/create/', views.create_menu_item, name='create_menu_item'),
    path('menu/update/<int:item_id>/', views.update_menu_item, name='update_menu_item'),
    path('menu/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('staffmgt/', views.staff_management, name='staff_management'),
]
"""path('payment/transfer/<int:order_id>/', views.bank_transfer_payment, name='bank_transfer_payment'),
path('remove-from-order/<int:item_id>/', views.remove_from_order, name='remove_from_order'),"""

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)