import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    items = []
    order = {'get_cart_total': 0}

    for i in cart:
        product = Product.objects.get(id=i)

        total = product.price * cart[i]

        order['get_cart_total'] += total

        item = {
            'product':{
                'id':product.id,
                'name':product.name,
                'price':product.price,
                'image':product.image
            },
            'quantity':cart[i],
            'get_total':total
        }

        items.append(item)

    return {'items':items, 'order':order}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all() 
    
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']

    return {'items':items, 'order':order}

def guestOrder(request, data):
    print("User is not logged in...")

    print("Cookies: ", request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])

    return customer, order