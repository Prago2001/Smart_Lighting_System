import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .Scheduler import fetchSunModel, scheduler, function_mapping, sync_to_schedule
import pytz
from dateutil import parser
# from datetime import date, datetime
import datetime
from .models import CurrentMeasurement, Schedule, Slave, Slot, TemperatureMeasurement
import time
import concurrent.futures
from .Coordinator import perform_dimming,perform_toggle
from apscheduler.job import Job

try:
    from .Coordinator import MASTER
except Exception as e:
    pass



# Create your views here.
@api_view(['GET'])
def get_nodes(request):
    data_list = []
    for node in Slave.objects.all():
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
        data_list = []
        toggle_status = []
        for node in Slave.objects.all():
            toggle_status.append(node.mains_val)
        if all(toggle_status) is True:
            return Response({'relay': True})
        else:
            return Response({'relay': False})
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

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                threads = [executor.submit(perform_toggle,node_name=node.name,id=node.unique_id,mains_val=switch_mains_value) for node in Slave.objects.all()]
                for f in concurrent.futures.as_completed(threads):
                    status, id = f.result()
                    node = Slave.objects.get(unique_id=id)
                    if status is True:
                        node.is_active = True
                        node.mains_val = switch_mains_value
                    else:
                        print(f"Unable to toggle {node.name}")
                        node.is_active = False
                    node.save()
            print(f"Time needed for execution {time.time() - start_time}")
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
                return Response({"message":f"Node {node.name} is inactive"})
            else:
                node.is_active = True
                remote.set_mains_value(switch_mains_value)
                node.mains_val = switch_mains_value
                node.save()
    return Response({"message":"Success"})

@api_view(['GET','POST','PUT'])
def dim_to(request):
    # print(request.method)
    if request.method == "GET":
        node = Slave.objects.first()
        return Response({'intensity': node.dim_val})

    elif request.method == "PUT":
        start_time = time.time()
        request_data = json.loads(request.body)
        params = request_data['params']

        if 'isGlobal' in params and params['isGlobal'] is True:
            dim_to_value = int(params["value"])



            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                threads = [executor.submit(perform_dimming,node_name=node.name,id=node.unique_id,dim_value=dim_to_value) for node in Slave.objects.all()]
                for f in concurrent.futures.as_completed(threads):
                    status, id = f.result()
                    node = Slave.objects.get(unique_id=id)
                    if status is True:
                        node.is_active = True
                        node.dim_val = dim_to_value
                    else:
                        print(f"Unable to dim {node.name}")
                        node.is_active = False
                    node.save()
            print(f"Time needed for execution {time.time() - start_time}")
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
        scheduler.add_job(
                    function_mapping['set_dim_to'],
                    args=[db_slot.intensity],
                    trigger='cron',
                    id = db_slot.__str__(),
                    hour = db_slot.start.hour,
                    minute = db_slot.start.minute,
                    timezone = 'Asia/Kolkata',
                    replace_existing=True,
                    name='dimming_job'
                )
        id = "sync_" + db_slot.__str__()
        scheduler.add_job(
                    sync_to_schedule,
                    trigger='cron',
                    id = id,
                    hour = db_slot.start.hour,
                    minute = db_slot.start.minute + 1,
                    timezone = 'Asia/Kolkata',
                    replace_existing=True,
                    name='sync_auto'
                )
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

@api_view(['DELETE'])
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

