from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product

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
def dashboard_view(request):
    return render(request, 'dashboard/index.html')


# Single Product View
def single_product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'Singleproduct.html', {
        'product': product
    })