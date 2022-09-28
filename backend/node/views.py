from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Slave


try:
    from .Coordinator import MASTER
except Exception as e:
    pass

# Create your views here.
@api_view(['GET'])
def get_nodes(request):
    data_list = []
    for node in Slave.objects.all():
        node_data = {
            'id' : node.name,
            'relay' : node.mains_val,
            'dim' : node.dim_val,
            'current' : node.current,
            'temp' : node.temperature,
            'is_active' : node.is_active,
        }
        data_list.append(node_data)
    return Response({'nodes': data_list})