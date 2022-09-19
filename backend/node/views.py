from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


try:
    from .Coordinator import MASTER
except Exception as e:
    pass

# Create your views here.
@api_view(['GET'])
def get_nodes(request):
    data_list = []
    for node in MASTER.nodes:
        node_data = {
            'id' : node._64bit_addr,
            'relay' : False,
            'dim' : 25,
            'current' : 50,
            'temp' : 30
        }
        data_list.append(node_data)
    return Response({'nodes': data_list})