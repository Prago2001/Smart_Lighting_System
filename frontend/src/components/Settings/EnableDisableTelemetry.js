import React, { useState,useEffect } from "react";
import Typography from '@mui/material/Typography';
import Switch from '@mui/material/Switch';
import Stack from '@mui/material/Stack';
import axios from "axios";
import url from "../BaseURL";

export default function EnableDisableTelemetry(){
    const [telemetryStatus,setTelemetryStatus] = useState(null);

    useEffect(() => {
        axios
        .get(url + "setTelemetry/",)
        .then((res) => {
            setTelemetryStatus(res.data.status);
        })
        .catch((error) => console.log(error));
    },[])
    
    const handleChange = (event) => {
        axios
        .put(url + "setTelemetry/", {
            params: {
            status: !telemetryStatus,
            },
        })
        .then((res) => {
            setTelemetryStatus(!telemetryStatus);
        })
        .catch((error) => console.log(error));
        
    }
    return(
        <div>
            <Typography variant="h5">
                Enable or Disable Telemetry
            </Typography>
            <Typography variant="caption">
                System collects current and temperature data from every streetlight after every two minutes. Disabling telemetry will turn off this operation.
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center" sx={{mt:4}}>
                <Typography>Disable Telemetry</Typography>
                <Switch
                    checked={telemetryStatus}
                    onChange={handleChange}
                />
                <Typography>Enable Telemetry</Typography>
            </Stack>
        </div>
    )
}