import React, { useState,useEffect } from "react";
import Grid from '@mui/material/Grid';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import classnames from "classnames";
import AreaName from "./AreaName";
import EnableDisableSchedule from "./EnableDisableSchedules";
import EnableDisableTelemetry from "./EnableDisableTelemetry";
import SyncWithAutoInterval from "./SyncWithAutoInterval";
import SystemInfo from "./SystemInfo";

export default function DisplaySettings(){
    
    const [currentSetting,setSetting] = useState("default");
    const options = [
        "Area Name",
        "Enable/Disable Schedules",
        "Enable/Disable Telemetry",
        "Sync with Auto Interval",
        "System Info"
    ];
    return(
        <Grid container spacing={1} sx={{height:'100%',m:4,p:4,ml:-4,fontSize:20,mt:-4}}>
            <Grid item xs={4} className="" >
                <List >
                        {options.map((text,index) => (
                            <ListItem
                                disablePadding
                                className="border-b-2 border-gray-100"
                            >
                                <ListItemButton onClick={() => setSetting(text)}>
                                    <ListItemText
                                        primary={text} primaryTypographyProps={{fontSize: 20}}/>
                                </ListItemButton>
                            </ListItem>
                        ))}
                </List>
            </Grid>
            <Divider orientation="vertical" flexItem/>
            <Grid item xs={7} sx={{m:2}}>
                {(() => {
                    if(currentSetting === 'default'){
                        return(
                            <div></div>
                        )
                    }
                    else if(currentSetting === "Area Name"){
                        return(
                            <div>
                                <AreaName/>
                            </div>
                        )
                    }
                    else if (currentSetting === "Enable/Disable Schedules"){
                        return (
                            <EnableDisableSchedule/>
                        )
                    }
                    else if(currentSetting === "Enable/Disable Telemetry"){
                        return (
                            <EnableDisableTelemetry/>
                        )
                    }
                    else if(currentSetting === "Sync with Auto Interval"){
                        return (
                            <SyncWithAutoInterval/>
                        )
                    }
                    else if(currentSetting === "System Info"){
                        return(
                            <SystemInfo/>
                        )
                    }
                })()}
            </Grid>
        </Grid>
    )
}
