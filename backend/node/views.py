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

@api_view(['GET'])
def discover_remote_nodes(request):
    for node in MASTER.discover_nodes():
        if not Slave.objects.filter(unique_id = node._64bit_addr).exists():
            slave = Slave(
                unique_id = node._64bit_addr, 
                name = node.node_name,
                current = node.get_current_value(),
                temperature = node.get_temperature_value(),
                mains_val = node.get_mains_value(),
                dim_val = node.get_dim_value()
            )
            slave.save()

    data_list = []
    for node in Slave.objects.all():
        remote = MASTER.get_node(node.name)
        if remote is None:
            node.is_active = False
            node.save()
        else:
            node.current = remote.get_current_value()
            node.temperature = remote.get_temperature_value()
            node.save()
        
        node_data = {
            'id' : node.name,
            'relay' : node.mains_val,
            'dim' : node.dim_val,
            'current' : node.current,
            'temp' : node.temperature,
            'is_active' : node.is_active,
        }
        data_list.append(node_data)
    return Response({'nodes':data_list})

@api_view(['GET','POST'])
def toggle_mains(request):
    if request.GET.get('isGlobal'):
        status = request.GET.get("status")

        if status == "on":
            switch_mains_value = True
        else:
            switch_mains_value = False


        for node in Slave.objects.all():
            remote = MASTER.get_node(node.name)
            if remote is None:
                node.is_active = False
            else:
                remote.set_mains_value(switch_mains_value)
            
            node.mains_val = switch_mains_value
            node.save()
    else:
        id = request.GET.get("id")
        status = request.GET.get("status")

        if status == "on":
            switch_mains_value = True
        else:
            switch_mains_value = False

        remote = MASTER.get_node(id)
        node = Slave.objects.get(name=id)
        if remote is None:
            node.is_active = False
            node.mains_val = switch_mains_value
            node.save()
            return Response({"message":f"Node {node.name} is inactive"})
        else:
            remote.set_mains_value(switch_mains_value)
            node.mains_val = switch_mains_value
            node.save()
    return Response({"message":"Success"})

@api_view(['GET','POST'])
def dim_to(request):
    if request.GET.get('isGlobal'):
        dim_to_value = int(request.GET.get("value"))



        for node in Slave.objects.all():
            remote = MASTER.get_node(node.name)
            if remote is None:
                node.is_active = False
            else:
                remote.set_dim_value(dim_to_value)
            
            node.dim_val = dim_to_value
            node.save()
    else:
        id = request.GET.get("id")
        dim_to_value = int(request.GET.get("value"))


        remote = MASTER.get_node(id)
        node = Slave.objects.get(name=id)
        if remote is None:
            node.is_active = False
            node.dim_val = dim_to_value
            node.save()
            return Response({"message":f"Node {node.name} is inactive"})
        else:
            remote.set_dim_value(dim_to_value)
            node.dim_val = dim_to_value
            node.save()
    return Response({"message":"Success"})