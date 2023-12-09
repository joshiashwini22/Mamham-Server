from django.contrib import admin
from authentication.models import Customer, Address
# Register your models here.

admin.site.register(
    [Customer, Address])