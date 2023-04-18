import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from astral import LocationInfo
from astral.sun import sun
from .models import Schedule, Slot, CurrentMeasurement, TemperatureMeasurement,Slave,Notification
from datetime import timedelta
from .Coordinator import get_curr_temp_val_async,retry_dim,retry_mains
import concurrent.futures
from django.utils.timezone import get_current_timezone
from apscheduler.job import Job
from .utils import write_end_time_energy,write_start_time_energy,update_energy_config_file
try:
    from .Coordinator import MASTER
except Exception as e:
    pass

TOGGLE_SUCCESS = "Lights switched {} successfully."
TOGGLE_FAILURE = "Switching {} lights failed for the following nodes: "
DIM_SUCCESS = 'Lights dimmed to {}% successfully.'
DIM_FAILURE = 'Dimming lights to {}% failed for the following nodes: '

function_mapping = {
    'set_dim_to' : MASTER.set_dim_value,
    'make_all_on' : MASTER.make_all_on,
    'make_all_off':MASTER.make_all_off,
}

scheduler = BackgroundScheduler()

# in startup :

def getInsValues():
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        threads = [executor.submit(get_curr_temp_val_async,node_name=node.name,id=node.unique_id) for node in Slave.objects.all()]
        for f in concurrent.futures.as_completed(threads):
            id, status, temp, curr = f.result()
            node = Slave.objects.get(unique_id=id)
            if status is True:
                CurrentMeasurement.objects.create(SlaveId = node,currentValue = curr)
                TemperatureMeasurement.objects.create(SlaveId = node,temperatureValue = temp)
                node.current = curr
                node.temperature = temp
                node.is_active = True
                node.save()
            else:
                node.is_active = False
                node.save()
        

def fetchSunModel() :

    city = LocationInfo(name="pune", region="India", timezone="Asia/Kolkata", latitude=18.6452489, longitude=73.92318563785392)
    s = sun(city.observer, tzinfo=city.timezone)
    MASTER.sunrise_timestamp = s['sunrise']
    MASTER.sunset_timestamp = s['sunset']
    MASTER.SunRise = s["sunrise"].strftime("%H:%M")
    MASTER.SunSet = s["sunset"].strftime("%H:%M")
# Coordinator().autoSchedule[0]['from'] = s["sunset"]
# Coordinator().autoSchedule[-1]['to'] = s["sunrise"]

    # current_schedule = Schedule.objects.get(currently_active = True)
    for current_schedule in Schedule.objects.all():
        slots=Slot.objects.filter(schedule=current_schedule).order_by('id')
        count = 0
        for slot in slots:
            if count == 0:
                slot.start = datetime.time(s["sunset"].hour,s["sunset"].minute,s["sunset"].second)
                slot.save()
            elif count == len(slots) - 1:
                slot.end = datetime.time(s["sunrise"].hour,s["sunrise"].minute,s["sunrise"].second)
                slot.save()
            count += 1

    # Changing scheduled job at sunrise
    if MASTER.Schedule is True:
        scheduler.add_job(
                            sync_to_schedule,
                            kwargs={'syncWithAutoInterval' : False,
                                    'relay':False,
                                    'run_time':MASTER.sunrise_timestamp},
                            trigger='cron',
                            id = "sync_sunrise",
                            hour = s["sunrise"].hour,
                            minute = s["sunrise"].minute,
                            timezone = 'Asia/Kolkata',
                            replace_existing=True,
                            name='sync_to_schedule'
        )
        # Changing scheduled job at sunset
        scheduler.add_job(
                            sync_to_schedule,
                            kwargs={'syncWithAutoInterval' : False,
                                    'relay':True,
                                    'run_time':MASTER.sunset_timestamp},
                            trigger='cron',
                            id = "sync_sunset",
                            hour = s["sunset"].hour,
                            minute = s["sunset"].minute,
                            timezone = 'Asia/Kolkata',
                            replace_existing=True,
                            name='sync_to_schedule'
        )




def updater_start():
    try:
        scheduler.add_job(fetchSunModel, 'cron', id='sunmodel', hour=0, minute=15, timezone='Asia/Kolkata',name='sunrise_sunset_values')
        scheduler.add_job(
            delete_logs,
            trigger='interval',
            id='delete_logs',
            name="Delete logs after every 24 hours",
            days=1,
            next_run_time=datetime.datetime.combine(datetime.date.today() + timedelta(days=1),datetime.time(hour=1),tzinfo=get_current_timezone()),
            timezone='Asia/Kolkata'
        )
        scheduler.add_job(
            update_energy_config_file,
            trigger='interval',
            id="update_energy_saved",
            name="Update energy saved after every 24 hours",
            days=1,
            next_run_time=datetime.datetime.combine(datetime.date.today() + timedelta(days=1),datetime.time(hour=8),tzinfo=get_current_timezone()),
            timezone='Asia/Kolkata'
        )
        if MASTER.Telemetry is True:
            scheduler.add_job(getInsValues, 'interval', seconds=120, id='inst_values',name='current_temperature_values')
        else:
            scheduler.add_job(getInsValues, 'interval', seconds=120, id='inst_values',name='current_temperature_values',next_run_time=None)
        add_sync_jobs()
        if MASTER.syncWithAuto is True:
            scheduler.add_job(
                sync_to_schedule,
                kwargs={'syncWithAutoInterval' : True},
                trigger='interval',
                minutes=MASTER.syncWithAutoInterval,
                id='sync_to_auto',
                name='sync_every_half_hour',
                timezone='Asia/Kolkata'
            )
        else:
            scheduler.add_job(
                sync_to_schedule,
                trigger='interval',
                kwargs={'syncWithAutoInterval' : True},
                minutes=MASTER.syncWithAutoInterval,
                id='sync_to_auto',
                name='sync_every_half_hour',
                timezone='Asia/Kolkata',
                next_run_time=None
            )
        scheduler.start()
        if MASTER.Schedule is False:
            job:Job
            for job in scheduler.get_jobs():
                if job.name in ('dimming_job','sync_to_schedule','sync_every_half_hour'):
                    job.pause()
        scheduler.print_jobs()
    except Exception as e:
        print("Error in updater_start: ",e)



def add_dim_jobs_on_startup():
    current_active_schedule = Schedule.objects.get(currently_active=True)
    slots = Slot.objects.filter(schedule=current_active_schedule).order_by('id')
    job_count = 0
    try:
        for slot in slots:
            scheduler.add_job(
                    function_mapping['set_dim_to'],
                    args=[slot.intensity],
                    trigger='cron',
                    id = slot.__str__(),
                    hour = slot.start.hour,
                    minute = slot.start.minute,
                    timezone = 'Asia/Kolkata',
                    replace_existing=True,
                    name='dimming_job'
                )
    except Exception as e:
        print(e)
    


def sync_to_schedule(syncWithAutoInterval:bool,intensity=None,relay=None,run_time=None):
    current_time = datetime.datetime.now().strftime("%H:%M")
    sunset = MASTER.SunSet
    sunrise = MASTER.SunRise
    if syncWithAutoInterval is True:
        operationType = ('information','information')
    else:
        operationType = ('toggle','dim')


    if current_time >= sunset or current_time < sunrise:
        
        current_schedule = Schedule.objects.get(currently_active = True)
        slots = Slot.objects.filter(schedule=current_schedule).order_by('id')

        failed_nodes = MASTER.make_all_on()      
        if len(failed_nodes) > 0 :
            MASTER.scheduledJobStatus = True
            scheduler.add_job(
                func=retry_mains,
                trigger='date',
                args=[failed_nodes,True,],
                id='retry_auto_mains',
                name="Retrying mains operation in auto mode",
                replace_existing=True,
                run_date=datetime.datetime.now() + timedelta(seconds=15),
                timezone = 'Asia/Kolkata',
            )
        while MASTER.scheduledJobStatus is True:
            continue
        if len(MASTER.failed_nodes) > 0:
            msg = ", ".join(MASTER.failed_nodes)
            Notification.objects.create(
                operation_type=operationType[0],
                success = False,
                message = TOGGLE_FAILURE.format("ON") + msg,
                timestamp=datetime.datetime.now(tz=get_current_timezone())
            )
        else:
            Notification.objects.create(
                operation_type=operationType[0],
                success = True,
                message = TOGGLE_SUCCESS.format("ON"),
                timestamp=datetime.datetime.now(tz=get_current_timezone())
            )
        MASTER.failed_nodes = []

        for slot in slots:
            start = slot.start.strftime("%H:%M")
            end = slot.end.strftime("%H:%M")

            if start < end:
                if start <= current_time < end:
                    failed_nodes = MASTER.set_dim_value(slot.intensity)
                    write_end_time_energy()
                    write_start_time_energy(slot.intensity,mains=True)
                    if len(failed_nodes) > 0 :
                        MASTER.scheduledJobStatus = True
                        scheduler.add_job(
                            func=retry_dim,
                            trigger='date',
                            args=[failed_nodes,slot.intensity,],
                            id='retry_auto_dim',
                            name="Retrying dim operation in auto mode",
                            replace_existing=True,
                            run_date=datetime.datetime.now() + timedelta(seconds=15),
                            timezone = 'Asia/Kolkata',
                        )
                    while MASTER.scheduledJobStatus is True:
                        continue
                    if len(MASTER.failed_nodes) > 0:
                        msg = ", ".join(MASTER.failed_nodes)
                        Notification.objects.create(
                            operation_type=operationType[1],
                            success = False,
                            message = DIM_FAILURE.format(slot.intensity) + msg,
                            timestamp=datetime.datetime.now(tz=get_current_timezone())
                        )
                    else:
                        Notification.objects.create(
                            operation_type=operationType[1],
                            success = True,
                            message = DIM_SUCCESS.format(slot.intensity),
                            timestamp=datetime.datetime.now(tz=get_current_timezone())
                        )
                    break

            else:
                if current_time >= start or current_time < end:
                    failed_nodes = MASTER.set_dim_value(slot.intensity)
                    write_end_time_energy()
                    write_start_time_energy(slot.intensity,mains=True)
                    if len(failed_nodes) > 0 :
                        MASTER.scheduledJobStatus = True
                        scheduler.add_job(
                            func=retry_dim,
                            trigger='date',
                            args=[failed_nodes,slot.intensity,],
                            id='retry_auto_dim',
                            name="Retrying dim operation in auto mode",
                            replace_existing=True,
                            run_date=datetime.datetime.now() + timedelta(seconds=15),
                            timezone = 'Asia/Kolkata',
                        )
                    while MASTER.scheduledJobStatus is True:
                        continue
                    if len(MASTER.failed_nodes) > 0:
                        msg = ", ".join(MASTER.failed_nodes)
                        Notification.objects.create(
                            operation_type=operationType[1],
                            success = False,
                            message = DIM_FAILURE.format(slot.intensity) + msg,
                            timestamp=datetime.datetime.now(tz=get_current_timezone())
                        )
                    else:
                        Notification.objects.create(
                            operation_type=operationType[1],
                            success = True,
                            message = DIM_SUCCESS.format(slot.intensity),
                            timestamp=datetime.datetime.now(tz=get_current_timezone())
                        )
                    break
        MASTER.failed_nodes = []
    else:
        failed_nodes = MASTER.make_all_off()
        write_end_time_energy()
        write_start_time_energy(intensity=0,mains=False)
        if len(failed_nodes) > 0:
            MASTER.scheduledJobStatus = True
            scheduler.add_job(
                func=retry_mains,
                trigger='date',
                args=[failed_nodes,False,],
                id='retry_auto_mains',
                name="Retrying mains operation in auto mode",
                replace_existing=True,
                run_date=datetime.datetime.now() + timedelta(seconds=15),
                timezone = 'Asia/Kolkata',
            )
            while MASTER.scheduledJobStatus is True:
                continue
        if len(MASTER.failed_nodes) > 0:
            msg = ", ".join(MASTER.failed_nodes)
            Notification.objects.create(
                operation_type=operationType[0],
                success = False,
                message = TOGGLE_FAILURE.format("OFF") + msg,
                timestamp=datetime.datetime.now(tz=get_current_timezone())
            )
        else:
            Notification.objects.create(
                operation_type=operationType[0],
                success = True,
                message = TOGGLE_SUCCESS.format("OFF"),
                timestamp=datetime.datetime.now(tz=get_current_timezone())
            )
        MASTER.failed_nodes = []


def add_sync_jobs():
    # Remove Previous jobs
    try:
        for job in scheduler.get_jobs():
            if job.name == 'sync_to_schedule':
                job.remove()
    except Exception as e:
        print("In add sync jobs: ",str(e))
    current_active_schedule = Schedule.objects.get(currently_active=True)
    slots = Slot.objects.filter(schedule=current_active_schedule).order_by('id')
    for slot in slots:
        
        if slot.start.strftime("%H:%M") == MASTER.SunSet:
            scheduler.add_job(
                        sync_to_schedule,
                        kwargs={'syncWithAutoInterval' : False,
                                'relay':True,
                                'run_time':MASTER.sunset_timestamp},
                        trigger='cron',
                        id = "sync_sunset",
                        hour = slot.start.hour,
                        minute = slot.start.minute,
                        timezone = 'Asia/Kolkata',
                        replace_existing=True,
                        name='sync_to_schedule'
            )
        else:
            id = "sync_" + slot.__str__()        
            scheduler.add_job(
                        sync_to_schedule,
                        kwargs={'syncWithAutoInterval' : False,
                                'relay':True,
                                'intensity':slot.intensity,
                                'run_time':slot.start},
                        trigger='cron',
                        id = id,
                        hour = slot.start.hour,
                        minute = slot.start.minute,
                        timezone = 'Asia/Kolkata',
                        replace_existing=True,
                        name='sync_to_schedule'
                    )
    
        if slot.end.strftime("%H:%M") == MASTER.SunRise:
            scheduler.add_job(
                        sync_to_schedule,
                        kwargs={'syncWithAutoInterval' : False,
                                'relay':False,
                                'run_time':MASTER.sunrise_timestamp},
                        trigger='cron',
                        id = "sync_sunrise",
                        hour = slot.end.hour,
                        minute = slot.end.minute,
                        timezone = 'Asia/Kolkata',
                        replace_existing=True,
                        name='sync_to_schedule'
                    )
    try:
        scheduler.print_jobs()
    except Exception as e:
        print('Error in add_sync_jobs - for loop ',str(e))
    
def delete_logs():
    try:
        threshold = datetime.datetime.now(tz=get_current_timezone()) - timedelta(days=2)
        Notification.objects.filter(timestamp__lt=threshold).delete()
        TemperatureMeasurement.objects.filter(dateTimeStamp__lt=threshold).delete()
        CurrentMeasurement.objects.filter(dateTimeStamp__lt=threshold).delete()
    except Exception as e:
        Notification.objects.create(
                operation_type='information',
                success = False,
                message = "Logs, current and temperature data deletion failed.",
                timestamp=datetime.datetime.now(tz=get_current_timezone())
        )
    else:
        Notification.objects.create(
                operation_type='information',
                success = True,
                message = "Logs, current and temperature data deleted successfully.",
                timestamp=datetime.datetime.now(tz=get_current_timezone())
        )