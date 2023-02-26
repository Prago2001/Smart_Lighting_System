import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .Scheduler import fetchSunModel, scheduler, function_mapping, sync_to_schedule
import pytz
from dateutil import parser
from datetime import timedelta
import datetime
from .models import CurrentMeasurement, Schedule, Slave, Slot, TemperatureMeasurement
import time
import concurrent.futures
from .Coordinator import perform_dimming,perform_toggle,retry_mains, retry_dim
from apscheduler.job import Job

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
            temp_val = remote.get_temperature_value()
            curr_val = remote.get_current_value()
            node.is_active = True
            node.current = curr_val
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

            if status == "on":
                switch_mains_value = True
            else:
                switch_mains_value = False
            
            failed_nodes = {}

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                threads = [executor.submit(perform_toggle,node_name=node.name,id=node.unique_id,mains_val=switch_mains_value) for node in Slave.objects.all().order_by('is_active')]
                for f in concurrent.futures.as_completed(threads):
                    status, id = f.result()
                    node = Slave.objects.get(unique_id=id)
                    if status is True:
                        node.is_active = True
                        node.mains_val = switch_mains_value
                    else:
                        print(f"Unable to toggle {node.name}")
                        node.is_active = False
                        failed_nodes[node.name] = node.unique_id
                    node.save()
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
                timezone = 'Asia/Kolkata',
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
                node.mains_val = switch_mains_value
                node.save()
                return Response({"operation":False})
            else:
                node.is_active = True
                remote.set_mains_value(switch_mains_value)
                node.mains_val = switch_mains_value
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

            failed_nodes = {}

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                threads = [executor.submit(perform_dimming,node_name=node.name,id=node.unique_id,dim_value=dim_to_value) for node in Slave.objects.all().order_by('is_active')]
                for f in concurrent.futures.as_completed(threads):
                    status, id = f.result()
                    node = Slave.objects.get(unique_id=id)
                    if status is True:
                        node.is_active = True
                        node.dim_val = dim_to_value
                    else:
                        print(f"Unable to dim {node.name}")
                        node.is_active = False
                        failed_nodes[node.name] = node.unique_id
                    node.save()
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
                timezone = 'Asia/Kolkata',
                )
                return Response({"operation":False,"nodes":failed_nodes.keys()})
        else:
            id = params["id"]
            dim_to_value = params["value"]


            remote = MASTER.get_node(id)
            node = Slave.objects.get(name=id)
            if remote is None:
                node.is_active = False
                node.dim_val = dim_to_value
                node.save()
                return Response({"message":f"Node {node.name} is inactive"})
            else:
                node.is_active = True
                remote.set_dim_value(dim_to_value)
                node.dim_val = dim_to_value
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
    return Response(data)



@api_view(['GET','POST'])
def changeSchedule(request):
    schedule = request.body.decode('utf-8')
    schedule = json.loads(schedule)
    schedule = schedule['schedule']

    current_active_schedule = Schedule.objects.get(currently_active=True)
    slots = Slot.objects.filter(schedule=current_active_schedule).order_by('id')
    row = 0
    for db_slot in slots:
        new_row = schedule[row]

        new_start = parser.isoparse(new_row['from']).astimezone(pytz.timezone('Asia/Kolkata'))
        new_end = parser.isoparse(new_row['to']).astimezone(pytz.timezone('Asia/Kolkata'))
        new_intensity = new_row['i']

        db_slot.start = new_start
        db_slot.end = new_end
        db_slot.intensity = new_intensity
        db_slot.save()
        # scheduler.add_job(
        #             function_mapping['set_dim_to'],
        #             args=[db_slot.intensity],
        #             trigger='cron',
        #             id = db_slot.__str__(),
        #             hour = db_slot.start.hour,
        #             minute = db_slot.start.minute,
        #             timezone = 'Asia/Kolkata',
        #             replace_existing=True,
        #             name='dimming_job'
        #         )
        # id = "sync_" + db_slot.__str__()
        # scheduler.add_job(
        #             sync_to_schedule,
        #             trigger='cron',
        #             id = id,
        #             hour = db_slot.start.hour,
        #             minute = db_slot.start.minute + 1,
        #             timezone = 'Asia/Kolkata',
        #             replace_existing=True,
        #             name='sync_auto'
        #         )
        row += 1
    for job in scheduler.get_jobs():
        print("name: %s, trigger: %s, next run: %s, handler: %s" % (job.name, job.trigger, job.next_run_time, job.func))
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
                timezone = 'Asia/Kolkata',
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
                            timezone = 'Asia/Kolkata',
                        )
            else:
                if current_time >= start or current_time < end:
                    failed_nodes = MASTER.set_dim_value(slot.intensity)
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
                            timezone = 'Asia/Kolkata',
                        )
            
    else:
        failed_nodes = MASTER.make_all_off()
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
                timezone = 'Asia/Kolkata',
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
        
        print("JOB LIST : ")
        for job in scheduler.get_jobs():
            print("name: %s, trigger: %s, next run: %s, handler: %s" % (job.name, job.trigger, job.next_run_time, job.func))
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
                if job.name in ('dimming_job','sync_auto','sync_every_half_hour'):
                    job.pause()
        elif 'status' in params and params['status'] is True:
            MASTER.Schedule = True
            job:Job
            for job in scheduler.get_jobs():
                if job.name in ('dimming_job','sync_auto','sync_every_half_hour'):
                    job.resume()
        
        print("JOB LIST : ")
        for job in scheduler.get_jobs():
            print("name: %s, trigger: %s, next run: %s, handler: %s" % (job.name, job.trigger, job.next_run_time, job.func))
        
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


@api_view(['GET'])
def getAllSchedules(request):
    schedules = Schedule.objects.all()
    return Response({'schedules':schedules})
    
@api_view(['GET'])
def getScheduleByName(request):
    #expects schedule name in url
    name = request.GET.get('schedule_name')
    schedule = Schedule.objects.get(schedule_name = name)
    return Response({'schedule':schedule})

@api_view(['GET'])
def getActiveSchedule(request):
    schedule = Schedule.objects.get(currently_active = True)
    return Response({'active_schedule':schedule})

@api_view(['PUT'])
def activateSchedule(request):
    #expects schedule name in request data
    schedule = request.body.decode('utf-8')
    schedule = json.loads(schedule)
    schedule_name = schedule['schedule_name']

    past_schedule = Schedule.objects.get(currently_active = True)
    past_schedule.currently_active = False
    past_schedule.save()

    activation_schedule = Schedule.objects.get(schedule_name = schedule_name)
    activation_schedule.currently_active = True
    activation_schedule.save()


    for job in scheduler.get_jobs():
        if job.name == 'sync_to_schedule':
            job.remove()

    active_slots = Slot.objects.filter(schedule = activation_schedule).order_by('id')
    
    for slot in active_slots:
    
        if slot.start.strftime("%H:%M") == MASTER.SunSet:
            scheduler.add_job(
                        sync_to_schedule,
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
                        trigger='cron',
                        id = "sync_sunrise",
                        hour = slot.end.hour,
                        minute = slot.end.minute,
                        timezone = 'Asia/Kolkata',
                        replace_existing=True,
                        name='sync_to_schedule'
                    )


    return Response(data={"message":"Success"})

@api_view(['DELETE'])
def deleteSchedule(request):
    #expects schedule_name in url
    schedule_name = request.GET.get('schedule_name')
    Schedule.objects.get(schedule_name = schedule_name).delete()

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
        schedule_name = body['schedule_ame']
        make_active = body['make_active']

        schedule_object = Schedule(schedule_name = schedule_name,currently_active = make_active)
        schedule_object.save()

        no_of_slots = body['no_of_slots']
        schedule = body['schedule']
        
        for i in range(no_of_slots):
            row = schedule[i]
            start = parser.isoparse(row['from']).astimezone(pytz.timezone('Asia/Kolkata'))
            end = parser.isoparse(row['to']).astimezone(pytz.timezone('Asia/Kolkata'))
            intensity = row['i']

            #start =  datetime.time(int(schedules_list[i][0]),int((schedules_list[i][0]%1)*100))   
            #end = datetime.time(int(schedules_list[i][1]),int((schedules_list[i][1]%1)*100))
            slot = Slot(start = start,end = end,intensity = intensity,schedule = schedule_object)
            slot.save()
            

        return Response(data={"message":"Success"})
    
    else:
        body = request.body.decode('utf-8')
        body = json.loads(body)
        schedule_name = body['schedule_ame']
        make_active = body['make_active']

        schedule_object = Schedule.objects.get(schedule_name = schedule_name)
        if(schedule_object.currently_active != make_active):
            schedule_object.currently_active = make_active
            schedule_object.save()

        slots = Slot.objects.filter(schedule = schedule_object).order_by('id')

        no_of_slots = len(slots)
        schedule = body['schedule']
        
        index = 0
        for i in range(no_of_slots):
            row = schedule[i]
            start = parser.isoparse(row['from']).astimezone(pytz.timezone('Asia/Kolkata'))
            end = parser.isoparse(row['to']).astimezone(pytz.timezone('Asia/Kolkata'))
            intensity = row['i']

            slots[index].start = start
            slots[index].end = end
            slots[index].intensity = intensity
            
            slots[index].save()

            index+=1
            

        return Response(data={"message":"Success"})


@api_view(['GET'])
def getSlotsByScheduleName(request):
    #expects schedule name in url
    schedule_name = request.GET.get('schedule_name')
    schedule = Schedule.objects.get(schedule_name = schedule_name)

    slots = Slot.objects.filter(schedule = schedule).order_by('id')

    data = {'slots':[]}

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
def changeASlotFromSchedule(request):
    #expects schedule name , 'n'th slot to be changed, new_start, new_end
    body = request.body.decode('utf-8')
    body = json.loads(body)
    
    schedule = Schedule.objects.get(schedule_name = body['schedule_name'])

    slots = Slot.objects.filter(schedule = schedule)
    
    n = body['n']
    new_start = body['new_start']
    new_end = body['new_end']

    slot_to_change = slots[n-1]
    slot_to_change.start = datetime.time(int(new_start),int((new_start%1)*100))
    slot_to_change.end = datetime.time(int(new_end),int((new_end%1)*100))

    slot_to_change.save()
    return Response({'slots':slots})
