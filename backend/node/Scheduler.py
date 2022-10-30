import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from astral import LocationInfo
from astral.sun import sun
from .models import Schedule, Slot, CurrentMeasurement, TemperatureMeasurement,Slave


try:
    from .Coordinator import MASTER
except Exception as e:
    pass

function_mapping = {
    'set_dim_to' : MASTER.set_dim_value,
    'make_all_on' : MASTER.make_all_on,
    'make_all_off':MASTER.make_all_off,
}

scheduler = BackgroundScheduler()

# in startup :

def getInsValues():
    for node in Slave.objects.all():
        remote = MASTER.get_node(node.name)

        if remote is None:
            node.is_active = False
        else:
            # If is_active of node is False
            # and communication re-ocurs then
            # setting it to current mains value and dim value 
            if node.is_active is False:
                remote.set_mains_value(node.mains_val)
                remote.set_dim_value(node.dim_val)
            node.is_active = True
            temp = remote.get_temperature_value() 
            curr = remote.get_current_value()

            curr = curr - 447
            if 150 > curr > 50:
                curr = curr * 2.93
            elif 250 > curr > 150:
                curr = curr * 2.44
            elif 350 > curr > 250:
                curr = curr * 2.27
            else:
                curr = curr * 2.3
            temp = ((temp * 1.2 / 1023) - 0.5) * 100
            CurrentMeasurement.objects.create(SlaveId = node,currentValue = curr)
            TemperatureMeasurement.objects.create(SlaveId = node,temperatureValue = temp)
            node.current = curr
            node.temperature = temp

        node.save()

def fetchSunModel() :

    city = LocationInfo(name="pune", region="India", timezone="Asia/Kolkata", latitude=18.6452489, longitude=73.92318563785392)
    s = sun(city.observer, tzinfo=city.timezone)
    MASTER.SunRise = s["sunrise"].strftime("%H:%M")
    MASTER.SunSet = s["sunset"].strftime("%H:%M")
# Coordinator().autoSchedule[0]['from'] = s["sunset"]
# Coordinator().autoSchedule[-1]['to'] = s["sunrise"]

    current_schedule = Schedule.objects.get(currently_active = True)
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

    j = scheduler.get_job('sunset')
    if j is None:
        scheduler.add_job(function_mapping['make_all_on'], 'cron', id='sunset', hour=s["sunset"].hour, minute=s["sunset"].minute, timezone='Asia/Kolkata')
    else:
        j.reschedule('cron', hour=s["sunset"].hour, minute=s["sunset"].minute, timezone='Asia/Kolkata')
    j = scheduler.get_job('sunrise')
    if j is None:
        scheduler.add_job(function_mapping['make_all_off'], 'cron', id='sunrise',  hour=s["sunrise"].hour, minute=s["sunrise"].minute, timezone='Asia/Kolkata')
    else:
        j.reschedule('cron', hour=s["sunrise"].hour, minute=s["sunrise"].minute, timezone='Asia/Kolkata')




def updater_start():

    scheduler.add_job(getInsValues, 'interval', seconds=120, id='inst_values',name='current_temperature_values')
    scheduler.add_job(fetchSunModel, 'cron', id='sunmodel', hour=0, minute=15, timezone='Asia/Kolkata',name='sunrise_sunset_values')
    scheduler.start()



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
    for job in scheduler.get_jobs():
        print("name: %s, trigger: %s, next run: %s, handler: %s" % (job.name, job.trigger, job.next_run_time, job.func))


def sync_to_schedule():
    current_time = datetime.datetime.now().strftime("%H:%M")
    sunset = MASTER.SunSet
    sunrise = MASTER.SunRise

    if current_time >= sunset or current_time < sunrise:
        MASTER.make_all_on()
        current_schedule = Schedule.objects.get(currently_active = True)
        slots = Slot.objects.filter(schedule=current_schedule).order_by('id')

        for slot in slots:
            start = slot.start.strftime("%H:%M")
            end = slot.end.strftime("%H:%M")
            if start < end:
                if start <= current_time < end:
                    MASTER.set_dim_value(slot.intensity)
            else:
                if current_time >= start or current_time < end:
                    MASTER.set_dim_value(slot.intensity)
    else:
        MASTER.make_all_off()