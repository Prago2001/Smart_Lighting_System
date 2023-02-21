from time import sleep
from typing import List, Set
from digi.xbee.devices import ZigBeeDevice
import concurrent.futures
from .models import Slave
from .Remote import Remote



def retry_mains(nodes,mains_val):
    MASTER.failed_nodes = []
    for node_name,id in nodes.items():
        remote = MASTER.get_node(node_name)
        node = Slave.objects.get(unique_id=id)
        if remote is not None:
            try:
                remote.set_mains_value(mains_val)
            except Exception as e:
                node.is_active = False
                node.save()
                print(f"Unable to toggle {node.name}")
                MASTER.failed_nodes.append(node.name)
                continue
            node.mains_val = mains_val
            node.is_active = True
            print(f"Switching {mains_val} for {node_name}")
        else:
            print(f"Unable to toggle {node.name}")
            node.is_active = False
            MASTER.failed_nodes.append(node.name)
        node.save()
        sleep(2)
    MASTER.manualJobStatus = False
    MASTER.scheduledJobStatus = False

def retry_dim(nodes,dim_val):
    MASTER.failed_nodes = []
    for node_name,id in nodes.items():
        remote = MASTER.get_node(node_name)
        node = Slave.objects.get(unique_id=id)
        if remote is not None:
            try:
                remote.set_dim_value(dim_val)
            except Exception as e:
                node.is_active = False
                node.save()
                print(f"Unable to dim {node.name}")
                MASTER.failed_nodes.append(node.name)
                continue
            node.dim_val = dim_val
            node.is_active = True
            print(f"Switching {dim_val} for {node_name}")
        else:
            print(f"Unable to dim {node.name}")
            node.is_active = False
            MASTER.failed_nodes.append(node.name)
        node.save()
        sleep(2)
    MASTER.manualJobStatus = False
    MASTER.scheduledJobStatus = False

def perform_dimming(node_name,id,dim_value):
    print(f"Starting thread in {node_name}")
    counter = 0
    while counter < 4:
        # time.sleep(0.5)
        try:
            remote = MASTER.get_node(node_name)
            if remote is not None:
                remote.set_dim_value(dim_value)
                print(f"Switching {dim_value} for {node_name}")
                return (True,id)
        except Exception as e:
            pass
        counter += 1
        if counter == 1:
            sleep(2)
        elif counter == 2:
            sleep(3)
        elif counter == 3:
            sleep(5)
    return (False,id)

def perform_toggle(node_name,id,mains_val):
    print(f"Starting thread in {node_name}")
    counter = 0
    while counter < 4:
        try:
            remote = MASTER.get_node(node_name)
            if remote is not None:
                remote.set_mains_value(mains_val)
                print(f"Toggling to {mains_val} for {node_name}")
                return (True,id)
        except Exception as e:
            pass
        counter += 1
        if counter == 1:
            sleep(2)
        elif counter == 2:
            sleep(3)
        elif counter == 3:
            sleep(5)
    return (False,id)
    
    

def get_curr_temp_val_async(node_name,id):
    
    counter = 0
    while counter < 3:
        remote = MASTER.get_node(node_name) 
        if remote is not None:
            try:
                temp = remote.get_temperature_value() 
                curr = remote.get_current_value()
                return (id,True,temp,curr)

            except Exception as e:
                print(str(e))
        counter+=1
        sleep(1)
    
    return (id,False,0,0)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Coordinator(metaclass=Singleton):
    def __init__(self):
        # self.master = ZigBeeDevice("/dev/ttyUSB0",9600)
        # self.master.open()
        # self.network = self.master.get_network()
        self.SunRise = None
        self.SunSet = None
        self.Telemetry = True
        self.Schedule = True  # Variables are for telemetry,enable schedule button
        self.manualJobStatus = False # If true then manual operation for some nodes has failed and job has been scheduled. After job is executed it will get toggled to False
        self.scheduledJobStatus = False
        self.failed_nodes = []

    def discover_nodes(self) -> List[Remote]:
        self.nodes : List[Remote] = []
        try:
            self.network.start_discovery_process()
            while self.network.is_discovery_running():
                sleep(3)
            for node in self.network.get_devices():
                print(node)
                try:
                    self.nodes.append(Remote(node))
                except:
                    pass
        except Exception as e:
            print(f"Error in discover_nodes: {e}")
            pass
        return self.nodes
    
    def get_node(self,node_name:str):
        node = self.network.discover_device(node_name)
        if node is None:
            return None
        else:
            return Remote(node=node)
    
    def make_all_on(self):
        failed_nodes = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            threads = [executor.submit(perform_toggle,node_name=node.name,id=node.unique_id,mains_val=True) for node in Slave.objects.all().order_by('is_active')]
            for f in concurrent.futures.as_completed(threads):
                status, id = f.result()
                node = Slave.objects.get(unique_id=id)
                if status is True:
                    node.is_active = True
                    node.mains_val = True
                else:
                    print(f"Unable to toggle {node.name}")
                    node.is_active = False
                    failed_nodes[node.name] = node.unique_id
                node.save()
        return failed_nodes
            
    
    def make_all_off(self):
        failed_nodes = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            threads = [executor.submit(perform_toggle,node_name=node.name,id=node.unique_id,mains_val=False) for node in Slave.objects.all().order_by('is_active')]
            for f in concurrent.futures.as_completed(threads):
                status, id = f.result()
                node = Slave.objects.get(unique_id=id)
                if status is True:
                    node.is_active = True
                    node.mains_val = False
                else:
                    print(f"Unable to toggle {node.name}")
                    node.is_active = False
                    failed_nodes[node.name] = node.unique_id
                node.save()
        return failed_nodes
    
    def set_dim_value(self,dim_value):
        failed_nodes = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            threads = [executor.submit(perform_dimming,node_name=node.name,id=node.unique_id,dim_value=dim_value) for node in Slave.objects.all().order_by('is_active')]
            for f in concurrent.futures.as_completed(threads):
                status, id = f.result()
                node = Slave.objects.get(unique_id=id)
                if status is True:
                    node.is_active = True
                    node.dim_val = dim_value
                else:
                    print(f"Unable to dim {node.name}")
                    node.is_active = False
                    failed_nodes[node.name] = node.unique_id
                node.save()
        return failed_nodes

MASTER = Coordinator()