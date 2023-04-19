import { React, useState, useEffect } from "react";
import axios from "axios";
import url from "./BaseURL";
import Snackbar from '@mui/material/Snackbar';
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import classnames from "classnames";
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';


export default function Status(props) {
    
    const [open,setOpen] = useState(props.open);
    const [success,setSucces] = useState(props.success);
    const [operation,setOperation] = useState(props.operation);
    const [msg,setMsg] = useState(props.msg);


    const handleClose = () => {
        setOpen(false);
        props.close();
    }

    function alertMessage(){
        
        if(operation === "toggle"){
            if(success === true){
                return (
                    <div>
                        Toggle operation was successful!
                    </div>
                )
            }
            else{
                return(
                    <div>
                        Toggle operation failed for following nodes!<br/>
                        <ul class='list-disc'>
                            {msg.map(id => <li>{id}</li>)}
                        </ul>
                    </div>
                )
                
            }
        }
        else if(operation === "dim"){
            if(success === true){
                return (
                    <div>
                        Dimming operation was successful!
                    </div>
                )
            }
            else{
                return(
                    <div>
                        Dimming operation failed for following nodes!<br/>
                        <ul class='list-disc'>
                            {msg.map(id => <li>{id}</li>)}
                        </ul>
                    </div>
                )
                
            }
        }
        else if(operation === "sync"){
            if(success === true){
                console.log(success,msg,operation)
                return (
                    <div>
                        Sync with auto operation was successful!
                    </div>
                )
            }
            else{
                return(
                    <div>
                        Sync with auto operation failed for following nodes!<br/>
                        <ul class='list-disc'>
                            {msg.map(id => <li>{id}</li>)}
                        </ul>
                    </div>
                )
            }
        }
        else if(operation === "discover"){
            if(success === true){
                return (
                    <div>
                        Discover operation was successful!
                    </div>
                )
            }
            else{
                return (
                    <div>
                        Discover operation failed!
                    </div>
                )
            }
        }
    }

    return (
        <Snackbar
            open={open}
            // autoHideDuration={3000}
            anchorOrigin ={{vertical:'bottom',horizontal:'right'}}
            onClose={handleClose}
        >
            <Alert 
                severity={success ? "success" : "error"}
                color={success ? "success" : "error"} 
                sx={{ width: '100%',fontSize:20 }}
                onClose={handleClose}
            >
                <AlertTitle sx={{fontWeight:'bold'  }}>{success ? "Success" : "Error"}</AlertTitle>
                {alertMessage()}
            </Alert>

        </Snackbar>
    )
    
}