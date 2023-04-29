from .models import Category, Order, OrderItem
import json

def totalQuantity(request):
    if request.user.is_authenticated:
        customer = request.user.customer

        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        if order:
            qty = order.get_cart_items

        else:
            qty = 0

    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        qty = 0
        for item in cart:
            qty += cart[item]

    return {'qty': qty}

def categoryList(request):
    categories = Category.objects.all()

    return {'categories': categories}