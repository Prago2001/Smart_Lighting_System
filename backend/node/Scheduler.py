import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from astral import LocationInfo
from astral.sun import sun
from .Coordinator import MASTER, Coordinator
from .models import Schedule, Slot, CurrentMeasurement, TemperatureMeasurement,Slave

scheduler = BackgroundScheduler()

# in startup :

def getInsValues():
    for node in Slave.objects.all():
        remote = MASTER.get_node(node.name)

        if remote is None:
            node.is_active = False
        else:
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
        scheduler.add_job(lambda : MASTER.make_all_on(), 'cron', id='sunset', hour=s["sunset"].hour, minute=s["sunset"].minute, timezone='Asia/Kolkata')
    else:
        j.reschedule('cron', hour=s["sunset"].hour, minute=s["sunset"].minute, timezone='Asia/Kolkata')
    j = scheduler.get_job('sunrise')
    if j is None:
        scheduler.add_job(lambda : MASTER.make_all_off(), 'cron', id='sunrise',  hour=s["sunrise"].hour, minute=s["sunrise"].minute, timezone='Asia/Kolkata')
    else:
        j.reschedule('cron', hour=s["sunrise"].hour, minute=s["sunrise"].minute, timezone='Asia/Kolkata')




def updater_start():

    scheduler.add_job(lambda : getInsValues(), 'interval', seconds=60, id='inst_values')
    scheduler.add_job(lambda : fetchSunModel(), 'cron', id='sunmodel', hour=0, minute=15, timezone='Asia/Kolkata')
    scheduler.start()