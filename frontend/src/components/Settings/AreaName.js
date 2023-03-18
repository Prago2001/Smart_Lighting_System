import React, { useState } from "react";
import Typography from '@mui/material/Typography';
import { TextField,Button } from "@mui/material";
import axios from "axios";
import url from "../BaseURL";
export default function AreaName(){
    // JSON.parse(localStorage.getItem("sunrise"));
    const [name,setName] = useState(JSON.parse(localStorage.getItem("area_name")));

    const handleClick = () => {
        axios
            .put(url + "areaName/",{
                area_name : name
            })
            .then((res) => {
                localStorage.setItem('area_name',JSON.stringify(name));
                window.location.reload(true);
            });

    }
    return(
        <div>
            <Typography variant="h5">
                Set your Area Name
            </Typography>
            <TextField
                label="Area Name"
                variant="outlined"
                value={name}
                onChange={(e) => {
                    setName(e.target.value);
                }}
                fullWidth
                size="large"
                sx={{
                    mt:4,
                    fontSize:24,
                }}
            />
            <Button
                variant="contained"
                sx={{
                    mt:4
                }}
                onClick={handleClick}
            >
                Save
            </Button>
        </div>
    )
}