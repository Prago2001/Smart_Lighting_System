import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .Scheduler import fetchSunModel, scheduler, function_mapping, sync_to_schedule, add_sync_jobs,delete_logs
import pytz
from dateutil import parser
from datetime import timedelta
import datetime
from .models import CurrentMeasurement, Schedule, Slave, Slot, TemperatureMeasurement,Notification
import time
import concurrent.futures
from .Coordinator import perform_dimming,perform_toggle,retry_mains, retry_dim
from apscheduler.job import Job
from django.utils.timezone import get_current_timezone
import random
from .utils import read_config_file,write_config_file,write_end_time_energy,write_start_time_energy,update_energy_config_file, get_package_info,restart_server
from threading import Timer
try:
    from .Coordinator import MASTER
except Exception as e:
    pass



# Create your views here.
@api_view(['GET'])
def get_nodes(request):
    data_list = []
    for node in Slave.objects.all().order_by('is_active'):
        node_data = {
            'id' : node.name,
            'relay' : node.mains_val,
            'dim' : node.dim_val,
            'current' : node.current,
            'temp' : node.temperature,
            'is_active' : node.is_active,
        }
        data_list.append(node_data)
    return Response({'nodes': data_list})

@api_view(['GET'])
def discover_remote_nodes(request):
    for node in MASTER.discover_nodes():
        if not Slave.objects.filter(unique_id = node._64bit_addr).exists():
            slave = Slave(
                unique_id = node._64bit_addr, 
                name = node.node_name,
                current = node.get_current_value(),
                temperature = node.get_temperature_value(),
                mains_val = node.get_mains_value(),
                dim_val = node.get_dim_value()
            )
            slave.save()

    data_list = []
    for node in Slave.objects.all():
        remote = MASTER.get_node(node.name)
        if remote is None:
            node.is_active = False
            node.save()
        else:
            temp_val = None
            curr_val = None
            try:
                temp_val = remote.get_temperature_value()
                curr_val = remote.get_current_value()
            except Exception as e:
                print(f"Real time collection of values failed for {node.name}")
            node.is_active = True
            if curr_val is not None:
                node.current = curr_val
            if temp_val is not None:
                node.temperature = temp_val
            node.save()

            CurrentMeasurement.objects.create(SlaveId = node,currentValue = curr_val)
            TemperatureMeasurement.objects.create(SlaveId = node,temperatureValue = temp_val)
        
        node_data = {
            'id' : node.name,
            'relay' : node.mains_val,
            'dim' : node.dim_val,
            'current' : node.current,
            'temp' : node.temperature,
            'is_active' : node.is_active,
        }
        data_list.append(node_data)
    return Response({'nodes':data_list})

@api_view(['GET','POST','PUT'])
def toggle_mains(request):
    if request.method == "GET":
        node = Slave.objects.all().order_by('-is_active').first()
        # print(node.mains_val,node.dim_val)
        if node is None:
            # To handle all deleted nodes
            return Response({'relay': False})
        else:
            return Response({'relay': node.mains_val})
        # data_list = []
        # toggle_status = []
        # for node in Slave.objects.all().filter('is_active'):
        #     toggle_status.append(node.mains_val)
        # if all(toggle_status) is True:
        #     return Response({'relay': True})
        # else:
        #     return Response({'relay': False})
    elif request.method == "PUT":
        start_time = time.time()
        request_data = json.loads(request.body)
        params = request_data['params']
        if 'isGlobal' in params and params['isGlobal'] is True:
            status = params['status']
            failed_nodes = {}
            write_end_time_energy()
            if status == "on":
                switch_mains_value = True
                failed_nodes = MASTER.make_all_on()
                node = Slave.objects.all().order_by('-is_active').first()
                if node is not None:
                    write_start_time_energy(mains=True,intensity=node.dim_val)
            else:
                switch_mains_value = False
                failed_nodes = MASTER.make_all_off()
                write_start_time_energy(mains=False,intensity=0)


            print(f"Time needed for execution {time.time() - start_time}")
            if len(failed_nodes) == 0:
                return Response({"operation":True})
            else:
                MASTER.manualJobStatus = True
                scheduler.add_job(
                func=retry_mains,
                trigger='date',
                args=[failed_nodes,switch_mains_value,],
                id='retry_manual_mains',
                name="Retrying mains operation in manual mode",
                replace_existing=True,
                run_date=datetime.datetime.now() + timedelta(seconds=15),
                timezone = MASTER.location['timezone'],
                )
                return Response({"operation":False,"nodes":failed_nodes.keys()})
            
        else:
            id = params['id']
            status = params['status']

            if status == "on":
                switch_mains_value = True
            else:
                switch_mains_value = False

            remote = MASTER.get_node(id)
            node = Slave.objects.get(name=id)
            if remote is None:
                node.is_active = False
                node.save()
                return Response({"operation":False})
            else:
                try:
                    remote.set_mains_value(switch_mains_value)
                except Exception as e:
                    node.is_active = False
                    node.save()
                    return Response({"operation":False})
                node.mains_val = switch_mains_value
                node.is_active = True
                node.save()
                return Response({"operation":True})

@api_view(['GET','POST','PUT'])
def dim_to(request):
    # print(request.method)
    if request.method == "GET":
        node = Slave.objects.all().order_by('-is_active').first()
        if node is None:
            # To handle all deleted nodes
            return Response({'intensity': 25})
        else:
            return Response({'intensity': node.dim_val})

    elif request.method == "PUT":
        start_time = time.time()
        request_data = json.loads(request.body)
        params = request_data['params']

        if 'isGlobal' in params and params['isGlobal'] is True:
            dim_to_value = int(params["value"])

            write_end_time_energy()
            write_start_time_energy(mains=True,intensity=dim_to_value)

            failed_nodes = {}

            failed_nodes = MASTER.set_dim_value(dim_value=dim_to_value)

            print(f"Time needed for execution {time.time() - start_time}")
            if len(failed_nodes) == 0:
                return Response({"operation":True})
            else:
                MASTER.manualJobStatus = True
                scheduler.add_job(
                func=retry_dim,
                trigger='date',
                args=[failed_nodes,dim_to_value,],
                id='retry_manual_dim',
                name="Retrying dim operation in manual mode",
                replace_existing=True,
                run_date=datetime.datetime.now() + timedelta(seconds=15),
                timezone = MASTER.location['timezone'],
                )
                return Response({"operation":False,"nodes":failed_nodes.keys()})
        else:
            id = params["id"]
            dim_to_value = params["value"]


            remote = MASTER.get_node(id)
            node = Slave.objects.get(name=id)
            if remote is None:
                node.is_active = False
                node.save()
                return Response({"message":f"Node {node.name} is inactive"})
            else:
                try:
                    remote.set_dim_value(dim_to_value)
                except Exception as e:
                    node.is_active = False
                    node.save()
                    return Response({"message":f"Node {node.name} is inactive"})
                node.dim_val = dim_to_value
                node.is_active = True
                node.save()

    return Response({"message":"Success"})



@api_view(['GET'])
def getSchedule(request):
    fetchSunModel()
    YEAR = datetime.date.today().year
    MONTH = datetime.date.today().month
    DAY = datetime.date.today().day
    current_schedule = Schedule.objects.get(currently_active=True)
    data = {'schedule':[]}
    slots = Slot.objects.filter(schedule=current_schedule).order_by('id')
    for row in slots:
        data['schedule'].append(
            {
                'from': datetime.datetime(YEAR,MONTH,DAY,row.start.hour,row.start.minute,row.start.second),
                'to': datetime.datetime(YEAR,MONTH,DAY,row.end.hour,row.end.minute,row.end.second),
                'i': row.intensity
            }
        )
    data['sunrise'] = MASTER.SunRise
    data['sunset'] = MASTER.SunSet
    data['sunrise_ts'] = MASTER.sunrise_timestamp
    data['sunset_ts'] = MASTER.sunset_timestamp
    return Response(data)



@api_view(['GET','POST'])
def changeSchedule(request):
    schedule = request.body.decode('utf-8')
    schedule = json.loads(schedule)
    schedule = schedule['schedule']

    current_active_schedule = Schedule.objects.get(currently_active=True)
    slots = Slot.objects.filter(schedule=current_active_schedule).order_by('id')
    for i in range(len(slots)):
        row = schedule[i]
        start = parser.isoparse(row['from']).astimezone(pytz.timezone(MASTER.location['timezone']))
        end = parser.isoparse(row['to']).astimezone(pytz.timezone(MASTER.location['timezone']))
        intensity = int(row['i'])

        slots[i].start = start
        slots[i].end = end
        slots[i].intensity = intensity
        
        slots[i].save()
    # Add sync jobs
    add_sync_jobs()
    return Response({"message" : "Success"})


@api_view(['GET','POST'])
def syncToSchedule(request):
    current_time = datetime.datetime.now().strftime("%H:%M")
    sunset = MASTER.SunSet
    sunrise = MASTER.SunRise
    
    if current_time >= sunset or current_time < sunrise:
        failed_nodes = MASTER.make_all_on()
        if len(failed_nodes) > 0:
            MASTER.manualJobStatus = True
            scheduler.add_job(
                func=retry_mains,
                trigger='date',
                args=[failed_nodes,True,],
                id='retry_manual_mains',
                name="Retrying mains operation in manual mode",
                replace_existing=True,
                run_date=datetime.datetime.now() + timedelta(seconds=15),
                timezone = MASTER.location['timezone'],
            )
        current_schedule = Schedule.objects.get(currently_active = True)
        slots = Slot.objects.filter(schedule=current_schedule).order_by('id')
        while MASTER.manualJobStatus is True:
            continue
        for slot in slots:
            start = slot.start.strftime("%H:%M")
            end = slot.end.strftime("%H:%M")
            if start < end:
                if start <= current_time < end:
                    failed_nodes = MASTER.set_dim_value(slot.intensity)
                    write_end_time_energy()
                    write_start_time_energy(slot.intensity,mains=True)
                    if len(failed_nodes) > 0:
                        MASTER.manualJobStatus = True
                        scheduler.add_job(
                            func=retry_dim,
                            trigger='date',
                            args=[failed_nodes,slot.intensity],
                            id='retry_manual_dim',
                            name="Retrying dim operation in manual mode",
                            replace_existing=True,
                            run_date=datetime.datetime.now() + timedelta(seconds=15),
                            timezone = MASTER.location['timezone'],
                        )
            else:
                if current_time >= start or current_time < end:
                    failed_nodes = MASTER.set_dim_value(slot.intensity)
                    write_end_time_energy()
                    write_start_time_energy(slot.intensity,mains=True)
                    if len(failed_nodes) > 0:
                        MASTER.manualJobStatus = True
                        scheduler.add_job(
                            func=retry_dim,
                            trigger='date',
                            args=[failed_nodes,slot.intensity],
                            id='retry_manual_dim',
                            name="Retrying dim operation in manual mode",
                            replace_existing=True,
                            run_date=datetime.datetime.now() + timedelta(seconds=15),
                            timezone = MASTER.location['timezone'],
                        )
            
    else:
        failed_nodes = MASTER.make_all_off()
        write_end_time_energy()
        write_start_time_energy(0,mains=False)
        if len(failed_nodes) > 0:
            MASTER.manualJobStatus = True
            scheduler.add_job(
                func=retry_mains,
                trigger='date',
                args=[failed_nodes,False,],
                id='retry_manual_mains',
                name="Retrying mains operation in manual mode",
                replace_existing=True,
                run_date=datetime.datetime.now() + timedelta(seconds=15),
                timezone = MASTER.location['timezone'],
            )
        
    return Response({"message":"Success"})

@api_view(['GET'])
def getInstValues(request):
    list = []
    for node in Slave.objects.all():
        
        data = {
            'id' : node.name,
            'current' : CurrentMeasurement.objects.get(SlaveId=node).currentValue,
            'temperature' : TemperatureMeasurement.objects.get(SlaveId=node).temperatureValue
        }

        list.append(data)

    return Response({'data':data})

@api_view(['GET'])
def getGraphValues(request):
    id = request.GET.get('id')
    modelNode = Slave.objects.get(name=id)

    i = 9

    curr = []
    temp = []
    for node in CurrentMeasurement.objects.filter(SlaveId=modelNode).order_by('-dateTimeStamp')[:10]:
        curr.append([i, node.currentValue])
        i -= 1
    
    i=9

    for node in TemperatureMeasurement.objects.filter(SlaveId=modelNode).order_by('-dateTimeStamp')[:10]:
        temp.append([i, node.temperatureValue])
        i -= 1

    curr.append(["x", "current"])
    temp.append(["x", "temperature"])

    curr = curr[::-1]
    temp = temp[::-1]

    return Response({'curr': curr, 'temp': temp})


@api_view(['GET','PUT'])
def enable_disable_telemetry(request):

    if request.method == "GET":
        return Response({'status': MASTER.Telemetry})

    elif request.method == "PUT":
        request_data = json.loads(request.body)
        params = request_data['params']
        if 'status' in params and params['status'] is False:
            MASTER.Telemetry = False
            job:Job
            for job in scheduler.get_jobs():
                if job.name == "current_temperature_values":
                    job.pause()
        elif 'status' in params and params['status'] is True:
            MASTER.Telemetry = True
            job:Job
            for job in scheduler.get_jobs():
                if job.name == "current_temperature_values":
                    job.resume()
        
        scheduler.print_jobs()
        write_config_file()
        return Response(data={"message":"Success"})


@api_view(['GET','PUT'])
def enable_disable_schedule(request):
    if request.method == "GET":
        return Response({'status': MASTER.Schedule})

    elif request.method == "PUT":
        request_data = json.loads(request.body)
        params = request_data['params']
        if 'status' in params and params['status'] is False:
            MASTER.Schedule = False
            job:Job
            for job in scheduler.get_jobs():
                if job.name in ('dimming_job','sync_to_schedule','sync_every_half_hour'):
                    job.pause()
        elif 'status' in params and params['status'] is True:
            MASTER.Schedule = True
            job:Job
            for job in scheduler.get_jobs():
                if job.name in ('dimming_job','sync_to_schedule'):
                    job.resume()
                if job.name == 'sync_every_half_hour' and MASTER.syncWithAuto is True:
                    job.resume()
        
        scheduler.print_jobs()
        write_config_file()
        return Response(data={"message":"Success"})

@api_view(['PUT'])
def delete_node(request):
    request_data = json.loads(request.body)
    params = request_data['params']
    id = params['id']
    nodeObject = Slave.objects.get(name=id)

    try:
        nodeObject.delete()
    except Exception as e:
        print(str(e))
    
    try:
        remote = MASTER.network.get_device_by_node_id(id)
        MASTER.network.remove_device(remote)
    except Exception as e:
        print(str(e))
    
    return Response(data={"message":"Success"})

@api_view(['GET'])
def getRetryJobStatus(response):
    while MASTER.manualJobStatus is True:
        continue
    failedNodes = []
    for node in Slave.objects.all():
        if node.is_active is False:
            failedNodes.append(node.name)
    if len(failedNodes) == 0:
        return Response({'operation':True})
    else:
        return Response({'operation':False,'nodes':failedNodes})

@api_view(['GET','DELETE'])
def logs(request):
    if request.method == "GET":
        data = []
        for record in Notification.objects.all().order_by('-timestamp'):
            data.append({
                'operation_type': record.operation_type,
                'success': record.success,
                'message': record.message,
                'timestamp': record.timestamp.astimezone(tz=get_current_timezone()),
            })
        return Response({'logs':data})
    elif request.method == "DELETE":
        delete_logs()
        return Response({"message":"success"})


@api_view(['GET','PUT'])
def alerts(request):
    if request.method == "GET":
        data = []
        to_filter = {'success' : False, 'is_read': False}
        for record in Notification.objects.all().filter(**to_filter).order_by('-timestamp'):
            timestamp = record.timestamp.astimezone(tz=get_current_timezone())
            timeString = timestamp.strftime("%d/%b/%y %I:%M %p")
            data.append({
                'message': record.message,
                'receivedTime': timeString,
                'image': "https://img.icons8.com/emoji/48/null/exclamation-mark-emoji.png",
                'id':record.pk
            })
        return Response({'alerts':data})
    elif request.method == "PUT":
        request_data = json.loads(request.body)
        params = request_data['params']
        if 'id_array' in params:
            for id in params['id_array']:
                notif = Notification.objects.get(pk=id)
                notif.is_read = True
                notif.save()
        return Response({'Success':True})
    

@api_view(['GET'])
def getAllSchedules(request):
    schedules = Schedule.objects.all().order_by('-currently_active')
    data = {'schedules':[]}

    for row in schedules:
        data['schedules'].append(
            {
                'schedule_id': row.schedule_id,
                'schedule_name': row.schedule_name,
                'currently_active': row.currently_active
            }
        )

    return Response(data)
    

@api_view(['GET'])
def getActiveSchedule(request):
    schedule = Schedule.objects.get(currently_active = True)
    slots = Slot.objects.filter(schedule = schedule).order_by('id')

    data = {
        'schedule_id': schedule.schedule_id,
        'schedule_name': schedule.schedule_name,
        'currently_active': schedule.currently_active,
        'slots':[]
        }

    YEAR = datetime.date.today().year
    MONTH = datetime.date.today().month
    DAY = datetime.date.today().day

    for row in slots:
        data['slots'].append(
            {
                'from': datetime.datetime(YEAR,MONTH,DAY,row.start.hour,row.start.minute,row.start.second),
                'to': datetime.datetime(YEAR,MONTH,DAY,row.end.hour,row.end.minute,row.end.second),
                'i': row.intensity
            }
        )

    return Response(data)


@api_view(['PUT'])
def activateSchedule(request):
    #expects schedule name in request data
    schedule = request.body.decode('utf-8')
    schedule = json.loads(schedule)
    schedule = schedule['schedule']
    schedule_name = schedule['schedule_name']

    past_schedule = Schedule.objects.get(currently_active = True)
    past_schedule.currently_active = False
    past_schedule.save()

    activation_schedule = Schedule.objects.get(schedule_name = schedule_name)
    activation_schedule.currently_active = True
    activation_schedule.save()

    # Add sync jobs
    add_sync_jobs()
    if MASTER.Schedule is False:
        job:Job
        for job in scheduler.get_jobs():
            if job.name in ('dimming_job','sync_to_schedule','sync_every_half_hour'):
                job.pause()



    return Response(data={"message":"Success"})

@api_view(['DELETE'])
def deleteSchedule(request):
    #expects schedule_name in url
    body = request.body.decode('utf-8')
    body = json.loads(body)
    schedule_name = body['schedule_name']
    try:
        Schedule.objects.get(schedule_name = schedule_name).delete()
    except Exception as e:
        return Response(data={'message':"Failed"})

    return Response(data={"message":"Success"})

@api_view(['POST','PUT'])
def createOrEditSchedule(request):
    # 'n' no. of slots with a shedule name and if to be set active , is expected in body
    '''
    {
        no_of_slots : 3
        schedule_name : S1
        make_active : True/False
        schedule : { object same as one received from frontend in changeSchedule }
    }
    
    '''
    if request.method == "POST":
        body = request.body.decode('utf-8')
        body = json.loads(body)
        schedule_name = body['schedule_name']
        make_active = body['make_active']

        if make_active is True:
            previously_active = Schedule.objects.get(currently_active=True)
            previously_active.currently_active = False
            previously_active.save()

        while True:
            try:
                schedule_object = Schedule(
                    schedule_id = random.randint(0,10000000),
                    schedule_name = schedule_name,
                    currently_active = make_active,
                )
                schedule_object.save()
                break
            except Exception as e:
                pass

        no_of_slots = body['no_of_slots']
        schedule = body['schedule']
        
        for i in range(no_of_slots):
            row = schedule[i]
            start = parser.isoparse(row['from']).astimezone(pytz.timezone(MASTER.location['timezone']))
            end = parser.isoparse(row['to']).astimezone(pytz.timezone(MASTER.location['timezone']))
            intensity = row['i']

            #start =  datetime.time(int(schedules_list[i][0]),int((schedules_list[i][0]%1)*100))   
            #end = datetime.time(int(schedules_list[i][1]),int((schedules_list[i][1]%1)*100))
            slot = Slot(start = start,end = end,intensity = intensity,schedule = schedule_object)
            slot.save()
        
        if make_active is True:
            add_sync_jobs()
            

        return Response(data={"message":"Success"})
    
    else:
        body = request.body.decode('utf-8')
        body = json.loads(body)
        schedule_name = body['schedule_name']
        schedule = body['schedule']

        schedule_object = Schedule.objects.get(schedule_name = schedule_name)
        
        slots = Slot.objects.filter(schedule = schedule_object).order_by('id')

        no_of_slots = len(slots)
        
        for i in range(no_of_slots):
            row = schedule[i]
            start = parser.isoparse(row['from']).astimezone(pytz.timezone(MASTER.location['timezone']))
            end = parser.isoparse(row['to']).astimezone(pytz.timezone(MASTER.location['timezone']))
            intensity = int(row['i'])

            slots[i].start = start
            slots[i].end = end
            slots[i].intensity = intensity
            
            slots[i].save()

        if schedule_object.currently_active is True:
            add_sync_jobs()
            

        return Response(data={"message":"Success"})


@api_view(['GET'])
def getScheduleInfo(request):
    #expects schedule name in url
    schedule_name = request.GET.get('schedule_name')
    schedule = Schedule.objects.get(schedule_name = schedule_name)

    slots = Slot.objects.filter(schedule = schedule).order_by('id')

    data = {
        'schedule_id': schedule.schedule_id,
        'schedule_name': schedule.schedule_name,
        'currently_active': schedule.currently_active,
        'no_of_slots': slots.count(),
        'slots':[]
        }

    YEAR = datetime.date.today().year
    MONTH = datetime.date.today().month
    DAY = datetime.date.today().day

    for row in slots:
        data['slots'].append(
            {
                'from': datetime.datetime(YEAR,MONTH,DAY,row.start.hour,row.start.minute,row.start.second),
                'to': datetime.datetime(YEAR,MONTH,DAY,row.end.hour,row.end.minute,row.end.second),
                'i': row.intensity
            }
        )

    return Response(data=data)


@api_view(["GET","PUT"])
def areaName(request):
    if request.method == "GET":
        return Response(data={'area_name': MASTER.areaName})
    elif request.method == "PUT":
        body = request.body.decode('utf-8')
        body = json.loads(body)
        area_name = body['area_name']

        MASTER.areaName = area_name
        write_config_file()
        return Response(data={"message":"Success"})

@api_view(["GET","PUT"])
def sync_with_auto_interval(request):
    if request.method == "GET":
        return Response(data={'status':MASTER.syncWithAuto,'interval':MASTER.syncWithAutoInterval})
    elif request.method == "PUT":
        body = request.body.decode('utf-8')
        body = json.loads(body)
        if 'status' in body:
            status = body['status']
            if status is True:
                job:Job
                for job in scheduler.get_jobs():
                    if job.name in ('sync_every_half_hour'):
                        job.resume()
                MASTER.syncWithAuto = True
            else:
                job:Job
                for job in scheduler.get_jobs():
                    if job.name in ('sync_every_half_hour'):
                        job.pause()
                MASTER.syncWithAuto = False
        elif 'interval' in body:
            interval = body['interval']
            MASTER.syncWithAutoInterval = interval
            scheduler.add_job(
                sync_to_schedule,
                kwargs={'syncWithAutoInterval' : True},
                trigger='interval',
                minutes=MASTER.syncWithAutoInterval,
                id='sync_to_auto',
                name='sync_every_half_hour',
                timezone=MASTER.location['timezone'],
                replace_existing=True
            )
        scheduler.print_jobs()
        write_config_file()
        return Response({'message':'Success'})

@api_view(["GET"])
def information(request):
    if request.method == "GET":
        data = {}
        data['active_nodes'] = Slave.objects.filter(is_active=True).count()
        data['total_nodes'] = Slave.objects.count()

        node = Slave.objects.all().order_by('-is_active').first()

        if node is None:
            # To handle all deleted nodes
            data['relay'] = False
            data['intensity'] = 25
        else:
            data['relay'] = node.mains_val
            data['intensity'] = node.dim_val
        
        data['sunrise_ts'] = MASTER.sunrise_timestamp
        data['sunset_ts'] = MASTER.sunset_timestamp

        data['sunrise'] = MASTER.sunrise_timestamp.strftime("%I:%M %p")
        data['sunset'] = MASTER.sunset_timestamp.strftime("%I:%M %p")

        if MASTER.Schedule is False:
            data['schedule'] = "Schedules are disabled"
            data['schedule_status'] = False
        else:
            job:Job
            for job in scheduler.get_jobs():
                if job.name == 'sync_to_schedule':
                    param = job.kwargs
                    if job.id == "sync_sunrise":
                        data['schedule'] = "Switching OFF lights at Sunrise"
                        data['schedule_status'] = "sunrise"
                    elif job.id == "sync_sunset":
                        data['schedule'] = "Switching ON lights at Sunset"
                        data['schedule_status'] = 'sunset'
                    else:
                        intensity = param['intensity']
                        time = param['run_time'].strftime("%I:%M %p")
                        data['schedule'] = f"Dimming lights to {intensity}%  intensity at {time}"
                        data['schedule_status'] = 'dim'
                    break
        data['energy_saved'] = round(MASTER.energy_saved,2)
        return Response(data)

@api_view(["GET"])
def system_information(request):
    if request.method == "GET":
        data = {}
        package_info = get_package_info()
        if package_info is None:
            data["version"] = "v4.3"
            data["release_date"] = "19 April 2023"
        else:
            data["version"] = package_info[1]
            data["release_date"] = package_info[0]
        
        data["city"] = MASTER.location["city"]
        data["region"] = MASTER.location["region"]
        data["lat"] = MASTER.location["latitude"]
        data["lon"] = MASTER.location["longitude"]

        return Response(data)

@api_view(["POST"])
def restart(request):
    if request.method == "POST":
        body = request.body.decode('utf-8')
        body = json.loads(body)
        status = body['status']

        t = Timer(5,restart_server)
        t.start()
        return Response({"message":"Success"})
