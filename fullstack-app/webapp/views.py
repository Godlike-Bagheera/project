from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

from .models import Product, Order, OrderItem, Review
from .forms import ReviewForm


# ---------- Каталог ----------

def index(request):
    products = Product.objects.all()
    return render(request, 'webapp/index.html', {'products': products})


# ---------- Аутентификация ----------

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'webapp/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'webapp/login.html', {'form': form})


# ---------- Корзина и заказы ----------

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, is_paid=False)
    order_item, item_created = OrderItem.objects.get_or_create(
        order=order, product=product,
        defaults={'price': product.price, 'quantity': 1},
    )
    if not item_created:
        order_item.quantity += 1
        order_item.save()

    messages.success(request, f"Товар '{product.name}' добавлен в корзину.")
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    order = Order.objects.filter(user=request.user, is_paid=False).first()
    return render(request, 'webapp/cart_detail.html', {'order': order})


@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, is_paid=False).first()
    if not order or not order.items.exists():
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('index')

    if request.method == 'POST':
        order.is_paid = True
        order.save()
        messages.success(request, "Заказ успешно оформлен! Спасибо за покупку.")
        return redirect('index')

    return render(request, 'webapp/checkout.html', {'order': order})


# ---------- Детальная страница товара и отзывы ----------

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()

    can_review = False
    if request.user.is_authenticated:
        bought = OrderItem.objects.filter(
            order__user=request.user,
            order__is_paid=True,
            product=product,
        ).exists()
        already_reviewed = Review.objects.filter(product=product, author=request.user).exists()
        can_review = bought and not already_reviewed

    if request.method == 'POST' and can_review:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.author = request.user
            review.save()
            messages.success(request, "Ваш отзыв добавлен!")
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'webapp/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'can_review': can_review,
    })


# ---------- Экспорт для пользователей (Фронтенд) ----------
import openpyxl
from .admin_reports import _fill_orders_workbook, _fill_products_workbook, _make_response

@login_required
def export_my_orders(request):
    """Скачивание истории заказов текущего пользователя"""
    qs = Order.objects.filter(user=request.user).select_related("user").prefetch_related("items__product").order_by("-created_at")
    wb = openpyxl.Workbook()
    _fill_orders_workbook(wb, qs)
    return _make_response(wb, f"my_orders_{request.user.username}")

def export_price_list(request):
    """Скачивание прайс-листа (всех товаров)"""
    qs = Product.objects.all().order_by("name")
    wb = openpyxl.Workbook()
    _fill_products_workbook(wb, qs)
    return _make_response(wb, "price_list")