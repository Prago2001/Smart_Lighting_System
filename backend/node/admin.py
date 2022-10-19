import imp
from django.contrib import admin
from .models import Slave,Schedule,Slot
# Register your models here.
admin.site.register(Slave)
admin.site.register(Slot)
admin.site.register(Schedule)
