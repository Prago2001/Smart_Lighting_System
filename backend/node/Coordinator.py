from time import sleep
from typing import List, Set
from digi.xbee.devices import ZigBeeDevice
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
    
    

MASTER = Coordinator()