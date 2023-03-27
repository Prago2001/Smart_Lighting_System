import React, { useState } from 'react';
import Typography from '@mui/material/Typography';
import Button from "@mui/material/Button"
import axios from "axios";
import url from "../BaseURL";
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

export default function DeleteLogs() {
    const [openFeedback,setFeedback] = useState(false);
    const handleClick = () => {
        axios
            .delete(url + "logs/")
            .then((res) => {
                if(res.data.message === "success"){
                    setFeedback(true);
                }
            })
    }
    return (
        <div>
            <Typography variant="h5">
                Delete Logs
            </Typography>
            <Typography variant="caption" sx={{mt:-2,mb:2}}>
                Logs, current and temperature data older than 48 hours will be deleted.<br/>
            </Typography>
            <Button
                variant="contained"
                sx={{
                    mt:2,
                }}
                onClick={handleClick}
                color="error"
            >
                Delete Logs
            </Button>
            <Snackbar
                open={openFeedback}
                autoHideDuration={3000}
                anchorOrigin ={{vertical:'top',horizontal:'right'}}
                onClose={() => setFeedback(false)}
            >
                <Alert severity="success" sx={{ width: '100%',fontSize:24 }}>
                    Logs deleted successfully!
                </Alert>

            </Snackbar>
        </div>
    )
}

