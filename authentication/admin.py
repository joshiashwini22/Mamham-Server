from django.contrib import admin
from authentication.models import Customer, Address, Notification, AdminUser
# Register your models here.

admin.site.register(
    [Customer, AdminUser, Address, Notification])