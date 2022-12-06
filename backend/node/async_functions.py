
from .models import Slave
from time import sleep
try:
    from .Coordinator import MASTER
except Exception as e:
    pass



def perform_dimming(node_name,id,dim_value):
    #node = Slave.objects.get(unique_id=id)
    print(f"Starting thread in {node_name}")
    counter = 0
    while counter < 3:
        # time.sleep(0.5)
        remote = MASTER.get_node(node_name)
        if remote is not None:
            remote.set_dim_value(dim_value)
            print(f"Switching {dim_value} for {node_name}")
            return (True,id)
        counter += 1
        sleep(0.4)
        
    
    return (False,id)
    
    # if remote is None:
    #     node.is_active = False
    #     print(f"Unable to dim {node_name}")
    # else:
    #     node.is_active = True
            
    # node.dim_val = dim_value
    # node.save()
    # return node_name

def perform_toggle(node_name,id,mains_val):
    print(f"Starting thread in {node_name}")
    counter = 0
    while counter < 3:
        remote = MASTER.get_node(node_name)
        if remote is not None:
            remote.set_mains_value(mains_val)
            print(f"Toggling to {mains_val} for {node_name}")
            return (True,id)
        counter += 1
        sleep(0.4)
    
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
        sleep(0.4)
    
    return (id,False,0,0)
        