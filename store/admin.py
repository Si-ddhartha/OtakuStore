from django.contrib import admin
from .models import *

# Register your models here.

# user = 'aniket'
# pass = 'otakustore'

admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
