from time import sleep
from typing import List, Set
from digi.xbee.devices import ZigBeeDevice
from .async_functions import perform_dimming,perform_toggle
import concurrent.futures
from .models import Slave
from .Remote import Remote

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Coordinator(metaclass=Singleton):
    def __init__(self):
        self.master = ZigBeeDevice("/dev/ttyUSB0",9600)
        self.master.open()
        self.network = self.master.get_network()
        self.SunRise = None
        self.SunSet = None
        self.Telemetry = True
        self.Schedule = True  # Variables are for telemetry,enable schedule button

    def discover_nodes(self) -> List[Remote]:
        self.nodes : List[Remote] = []
        self.network.start_discovery_process()
        while self.network.is_discovery_running():
            sleep(0.1)
        for node in self.network.get_devices():
            print(node)
            try:
                self.nodes.append(Remote(node))
            except:
                pass
        return self.nodes
    
    def get_node(self,node_name:str):
        node = self.network.discover_device(node_name)
        if node is None:
            return None
        else:
            return Remote(node=node)
    
    def make_all_on(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            threads = [executor.submit(fn=perform_toggle,node_name=node.name,id=node.unique_id,mains_val=True) for node in Slave.objects.all()]
            for f in concurrent.futures.as_completed(threads):
                status, id = f.result()
                node = Slave.objects.get(unique_id=id)
                if status is True:
                    node.is_active = True
                    node.mains_val = True
                else:
                    print(f"Unable to toggle {node.name}")
                    node.is_active = False
                node.save()
    
    def make_all_off(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            threads = [executor.submit(fn=perform_toggle,node_name=node.name,id=node.unique_id,mains_val=False) for node in Slave.objects.all()]
            for f in concurrent.futures.as_completed(threads):
                status, id = f.result()
                node = Slave.objects.get(unique_id=id)
                if status is True:
                    node.is_active = True
                    node.mains_val = False
                else:
                    print(f"Unable to toggle {node.name}")
                    node.is_active = False
                node.save()

    def set_dim_25(self):
        for node in Slave.objects.all():
            remote = self.get_node(node.name)
            if remote is None:
                node.is_active = False
            else:
                node.is_active = True
                remote.set_dim_value(25)
            
            node.dim_val = 25
            node.save()


    def set_dim_50(self):
        for node in Slave.objects.all():
            remote = self.get_node(node.name)
            if remote is None:
                node.is_active = False
            else:
                node.is_active = True
                remote.set_dim_value(50)

            node.dim_val = 50
            node.save()
        
    def set_dim_75(self):
        for node in Slave.objects.all():
            remote = self.get_node(node.name)
            if remote is None:
                node.is_active = False
            else:
                node.is_active = True
                remote.set_dim_value(75)
            
            node.dim_val = 75
            node.save()

    def set_dim_100(self):
        for node in Slave.objects.all():
            remote = self.get_node(node.name)
            if remote is None:
                node.is_active = False
            else:
                node.is_active = True
                remote.set_dim_value(100)

            node.dim_val = 100
            node.save()
    
    def set_dim_value(self,dim_value):
        # print("Dim Value - Scheduler: ",dim_value)
        # if dim_value == 25:
        #     self.set_dim_25()
        # elif dim_value == 50:
        #     self.set_dim_50()
        # elif dim_value == 75:
        #     self.set_dim_75()
        # elif dim_value == 100:
        #     self.set_dim_100()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            threads = [executor.submit(fn=perform_dimming,node_name=node.name,id=node.unique_id,dim_value=dim_value) for node in Slave.objects.all()]
            for f in concurrent.futures.as_completed(threads):
                status, id = f.result()
                node = Slave.objects.get(unique_id=id)
                if status is True:
                    node.is_active = True
                    node.dim_val = dim_value
                else:
                    print(f"Unable to dim {node.name}")
                    node.is_active = False
                node.save()

MASTER = Coordinator()