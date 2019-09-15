from django.contrib import admin
from backend.models import BackendUser, Role, Permission, Menu
from customer.models import Buyer, Order

# Register your models here.
admin.site.register(BackendUser)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(Menu)

admin.site.register(Buyer)
admin.site.register(Order)
