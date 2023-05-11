import React, { useState } from "react";
import Typography from '@mui/material/Typography';

export default function SystemInfo(){


    return (
        <div>
            <Typography variant='h5'>
                System Information
            </Typography>
            <Typography variant="overline">
                Version Number: 4.2.1 <br/>
                Release Date: 11 May 2023
            </Typography>
        </div>
    )
}