from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Payment
from .models import MenuItem  
from django.utils.crypto import get_random_string
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
import json



@login_required
def menu(request):
    table_number = 2  # Example table number; replace with dynamic logic
    
    order = Order.objects.filter(table_number=table_number, status='pending').first()
    order_list = request.session.get('order_list', [])
    total_price = sum(item['price'] for item in order_list)
    if not order:
        order = Order.objects.create(table_number=table_number, item='', price=0.0)

    menu_items = MenuItem.objects.all()  # Fetch all menu items
    # Pass the menu items to the template
    return render(request, 'menu.html', {'menu_items': menu_items, 'order': order,'order_list': order_list, 'total_price': total_price})

from django.shortcuts import redirect, get_object_or_404

def add_to_order(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    order_list = request.session.get('order_list', [])
    order_list.append({'name': item.name, 'price': float(item.price)})
    request.session['order_list'] = order_list
    return redirect('menu')

def clear_order(request):
    request.session['order_list'] = []
    return redirect('menu')


"""def view_order_list(request):
    # Retrieve the order list from the session
    order_list = request.session.get('order_list', [])
    total_price = sum(item['price'] for item in order_list)  # Calculate the total price

    return render(request, 'order_list.html', {'order_list': order_list, 'total_price': total_price})"""
def view_order_list(request):
    order_list = request.session.get('order_list', [])
    processed_items = {}
    
    # Process items to include quantities
    for item in order_list:
        if item['name'] in processed_items:
            processed_items[item['name']]['quantity'] += 1
            processed_items[item['name']]['subtotal'] += item['price']
        else:
            processed_items[item['name']] = {
                'name': item['name'],
                'price': item['price'],
                'quantity': 1,
                'subtotal': item['price']
            }
    
    total_price = sum(item['price'] for item in order_list)
    
    return render(request, 'order_list.html', {
        'order_items': list(processed_items.values()),
        'total_price': total_price
    })    



def checkout(request):
    order_list = request.session.get('order_list', [])
    total_price = sum(item['price'] for item in order_list)

    if request.method == 'POST':
        # Handle payment and finalize order (e.g., save to the database)
        request.session['order_list'] = []  # Clear the order list after payment
        return redirect('order_success')  # Redirect to success page

    return render(request, 'checkout.html', {'order_list': order_list, 'total_price': total_price})
def order_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_number = data.get('table')
            item = data.get('item')
            price = data.get('price')

            # Save the order to the database
            Order.objects.create(table_number=table_number, item=item, price=price)

            response = {
                'message': f'Order for {item} has been placed successfully!',
                'table': table_number,
                'item': item,
                'price': price
            }
            return JsonResponse(response, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def mark_as_delivered(request, order_id):
    if request.method == 'POST':
        try:
            # Get the order by ID and mark as delivered
            order = Order.objects.get(id=order_id)
            order.status = 'delivered'
            order.save()
            return JsonResponse({'message': 'Order marked as delivered.'}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Simulate processing a payment
        payment_reference = get_random_string(12)  # Generate a random payment reference
        payment = Payment.objects.create(
            order=order,
            amount=order.price,
            payment_reference=payment_reference,
            payment_status='completed'  # Set the payment status to completed
        )
        order.status = 'delivered'
        order.save()  # Update the order status to delivered
        return JsonResponse({'message': 'Payment processed successfully', 'payment_reference': payment_reference})
    
    return render(request, 'payment_form.html', {'order': order})
"""def menu_view(request):
    return render(request, 'menu.html')
"""
"""def view_orders(request):
    orders = Order.objects.all()  # Retrieve all orders
    return render(request, 'orders.html', {'orders': orders})
"""
def view_orders(request):
    orders = Order.objects.all()
    
    # Get order items from session
    order_items = []
    for order in orders:
        items = request.session.get(f'order_list_{order.id}', [])
        for item in items:
            order_items.append({
                'order_id': order.id,
                'name': item['name'],
                'price': item['price']
            })

    return render(request, 'orders.html', {
        'orders': orders,
        'order_items': order_items
    })


"""import requests
from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from .models import Payment, Order
import uuid

def initialize_payment(request, order_id):
    # Get the order associated with the payment
    order = get_object_or_404(Order, id=order_id)

    # Generate a unique payment reference
    payment_reference = str(uuid.uuid4())
    
    # Create or retrieve the Payment instance
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.total_price,  # Assuming the `Order` model has a `total_price` field
            'payment_reference': payment_reference
        }
    )

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'email': order.customer_email,  # Assuming `Order` model has a `customer_email` field
        'amount': int(payment.amount) * 100,  # Convert Naira to Kobo
        'reference': payment.payment_reference,
        'callback_url': 'http://127.0.0.1:8000/payment/verify/',  # Update with your callback URL
    }
    
    response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        authorization_url = response_data['data']['authorization_url']
        return redirect(authorization_url)
    else:
        return JsonResponse({'error': 'Payment initialization failed'}, status=500)
    """
    


import uuid
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from .forms import EmailForm
from .models import Payment, Order
from django.urls import reverse

def initialize_payment(request):
    # Retrieve order items from session
    order_list = request.session.get('order_list', [])
    total_price = sum(item['price'] for item in order_list)

    # Ensure user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to proceed with payment.")
        return redirect('login')

    # Use authenticated user's email
    user_email = request.user.email

    # Generate unique payment reference
    payment_reference = str(uuid.uuid4())

    # Create a payment record
    payment = Payment.objects.create(
        amount=total_price,
        payment_reference=payment_reference,
        payment_status='pending'
    )

    # Paystack payment initialization
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'email': user_email,
        'amount': int(total_price * 100),  # Convert to kobo
        'reference': payment_reference,
        'callback_url': request.build_absolute_uri(reverse('verify_payment')),
        'metadata': {
            'order_items': [
                {'name': item['name'], 'price': item['price']} 
                for item in order_list
            ],
            'total_price': total_price,
            'user_id': request.user.id
        }
    }

    try:
        response = requests.post(
            'https://api.paystack.co/transaction/initialize', 
            headers=headers, 
            json=data
        )
        response_data = response.json()

        if response.status_code == 200:
            authorization_url = response_data['data']['authorization_url']
            
            # Optional: Link payment to orders
            order_items = Order.objects.filter(
                table_number=2,  # Assuming fixed table number
                status='pending'
            )
            payment.orders.add(*order_items)

            return redirect(authorization_url)
        else:
            payment.payment_status = 'failed'
            payment.save()
            messages.error(request, 'Payment initialization failed')
            return redirect('checkout')

    except requests.exceptions.RequestException as e:
        payment.payment_status = 'failed'
        payment.save()
        messages.error(request, f'Network error: {e}')
        return redirect('checkout')
def verify_payment(request):
    reference = request.GET.get('reference')
    
    try:
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'
        }
        response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', 
                                headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            payment_status = response_data['data']['status']
            
            # Retrieve associated payment record
            payment = Payment.objects.get(payment_reference=reference)
            
            if payment_status == 'success':
                payment.payment_status = 'completed'
                payment.save()
                
                # Clear session order list after successful payment
                request.session['order_list'] = []
                
                messages.success(request, 'Payment successful!')
                return render(request, 'payment_success.html', {'payment': payment})
            else:
                payment.payment_status = 'failed'
                payment.save()
                
                messages.error(request, 'Payment verification failed')
                return render(request, 'payment_failed.html')
        
    except Payment.DoesNotExist:
        messages.error(request, 'Payment record not found')
        return redirect('menu')
    except requests.exceptions.RequestException:
        messages.error(request, 'Network error during payment verification')
        return redirect('menu')



from django.shortcuts import get_object_or_404, redirect
def manage_pos_payments(request):
    orders = Order.objects.filter(payment_status='requesting')
    # Calculate total amount
    total_amount = sum(order.price for order in orders)
    
    context = {
        'orders': orders,
        'total_amount': total_amount,
        'pending_count': orders.count()
    }
    return render(request, 'manage_pos_payments.html', context)
def request_pos_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # Update the order with payment method and status
        order.payment_method = 'pos'
        order.payment_status = 'requesting'
        order.save()

        # Redirect the user to a confirmation page
        return render(request, 'pos_request_received.html', {'table_number': order.table_number})
from django.db.models import Sum

def manage_orders(request):
    orders = Order.objects.all().select_related('payment')
    tables = (
        orders.values('table_number')
        .annotate(total_price=Sum('price'))
        .order_by('table_number')
    )
    return render(request, 'orders.html', {'orders': orders, 'tables': tables})



def manage_bank_payments(request):
    # Use prefetch_related for ManyToManyField
    pending_payments = Payment.objects.filter(
        payment_status='pending'
    ).prefetch_related('orders')
    
    total_pending_amount = pending_payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        action = request.POST.get('action')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            
            if action == 'mark_completed':
                payment.payment_status = 'completed'
            elif action == 'mark_failed':
                payment.payment_status = 'failed'
                
            payment.save()
            
            messages.success(request, f'Payment {payment.payment_reference} marked as {payment.payment_status}')
            return redirect('manage_bank_payments')
            
        except Payment.DoesNotExist:
            messages.error(request, 'Payment not found')
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
    
    context = {
        'pending_payments': pending_payments,
        'total_pending_amount': total_pending_amount,
        'payment_statistics': {
            'completed': Payment.objects.filter(payment_status='completed').count(),
            'failed': Payment.objects.filter(payment_status='failed').count(),
            'pending': pending_payments.count(),
        }
    }
    
    return render(request, 'manage_bank_payments.html', context)
"""def manage_bank_payments(request):
    pending_payments = Payment.objects.filter(payment_status='pending').select_related('orders')
    total_pending_amount = pending_payments.aggregate(total=Sum('amount'))['total'] or 0
    
    return render(request, 'manage_bank_payments.html', {
        'pending_payments': pending_payments,
        'total_pending_amount': total_pending_amount,
    })"""

def bank_transfer_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # Simulate saving the payment reference (for manual verification by staff)
        payment_reference = request.POST.get('payment_reference')
        order.payment_method = 'transfer'
        order.payment_status = 'requesting'
        order.save()
        return redirect('manage_bank_payments')  # Redirect to a page for staff to verify the transfer
    return render(request, 'bank_transfer_form.html', {'order': order})


def mark_as_paid(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.payment_status = 'paid'
        order.status = 'delivered'  # Optionally update the order status
        order.save()
    return redirect('manage_pos_payments')




from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('menu')  # Redirect to menu or any other page

    return render(request, 'register.html')


from django.contrib.auth import authenticate, login

def login_view(request):
    # First check if user is already authenticated
    if request.user.is_authenticated:
        return redirect('menu')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check email format to determine user type
            if user.email.endswith('-staff@gmail.com'):
                user_type = 'staff'
            elif user.email.endswith('-admin@gmail.com'):
                user_type = 'admin'
            else:
                messages.error(request, "Unauthorized access!")
                return redirect('login')
            
            # If we get here, the user type is valid
            login(request, user)
            messages.success(request, f"Login successful! You are logged in as {user_type}.")
            return redirect('menu')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

from django.contrib.auth import logout

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.user.email.endswith('-staff@gmail.com'):
        return render(request, 'staff_dashboard.html')  # Staff dashboard
    elif request.user.email.endswith('-admin@gmail.com'):
        return render(request, 'admin_dashboard.html')  # Admin dashboard
    else:
        messages.error(request, "Unauthorized access!")
        return redirect('login')

@login_required
def mark_as_paidy(request, payment_id):
    if request.method == 'POST':
        payment = get_object_or_404(Payment, id=payment_id)
        payment.payment_status = 'paid'
        payment.save()
        
        # Update the order status if needed
        payment.order.status = 'paid'
        payment.order.save()
        
        messages.success(request, f"Payment for Order #{payment.order.id} has been verified successfully.")
    return redirect('manage_bank_payments')


def bank_transfer_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # Simulate a bank transfer payment request
        payment_reference = str(uuid.uuid4())
        Payment.objects.create(
            order=order,
            amount=order.price,
            payment_reference=payment_reference,
            payment_status='pending',  # Initially pending
        )
        messages.success(request, "Bank transfer request received. Staff will verify shortly.")
        return redirect('bank_details_view')  # Redirect users to the menu or another confirmation page





from django.shortcuts import render, get_object_or_404
from django.contrib import messages
import uuid

def bank_details_view(request, order_id):
    # Retrieve the order by ID
    order = get_object_or_404(Order, id=order_id)
    order_list = request.session.get('order_list', [])
    total_price = sum(item['price'] for item in order_list)
    # Static bank details
    bank_details = {
        'bank_name': 'GT Bank',
        'account_number': '647388933',
        'account_name': 'FOODIES PLACE',
    }

    if request.method == 'POST':
        # Generate a unique payment reference
        payment_reference = str(uuid.uuid4())

        # Create a Payment record
        Payment.objects.create(
            amount=order.price,
            payment_reference=payment_reference,
            payment_status='pending',  # Initially pending
        )

        # Show a success message
        messages.success(request, "Bank transfer request logged. Please use the details below to complete your payment.")

    # Always show the bank details page
    return render(request, 'bank_details.html', {
        'order': order,
        'bank_details': bank_details,
        'order_list': order_list,
        'total_price': total_price,
    })


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import MenuItem
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def menu_management(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'menu_management.html', {'menu_items': menu_items})

@require_http_methods(["GET"])
def get_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    return JsonResponse({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': str(item.price),
        'category': item.category,
        'image': item.image
    })

@require_http_methods(["POST"])
def create_menu_item(request):
    try:
        item = MenuItem.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
            price=request.POST['price'],
            category=request.POST['category'],
            image=request.FILES['image']
        )
        return JsonResponse({'success': True, 'id': item.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["PUT"])
def update_menu_item(request, item_id):
    try:
        item = get_object_or_404(MenuItem, id=item_id)
        item.name = request.POST['name']
        item.description = request.POST['description']
        item.price = request.POST['price']
        item.category = request.POST['category']
        item.image=request.FILES['image']
        item.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["DELETE"])
def delete_menu_item(request, item_id):
    try:
        item = get_object_or_404(MenuItem, id=item_id)
        item.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
"""def remove_from_order(request, item_id):
    if request.method == 'POST':
        order = Order.objects.get(id=request.session.get('order_id'))
        order_item = OrderItem.objects.get(id=item_id, order=order)
        order_item.delete()
        return redirect('menu')
    return redirect('menu')"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Q
from .models import StaffProfile, Department, Role, ProgressRecord, AssignmentHistory

def is_admin(user):
    return user.is_authenticated and user.email.endswith('-admin@gmail.com')


def staff_management(request):
    """Retrieve and display staff users"""
    # Filter users with staff email
    staff_users = User.objects.filter(email__endswith='-staff@gmail.com')
    
    # Create or update StaffProfile for each staff user
    staff_profiles = []
    for user in staff_users:
        # Create StaffProfile if it doesn't exist
        staff_profile, created = StaffProfile.objects.get_or_create(
            user=user,
            defaults={
                'department': None,
                'role': None,
                'is_active': True
            }
        )
        staff_profiles.append(staff_profile)

    context = {
        'staff_list': staff_profiles,
        'departments': Department.objects.all(),
        'roles': Role.objects.all(),
    }
    return render(request, 'staff_management.html', context)


def update_staff_assignment(request, staff_id):
    """API endpoint to update staff department or role"""
    if request.method == 'POST':
        staff_profile = get_object_or_404(StaffProfile, id=staff_id)
        data = json.loads(request.body)
        
        field = data.get('field')
        value = data.get('value')
        
        if field == 'department':
            staff_profile.department_id = value
        elif field == 'role':
            staff_profile.role_id = value
        
        staff_profile.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def add_staff_progress(request, staff_id):
    """API endpoint to add progress record for a staff member"""
    if request.method == 'POST':
        staff_profile = get_object_or_404(StaffProfile, id=staff_id)
        
        progress_record = ProgressRecord.objects.create(
            staff=staff_profile,
            evaluation_date=datetime.now(),
            performance_rating=request.POST.get('performance_rating'),
            tasks_completed=request.POST.get('tasks_completed'),
            comments=request.POST.get('comments'),
            evaluated_by=request.user
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})