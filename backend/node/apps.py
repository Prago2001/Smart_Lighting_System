from django.apps import AppConfig



class NodeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'node'

    def ready(self):
        try:
            from .Coordinator import MASTER
            from .models import Slave,Schedule,Slot
            import datetime
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
            try:
                current_schedule = Schedule.objects.get(current = True)
                
            except:

                try:
                    default_schedule = Schedule.objects.get(schedule_id = 1)
                except:
                    default_schedule = Schedule(schedule_id = 1,schedule_name = "Default")
                    default_schedule.save()
                    s1 = Slot(datetime.time(18,0,0),datetime.time(20,0,0),75,1)
                    s2 = Slot(datetime.time(20,0,0),datetime.time(22,0,0),100,1)
                    s3 = Slot(datetime.time(22,0,0),datetime.time(0,0,0),75,1)
                    s4 = Slot(datetime.time(0,0,0),datetime.time(3,0,0),50,1)
                    s5 = Slot(datetime.time(3,0,0),datetime.time(6,0,0),50,1)
                    s1.save()
                    s2.save()
                    s3.save()
                    s4.save()
                    s5.save()
                current_schedule = default_schedule

            # Something to do with current_schedule

        except Exception as e:
            print(e)
            pass