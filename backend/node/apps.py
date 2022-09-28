from django.apps import AppConfig



class NodeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'node'

    def ready(self):
        try:
            from .Coordinator import MASTER
            from .models import Slave
            counter = Slave.objects.count()+1
            for node in MASTER.discover_nodes():
                print(node._64bit_addr)
                if not Slave.objects.filter(unique_id = node._64bit_addr).exists():
                    slave = Slave(
                        unique_id = node._64bit_addr, 
                        name = "Street Light "+str(counter),
                        current = node.get_current_value(),
                        temperature = node.get_temperature_value(),
                        mains_val = node.get_mains_value(),
                        dim_val = node.get_dim_value()
                    )
                    slave.save()
                    counter+=1
        except Exception as e:
            pass