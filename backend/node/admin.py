import imp
from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Slave)
admin.site.register(Slot)
admin.site.register(Schedule)
admin.site.register(CurrentMeasurement)
admin.site.register(TemperatureMeasurement)
