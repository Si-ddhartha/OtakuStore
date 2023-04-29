from django.urls import path
from . import views

from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("register/", views.register_user, name="register"),
    path("verify/<str:token>", views.verify, name="verify"),
    path("login/", views.login_user, name="login"),
    path("logout/", LogoutView.as_view(next_page='home'), name="logout"),

    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path("products/<str:category>", views.products, name="products"),
    path("cart/", views.cart, name="cart"),
    path("delete_cart_item/<int:id>", views.delete_cart_item, name="delete_cart_item"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.update_item, name="update_item"),
    path("process_order/", views.process_order, name="process_order"),
    path("contact/", views.contact, name="contact"),
]