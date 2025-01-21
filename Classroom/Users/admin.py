from django.contrib import admin
from .models import CustomUser , Device
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Device)