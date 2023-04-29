from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import JsonResponse
import json
import datetime
import random
import uuid
from .models import *
from .utils import cookieCart, cartData, guestOrder

from django.contrib.auth.models import User
from .forms import RegisterUserForm

from django.contrib.auth import authenticate, login

# For email verification 
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site


# Create your views here.
def send_activation_mail(request, user, token):
    domain = get_current_site(request)

    send_mail = EmailMessage(
        'Account activation mail.',
        render_to_string('store/mail_body.html', {
            'name':user.username,
            'domain':domain,
            'token':token,
        }),
        settings.EMAIL_HOST_USER,
        [user.email],
    )

    send_mail.fail_silently = False
    send_mail.send()
    print("Email sent successfully...")

def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterUserForm()

    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]

            # Checking if the user already exists
            if User.objects.filter(email=email).first():
                print("User exists......")
                messages.error(request, 'Email already exists. Please enter another email.')
                return redirect('register')        


            user = form.save()

            # Checking if the customer already exists
            if Customer.objects.filter(email=email).first():
                print("Guest customer with same email exists")
                guest_customer = Customer.objects.get(email=email)
                guest_customer.delete()
                print("Deleted guest customer")


            auth_token = uuid.uuid4()
            Customer.objects.create(user=user, name=username, email=email, auth_token=auth_token)


            send_activation_mail(request, user, auth_token)


            messages.success(request, 'Account Created.')
            return redirect('login')
        
    
    context = {'form':form}
    return render(request, 'store/register.html', context)

def verify(request, token):
    try:
        customer = Customer.objects.filter(auth_token=token).first()

        if customer:
            if customer.is_verified:
                messages.info(request, "Your account is already verified.")
                return redirect('login')
            
            else:
                customer.is_verified = True
                customer.save()
                messages.info(request, "Your account has been verified. Please login.")
                return redirect('login')

    except Exception as e:
        print(e)

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not Customer.objects.filter(user=user).first().is_verified:
                messages.error(request, "Your account is not verified. Please click on the link sent to your mail to activate your account.")
                return redirect('login')

            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, "Invalid Credentials.")
            return redirect('login')

    context = {}
    return render(request, 'store/login.html', context)

def home(request):
    print("User:", request.user)
    products = list(Product.objects.all())
    products = random.sample(products, 9)
    # products = Product.objects.all()[1:7]
    # category_id = request.GET.get('category')

    # if category_id:
    #     products = Product.objects.filter(category=category_id)
    # else:
    #     products = list(Product.objects.all())
    #     products = random.sample(products, 6)

    context = {'products':products}
    return render(request, "store/home.html", context)

def products(request, category=""):
    if category:
        category_id = Category.objects.filter(name=category).values('id')[0]['id']
        products = Product.objects.filter(category=category_id)
    
    else:
        products = list(Product.objects.all())
        random.shuffle(products)

    context = {'products':products}
    return render(request, "store/products.html", context)

def contact(request):
    context = {}

    return render(request, "store/contact.html", context)

def cart(request):
    data = cartData(request)
    # print(data)

    context = {'items':data['items'], 'order':data['order']}
    return render(request, "store/cart.html", context)

def checkout(request):
    data = cartData(request)

    context = {'items':data['items'], 'order':data['order']}
    return render(request, "store/checkout.html", context)


from .context_processor import totalQuantity
def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print(productId)
    print(action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    qty = totalQuantity(request)
    info = {'qty':qty}

    return JsonResponse(info, safe=False)

def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    print("Data: ", data)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    print("Front-end total = ", total)
    print("Back-end total = ", order.get_cart_total)
    if total == float(order.get_cart_total):
        print("Order Completed...")
        order.complete = True
    order.save()

    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
    )

    return JsonResponse('Payment Complete!!!', safe=False)

def delete_cart_item(request, id):
    # cart_item = OrderItem.objects.get(id=id)
    customer = request.user.customer
    order = Order.objects.get(customer=customer, complete=False)
    print(order)
    if OrderItem.objects.get(order=order, id=id):
        print("Item Exists")
        OrderItem.objects.get(order=order, id=id).delete()
        order.save()
        print("Item deleted")
    
    else:
        print("Item not found")

    return redirect('cart')
