import React, { useState } from "react";
import AdapterDateFns from "@mui/lab/AdapterDateFns";
import LocalizationProvider from "@mui/lab/LocalizationProvider";
import MobileTimePicker from "@mui/lab/MobileTimePicker";
import TextField from '@mui/material/TextField';
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import Grid from '@mui/material/Grid';

export default function Slot({value,index,schedule,setSchedule}){
    const [startTime,setStartTime] = useState(value.from);
    const [endTime,setEndTime] = useState(value.to);
    const [intensity,setIntensity] = useState(value.i);
    return (
        <Grid
            container
            direction="row"
            justifyContent="center"
            alignItems="center"
            spacing={2}
        >
            <Grid item xs={5}>
                <LocalizationProvider className="" dateAdapter={AdapterDateFns}>
                    <MobileTimePicker
                        label="Start Time"
                        value={schedule[index].from}
                        disabled={index === 0}
                        onChange={(newValue) => {
                            const previous = {from:schedule[index-1].from,to:newValue,i:schedule[index-1].i}
                            const current = {from:newValue,to:schedule[index].to,i:schedule[index].i}
                            setSchedule([
                                ...schedule.slice(0,index-1),
                                previous,
                                current,
                                ...schedule.slice(index+1)
                            ]);
                            setStartTime(newValue)
                        }}
                        renderInput={(params) => <TextField {...params} />}
                    />
                </LocalizationProvider>
            </Grid>
            <Grid item xs={5}>
                <LocalizationProvider className="" dateAdapter={AdapterDateFns}>
                    <MobileTimePicker
                        label="End Time"
                        value={schedule[index].to}
                        disabled={index === (schedule.length - 1)}
                        onChange={(newValue) => {
                            const next = {from:newValue,to:schedule[index+1].to,i:schedule[index+1].i};
                            const current = {from:schedule[index].from,to:newValue,i:schedule[index].i};
                            setSchedule([
                                ...schedule.slice(0,index),
                                current,
                                next,
                                ...schedule.slice(index+2)
                            ]);
                            setEndTime(newValue);
                        }}
                        renderInput={(params) => <TextField {...params} />}
                    />
                </LocalizationProvider>
            </Grid>
            <Grid item xs={2}>
                <FormControl sx={{ m: 1, minWidth: 120 }}>
                    <InputLabel id="intensity-label">
                        Intensity
                    </InputLabel>
                    <Select
                        labelId="intensity-label"
                        value={schedule[index].i}
                        onChange={(e) => {
                            setSchedule([
                                ...schedule.slice(0,index),
                                {...schedule[index],i:e.target.value},
                                ...schedule.slice(index+1)
                            ]);
                            setIntensity(e.target.value);
                        }}
                        label="Intensity"
                    >
                        <MenuItem value={25}>25</MenuItem>
                        <MenuItem value={50}>50</MenuItem>
                        <MenuItem value={75}>75</MenuItem>
                        <MenuItem value={100}>100</MenuItem>
                    </Select>
                </FormControl>
            </Grid>
        </Grid>
    )
}