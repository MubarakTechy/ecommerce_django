from django.contrib import admin
from .models import Category, Product, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'product',
        'quantity',
        'price',
        'total_price',
        'status',
        'payment_status',
        'created_at'
    )

    list_filter = (
        'status',
        'payment_status',
        'created_at'
    )

    search_fields = (
        'user__username',
        'product__name',
        'payment_reference'
    )