from django.urls import path
from django.contrib import admin
from . import views


urlpatterns = [    
    
    path('', views.Home, name='Home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('single-product/<int:product_id>/', views.single_product_view, name='single_product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path("order/<int:product_id>/", views.order_view, name="order_product"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/<int:wishlist_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
     path("profile/update/", views.update_profile, name="update_profile"),
     path("pay/<int:order_id>/", views.initiate_payment, name="pay"),
    path("payment/verify/", views.verify_payment, name="verify_payment"),
]