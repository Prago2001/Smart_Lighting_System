from django.apps import AppConfig

class NodeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'node'

    def ready(self):
        try:
            from .Coordinator import MASTER
            for node in MASTER.discover_nodes():
                print(node._64bit_addr)
        except Exception as e:
            pass