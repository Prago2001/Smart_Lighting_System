import json
from .models import Energy
from datetime import timedelta
import datetime
from django.utils.timezone import get_current_timezone
import pytz
import requests
import subprocess
from django.utils import timezone
try:
    from .Coordinator import MASTER
except Exception as e:
    pass

CURRENT_AT_25 = 0.22
CURRENT_AT_50 = 0.48
CURRENT_AT_75 = 0.67
CURRENT_AT_100 = 0.91


def read_config_file():
    try:
        with open("config.json","r") as file:
            data = json.load(file)
            
            MASTER.Telemetry = data["telemetry"]
            MASTER.Schedule = data["schedule"]
            MASTER.areaName = data["area_name"]
            MASTER.syncWithAuto = data["sync_with_auto"]
            MASTER.syncWithAutoInterval = data["sync_with_auto_interval"]
            MASTER.energy_saved = data['energy_saved']
            file.close()
    except FileNotFoundError as fnf:
        write_config_file()
        print("Config file not found. Creating config.json")
    except Exception as e:
        print("Error in reading config file",e)

def write_config_file():
    try:
        with open("config.json","w") as file:
            data = {}
            data["telemetry"] = MASTER.Telemetry
            data["schedule"] = MASTER.Schedule
            data["area_name"] = MASTER.areaName
            data["sync_with_auto"] = MASTER.syncWithAuto
            data["sync_with_auto_interval"] = MASTER.syncWithAutoInterval
            data['energy_saved'] = MASTER.energy_saved
            json.dump(data, file,sort_keys=True,indent=4)
            file.close()
    except Exception as e:
        print("Error in writing config file",e)

def update_energy_config_file():
    try:
        data = {}
        with open("config.json","r") as file:
            data = json.load(file)

            total = 0
            for object in Energy.objects.all():
                if object.saved is not None:
                    total += object.saved
            data['energy_saved'] += total
            data['energy_saved'] = round(data['energy_saved'],2)
            MASTER.energy_saved = data['energy_saved']
            file.close()
        with open("config.json","w") as file:
            json.dump(data, file,sort_keys=True,indent=4)
            file.close()
    except Exception as e:
        print(f"Error while writing energy saved to file", e)
    
    last_energy_object = Energy.objects.filter(saved=None).values_list("id", flat=True  )
    if last_energy_object is not None:
        try:
            Energy.objects.exclude(pk__in=list(last_energy_object)).delete()
        except Exception as e:
            print(f"Error while deleting Energy objects", e)


def write_start_time_energy(intensity,mains):
    try:
        Energy.objects.create(
            start_time=datetime.datetime.now(tz=get_current_timezone()),
            intensity=intensity,
            mains=mains
        )
    except Exception as e:
        print(f"Exception while creating an energy object")

def write_end_time_energy():
    energy = Energy.objects.last()
    
    if energy is not None and energy.end_time is None:
        energy.end_time = datetime.datetime.now(tz=get_current_timezone())

        
        
        if energy.mains is False:
            energy.consumption = 0
            energy.saved = 0
        else:
            # Calculate duration in hours
            duration = energy.end_time - energy.start_time
            duration_in_hours = duration.total_seconds() / 3600

            energy.consumption = round(MASTER.number_of_nodes * calculate_power(energy.intensity,energy.mains) * duration_in_hours, 2)

            max_energy = round(MASTER.number_of_nodes * 50 * CURRENT_AT_100 * duration_in_hours / 1000,2)

            energy.saved = round(max_energy - energy.consumption,2)
            
        energy.save()
        print(f"Energy Saved: {energy.saved}")
        

def calculate_power(intensity,mains):
    if mains is False:
        return 0
    else:
        if intensity == 25:
            current = CURRENT_AT_25
        elif intensity == 50:
            current = CURRENT_AT_50
        elif intensity == 75:
            current = CURRENT_AT_75
        elif intensity == 100:
            current = CURRENT_AT_100
        
        # Power for a single street light in kilo-watt
        power = (current * 50) / 1000

        return power

def get_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json').json()
    except requests.exceptions.RequestException as e:
        print("Error in fetching ip address\n",e)
        return None
    else:
        return response["ip"]

def get_location():
    ip = get_ip()
    if ip is not None:
        try:
            response = requests.get('http://ipinfo.io/json').json()
        except requests.exceptions.RequestException as e:
            print("Error in fetching location details\n", e)
        else:
            print(response)
            MASTER.location["ip"] = ip
            if "city" in response and "timezone" in response and "loc" in response:
                MASTER.location["city"] = response.get("city")
                MASTER.location["region"] = response.get("region")
                MASTER.location["timezone"] = response.get("timezone")
                lat, long = response.get('loc').split(",")
                MASTER.location["latitude"] = float(lat)
                MASTER.location["longitude"] = float(long)
                print(MASTER.location)
            try:
                timezone.activate(pytz.timezone(MASTER.location['timezone']))
            except Exception as e:
                print("Unable to set timezone")

def get_package_info():
    try:
        request = requests.get('https://api.github.com/repos/Prago2001/Smart_Lighting_System/releases/latest').json()
    except requests.exceptions.RequestException as e:
        print("Unable to fetch verison of package")
        return None
    else:
        version = request.get('tag_name')
        release_date = request.get('published_at')
        release_date = datetime.datetime.strptime(release_date,"%Y-%m-%dT%H:%M:%SZ")
        return (release_date.strftime("%-d %B %Y"),version)

def restart_server():
    restart_service = "sudo systemctl restart backend.service".split()
    process = subprocess.run(
        restart_service,
        stdout=subprocess.PIPE,
        encoding="ascii"
    )