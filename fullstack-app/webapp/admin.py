from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review
from . import admin_reports


# ---------- Экшены экспорта ----------

@admin.action(description="Экспорт выбранных заказов в Excel")
def export_orders_action(modeladmin, request, queryset):
    return admin_reports.orders_to_excel_response(queryset)


@admin.action(description="Экспорт выбранных товаров в Excel")
def export_products_action(modeladmin, request, queryset):
    return admin_reports.products_to_excel_response(queryset)


@admin.action(description="Экспорт выбранных отзывов в Excel")
def export_reviews_action(modeladmin, request, queryset):
    return admin_reports.reviews_to_excel_response(queryset)


# ---------- Каталог ----------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category")
    list_filter = ("category",)
    search_fields = ("name",)
    actions = [export_products_action]


# ---------- Заказы ----------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "is_paid")
    list_filter = ("is_paid", "created_at")
    inlines = [OrderItemInline]
    actions = [export_orders_action]


# ---------- Отзывы ----------

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "author", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "author__username", "text")
    actions = [export_reviews_action]