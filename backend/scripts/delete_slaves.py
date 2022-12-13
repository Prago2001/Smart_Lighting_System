from node.models import *

def run():
    Slave.objects.all().delete()