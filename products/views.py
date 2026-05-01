from itertools import product
from urllib import request

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Order, Product, Cart, Wishlist
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
import requests
from django.conf import settings
import uuid
import json

# Home
def Home(request):
    products = Product.objects.all()

    return render(request, 'Home.html', {
        'products': products
    })


# Signup
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            return render(request, 'auth/signup.html', {'error': 'Email already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('login')

    return render(request, 'auth/signup.html')


# Login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        return render(request, "auth/login.html", {"error": "Invalid credentials"})

    return render(request, "auth/login.html")


# Logout
def logout_view(request):
    logout(request)
    return redirect('login')


# Dashboard
@login_required
def dashboard_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    cart_items = Cart.objects.filter(user=request.user)
    wishlist_items = Wishlist.objects.filter(user=request.user)

    cart_total = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, "dashboard/index.html", {
        "orders": orders,
        "cart_items": cart_items,
        "wishlist_items": wishlist_items,
        "cart_total": cart_total
    })

# Single Product View
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]

    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products
    })

@login_required
def order_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    quantity = 1
    price = product.price
    total_price = price * quantity
    reference = str(uuid.uuid4())

    order = Order.objects.create(
        user=request.user,
        product=product,
        quantity=quantity,
        price=price,
        total_price=total_price,
        payment_reference=reference,
        payment_status="pending"
    )

    # ✅ go directly to payment
    return redirect("pay", order_id=order.id)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('dashboard')


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    total = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, "dashboard/index.html", {
        "cart_items": cart_items,
        "cart_total": total
    })

@login_required
def remove_from_cart(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)
    item.delete()
    return redirect("dashboard")

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('dashboard')


@login_required
def remove_from_wishlist(request, wishlist_id):
    item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    item.delete()
    return redirect('dashboard')



@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user

        username = request.POST.get("username")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # update username
        if username:
            user.username = username
            user.save()

        # update password safely
        if new_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # keeps user logged in
            else:
                return JsonResponse({"error": "Passwords do not match"}, status=400)

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request"}, status=400)






@login_required
def initiate_payment(request, order_id):
    order = Order.objects.get(id=order_id)

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": int(order.price * 100),  # Paystack uses kobo
        "callback_url": "http://127.0.0.1:8000/payment/verify/",
    }

    response = requests.post(url, json=data, headers=headers)
    res_data = response.json()

    if res_data["status"]:
        order.payment_reference = res_data["data"]["reference"]
        order.save()
        return redirect(res_data["data"]["authorization_url"])

    return redirect("dashboard")



@login_required
def verify_payment(request):
    reference = request.GET.get("reference")

    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data["status"]:
        order = Order.objects.get(payment_reference=reference)

        order.payment_status = "paid"
        order.status = "processing"
        order.save()

    return redirect("dashboard")

# @login_required
# def create_order(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     order = Order.objects.create(
#         user=request.user,
#         product=product,
#         quantity=1,
#         status="pending"
#     )

#     return redirect("pay_order", order_id=order.id)


import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404



@login_required
def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # ✅ Prevent paying twice
    if order.payment_status == "paid":
        return redirect("dashboard")

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": int(order.total_price * 100),
        "reference": order.payment_reference,
        "callback_url": "http://127.0.0.1:8000/payment/verify/",
    }

    response = requests.post(url, json=data, headers=headers)
    res_data = response.json()

    if res_data.get("status"):
        return redirect(res_data["data"]["authorization_url"])

    return redirect("dashboard")





@login_required
def verify_payment(request):
    reference = request.GET.get("reference")

    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data.get("status") and res_data["data"]["status"] == "success":
        try:
            order = Order.objects.get(payment_reference=reference)

            order.payment_status = "paid"
            order.status = "processing"
            order.save()

        except Order.DoesNotExist:
            pass

    return redirect("dashboard")
@login_required
def sync_cart(request):
    data = json.loads(request.body)
    cart_items = data.get("cart", [])

    for item in cart_items:
        product = Product.objects.get(id=item["id"])

        cart, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            cart.quantity += item["quantity"]
            cart.save()

    return JsonResponse({"status": "success"})
