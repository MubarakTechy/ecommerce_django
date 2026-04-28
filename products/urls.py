from django.urls import path
from django.contrib import admin
from . import views


urlpatterns = [    
    
    path('', views.Home, name='Home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('single-product/<int:product_id>/', views.single_product_view, name='single_product'),

]