import React, { useState } from 'react';
import Typography from '@mui/material/Typography';
import Button from "@mui/material/Button"
import axios from "axios";
import url from "../BaseURL";
import { Dialog,DialogContent,DialogContentText,DialogTitle } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";


export default function RestartServer(){

    const [open,setOpen] = useState(false);

    const handleClick = () => {
        axios
        .post(url + 'restartServer/', {
            status:true
        })
        .then((res) => {
            setOpen(true);
            setTimeout(() => {
                window.location.reload();
            }, 60000);
        })
    }

    return(
        <div>
            <Typography variant="h5">
                Restart Server
            </Typography>
            <Typography variant="caption" sx={{mt:-2,mb:2,color:'red'}}>
                Caution: This will restart the backend server<br/>
            </Typography>
            <Button
                variant="contained"
                sx={{
                    mt:2,
                }}
                onClick={handleClick}
                color="error"
            >
                Restart Server
            </Button>
            <Dialog
                open={open}
                sx = {{
                justifyContent: "flex-center",
                alignItems: "flex-center",
                fontSize:20,
                fontWeight: 'bold',
                }}
            >
                <DialogTitle>
                    Restarting Server ...
                </DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Please Wait. Do not refresh <br/>
                    </DialogContentText>
                    <CircularProgress />
                </DialogContent>
            </Dialog>
        </div>
    )
}