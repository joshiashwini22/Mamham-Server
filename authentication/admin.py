from django.contrib import admin
from authentication.models import Customer, Address, Notification
# Register your models here.

admin.site.register(
    [Customer, Address, Notification])