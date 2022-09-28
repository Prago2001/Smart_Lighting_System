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
        


