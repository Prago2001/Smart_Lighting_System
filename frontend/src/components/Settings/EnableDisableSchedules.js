import React, { useState,useEffect } from "react";
import Typography from '@mui/material/Typography';
import Switch from '@mui/material/Switch';
import Stack from '@mui/material/Stack';
import axios from "axios";
import url from "../BaseURL";
export default function EnableDisableSchedule(){
    const [scheduleStatus,setScheduleStatus] = useState(null);

    useEffect(() =>{
        axios
        .get(url + "activateSchedule/")
        .then((res) => {
            setScheduleStatus(res.data.status);
        })
        .catch((error) => console.log(error));
    },[])
    
    const handleChange = (event) => {
        axios
            .put(url + "activateSchedule/",{
                params: {
                  status: !scheduleStatus,
                },
              })
            .then((res) => {
                setScheduleStatus(!scheduleStatus);
            })
        
    }
    return(
        <div>
            <Typography variant="h5">
                Enable or Disable schedules
            </Typography>
            <Typography variant="caption">
                Disabling schedules means the system will not follow a schedule and must be controlled manually.
                <br/>
                Enabling schedules means the system will follow a selected schedule.
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center" sx={{mt:4}}>
                <Typography>Disable Schedules</Typography>
                <Switch
                    checked={scheduleStatus}
                    onChange={handleChange}
                />
                <Typography>Enable Schedules</Typography>
            </Stack>
        </div>
    )
}