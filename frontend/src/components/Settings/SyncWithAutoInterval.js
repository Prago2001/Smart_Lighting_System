import React, { useState,useEffect } from "react";
import Typography from '@mui/material/Typography';
import Switch from '@mui/material/Switch';
import Stack from '@mui/material/Stack';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormHelperText from '@mui/material/FormHelperText';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import axios from "axios";
import url from "../BaseURL";

export default function SyncWithAutoInterval(){
    const [state,setState] = useState(true);
    const [interval,setInterval] = useState(30);
    useEffect(() => {
        axios
            .get(url + 'syncWithAutoInterval')
            .then((res) => {
                setState(res.data.status);
                setInterval(res.data.interval);
            })
    },[])

    const handleToggle = (event) => {
        axios
            .put(url + 'syncWithAutoInterval',{
                status: !state
            })
            .then((res) => {
                setState(!state);
            });
        
    }

    const handleChange = (e) => {
        axios
            .put(url + 'syncWithAutoInterval',{
                interval : e.target.value
            })
            .then((res) => {
                setInterval(e.target.value);
            });
        
    }

    return (
        <div>
            <Typography variant="h5">
                Sync With Auto Interval
            </Typography>
            <Typography variant="caption">
                The system performs a "Sync with Auto" operation after every {interval} minutes. This can be either switched off or the interval duration can be switched in the below dropdown 
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center" sx={{mt:4}}>
                <Typography>Disable Sync With Auto Interval</Typography>
                <Switch
                    checked={state}
                    onChange={handleToggle}
                />
                <Typography>Enable Sync With Auto Interval</Typography>
            </Stack>
            <FormControl sx={{ mt: 4, minWidth: 120 }}>
                <InputLabel id="helper-label">Interval</InputLabel>
                <Select
                    labelId="helper-label"
                    value={interval}
                    label="Interval"
                    onChange={handleChange}
                    disabled={!state}
                >
                    <MenuItem value={30}>30 minutes</MenuItem>
                    <MenuItem value={60}>1 hour</MenuItem>
                    <MenuItem value={120}>2 hour</MenuItem>
                    <MenuItem value={240}>4 hour</MenuItem>
                </Select>
                <FormHelperText>Select interval duration for Sync with Auto</FormHelperText>
            </FormControl>
        </div>
    )
}