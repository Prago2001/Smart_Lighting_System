import json
try:
    from .Coordinator import MASTER
except Exception as e:
    pass


def read_config_file():
    try:
        with open("config.json","r") as file:
            data = json.load(file)
            
            MASTER.Telemetry = data["telemetry"]
            MASTER.Schedule = data["schedule"]
            MASTER.areaName = data["area_name"]
            MASTER.syncWithAuto = data["sync_with_auto"]
            MASTER.syncWithAutoInterval = data["sync_with_auto_interval"]
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

            json.dump(data, file,sort_keys=True,indent=4)
    except Exception as e:
        print("Error in writing config file",e)
    