from django.contrib import admin
from django.urls import path, include
from webapp import admin_reports

urlpatterns = [
    path(
        "admin/reports/",
        admin.site.admin_view(admin_reports.reports_index),
        name="admin-reports",
    ),
    path(
        "admin/reports/orders/",
        admin_reports.export_orders_excel,
        name="admin-reports-orders",
    ),
    # Новый маршрут для детализации продаж
    path(
        "admin/reports/sales/",
        admin_reports.export_sales_excel,
        name="admin-reports-sales",
    ),
    path(
        "admin/reports/products/",
        admin_reports.export_products_excel,
        name="admin-reports-products",
    ),
    path(
        "admin/reports/reviews/",
        admin_reports.export_reviews_excel,
        name="admin-reports-reviews",
    ),
    path("admin/", admin.site.urls),
    path("", include("webapp.urls")),
]