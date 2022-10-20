from time import sleep
from typing import List, Set
from digi.xbee.devices import ZigBeeDevice

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

        for node in Slave.objects.all():
            remote = self.get_node(node.name)
            if remote is None:
                node.is_active = False
            else:
                node.is_active = True
                remote.set_mains_value(True)
            node.mains_val = True
            node.save()
    
    def make_all_off(self):

        for node in Slave.objects.all():
            remote = self.get_node(node.name)
            if remote is None:
                node.is_active = False
            else:
                node.is_active = True
                remote.set_mains_value(False)
            node.mains_val = False
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
        if dim_value == 25:
            self.set_dim_25()
        elif dim_value == 50:
            self.set_dim_50()
        elif dim_value == 75:
            self.set_dim_75()
        elif dim_value == 100:
            self.set_dim_100()

MASTER = Coordinator()