import React, { useState } from "react";
import Typography from '@mui/material/Typography';

export default function SystemInfo(){


    return (
        <div>
            <Typography variant='h5'>
                System Information
            </Typography>
            <Typography variant="overline">
                Version Number: 3.4
            </Typography>
        </div>
    )
}