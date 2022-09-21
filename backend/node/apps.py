from django.apps import AppConfig

from .models import Slave

class NodeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'node'

    def ready(self):
        try:
            from .Coordinator import MASTER
            for node in MASTER.discover_nodes():
                print(node._64bit_addr)
                if not Slave.objects.filter(unique_id = node._64bit_addr).exists():
                    slave = Slave(unique_id = node._64bit_addr)
                    slave.save()
        except Exception as e:
            pass