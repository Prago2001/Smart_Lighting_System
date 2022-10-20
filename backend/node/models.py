from email.policy import default
from django.db import models

class Slave(models.Model):
    unique_id = models.CharField(max_length=20,unique=True,primary_key=True)
    name = models.CharField(max_length=255,default="Street Light ")
    is_active = models.BooleanField(default=True)
    mains_val = models.BooleanField(default=False)
    dim_val = models.IntegerField(default=25,choices=
    [   
        (0,"0"),
        (25,"25"),
        (50,"50"),
        (75,"75"),
        (100,"100")
    ])
    temperature = models.FloatField(null=True)
    current = models.FloatField(null=True)
    last_modified = models.DateTimeField(auto_now=True)
    # coordinator_id if needed

    def __str__(self):
        return self.name


class Schedule(models.Model):
    schedule_id = models.IntegerField(primary_key=True)
    schedule_name = models.CharField(max_length = 100)
    currently_active = models.BooleanField(default = False)

    def __str__(self):
        return self.schedule_name


class Slot(models.Model):
    start = models.TimeField()
    end = models.TimeField()
    intensity = models.IntegerField(default=25,choices=
    [   
        (0,"0"),
        (25,"25"),
        (50,"50"),
        (75,"75"),
        (100,"100")
    ])
    schedule = models.ForeignKey(Schedule,on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.schedule}-{self.id}"

class CurrentMeasurement(models.Model):
    SlaveId = models.ForeignKey(Slave,on_delete = models.CASCADE)
    dateTimeStamp = models.DateTimeField(auto_now_add = True)
    currentValue = models.FloatField()

class TemperatureMeasurement(models.Model):
    SlaveId = models.ForeignKey(Slave,on_delete = models.CASCADE)
    dateTimeStamp = models.DateTimeField(auto_now_add = True)
    temperatureValue = models.FloatField()
'''
import datetime
  
# time(hour = 0, minute = 0, second = 0)
d = datetime.time(10, 33, 45)

geek_object = GeeksModel.objects.create(geeks_field = d)
geek_object.save()

'''