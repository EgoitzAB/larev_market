from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'fecha_inicio', 'fecha_fin', 'discount', 'activo']
    list_filter = ['activo', 'fecha_inicio', 'fecha_fin']
    search_fields = ['code']