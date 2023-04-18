from django.apps import AppConfig



class NodeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'node'

    def ready(self):
        try:
            from .Coordinator import MASTER
            from .models import Slave,Schedule,Slot,Energy
            import datetime
            from .Scheduler import fetchSunModel,updater_start,add_dim_jobs_on_startup,sync_to_schedule
            from .Scheduler import add_sync_jobs
            from .views import changeSchedule
            from .utils import read_config_file, write_config_file, get_location
            get_location()
            # Slave.objects.all().delete()
            # This piece of code is to ensure that the last energy object
            # will get deleted as it will be having null values in 
            # end_time, consumption and saved
            last_energy_object = Energy.objects.last()
            if last_energy_object is not None:
                last_energy_object.delete()
            
            
            counter = Slave.objects.count()+1
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
                current_schedule = Schedule.objects.get(currently_active = True)
                
            except:

                try:
                    default_schedule = Schedule.objects.get(schedule_id = 1)
                except:
                    default_schedule = Schedule(schedule_id = 1,schedule_name = "Default",currently_active=True)
                    default_schedule.save()
                    s1 = Slot(
                        start=datetime.time(19,0,0),
                        end=datetime.time(21,0,0),
                        intensity=100,
                        schedule=default_schedule)
                    s2 = Slot(
                        start=datetime.time(21,0,0),
                        end=datetime.time(23,0,0),
                        intensity=50,
                        schedule=default_schedule)
                    s3 = Slot(
                        start=datetime.time(23,0,0),
                        end=datetime.time(5,0,0),
                        intensity=25,
                        schedule=default_schedule)
                    s4 = Slot(
                        start=datetime.time(5,0,0),
                        end=datetime.time(7,0,0),
                        intensity=75,
                        schedule=default_schedule)
                    s1.save()
                    s2.save()
                    s3.save()
                    s4.save()
                    print(Slot.objects.all())
                current_schedule = default_schedule

            read_config_file()

            fetchSunModel()
            updater_start()
            if MASTER.Schedule is True:
                sync_to_schedule(syncWithAutoInterval=True)
            
            # add_dim_jobs_on_startup()
            # add_sync_jobs()
            
            # print(scheduler.get_jobs())
            

            # Something to do with current_schedule

        except Exception as e:
            print(e,str(e))
            pass