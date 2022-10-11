from django.apps import AppConfig



class NodeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'node'

    def ready(self):
        try:
            from .Coordinator import MASTER
            from .models import Slave
            # Slave.objects.all().delete()
            # counter = Slave.objects.count()+1
            for node in MASTER.discover_nodes():
                if not Slave.objects.filter(unique_id = node._64bit_addr).exists():
                    slave = Slave(
                        unique_id = node._64bit_addr, 
                        # name = "Street Light "+str(counter),
                        name = node.node_name,
                        current = node.get_current_value(),
                        temperature = node.get_temperature_value(),
                        mains_val = node.get_mains_value(),
                        dim_val = node.get_dim_value()
                    )
                    # node.set_node_id("Street Light "+str(counter))
                    # counter+=1
                    slave.save()
                else:
                    slave = Slave.objects.get(unique_id=node._64bit_addr)

                    previous_mains_val = slave.mains_val
                    previous_dim_val = slave.dim_val
                    node.set_mains_value(previous_mains_val)
                    node.set_dim_value(previous_dim_val)

        except Exception as e:
            print(e)
            pass