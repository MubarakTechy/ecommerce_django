from itertools import product
from urllib import request

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Order, Product, Cart, Wishlist
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import update_session_auth_hash

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
def single_product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'Singleproduct.html', {
        'product': product
    })


@login_required
def order_view(request, product_id):
    product = Product.objects.get(id=product_id)

    Order.objects.create(
        user=request.user,
        product=product,
        quantity=1,
        price=product.price,
        status="pending"   # lowercase
    )

    return redirect("dashboard")


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

    total = sum(item.total_price() for item in cart_items)

    return render(request, "dashboard/", {
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