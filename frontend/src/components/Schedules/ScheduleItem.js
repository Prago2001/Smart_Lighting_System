import React, { useState,useEffect } from "react";
import Button from '@mui/material/Button';
import TaskAltIcon from '@mui/icons-material/TaskAlt';
import DeleteForeverOutlinedIcon from '@mui/icons-material/DeleteForeverOutlined';
import axios from "axios";
import url from "../BaseURL";
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import ViewEditSchedule from "./ViewEditSchedule";



function ScheduleItem({schedule,index,schedules,setSchedules}){
    const [deleteAlert,setDeleteAlert] = useState(false);
    const [editSchedule,setEditSchedule] = useState(false);

    const updateScheduleList = () => {
        axios
            .get(url + 'getAllSchedules/')
            .then((res) => {
                setSchedules(res.data.schedules);
                // console.log('updateScheduleList');
            })
    };

    const handleEditScheduleClose = () => {
        setEditSchedule(false);
    };

    const handleDelete = () => {
        axios.
            delete(url + 'deleteSchedule/',{
                data : {
                    schedule_name : schedule.schedule_name
                }
            })
            .then((res) => {
                axios
                    .get(url + 'getAllSchedules/')
                    .then((res) => {
                        setSchedules(res.data.schedules);
                    })  
                
            })
        setDeleteAlert(false);
    }



    return(
        <div className='grid grid-flow-col grid-cols-10 gap-4 items-center  text-xl font-normal p-4  bg-gray-100 rounded-md '>
            <div className='flex col-span-4 justify-start font-bold'>
                {schedule.schedule_name}
            </div>
            <div className='flex col-span-1 justify-center'>
                {schedule.currently_active ? <TaskAltIcon className="text-green-600" fontSize="large"/> :  "" }
                
            </div>
            <div className='flex col-span-3 justify-around'>
                <Button 
                    variant="contained"
                    onClick={() => setEditSchedule(true)}
                >
                    VIEW/EDIT
                </Button>
                {
                    editSchedule && 
                    <ViewEditSchedule 
                        closeEditSchedule={handleEditScheduleClose}
                        name={schedule.schedule_name}
                        updateScheduleList={updateScheduleList}
                    />
                }
            </div>
            <div className='flex col-span-2 justify-around'>
                <Button 
                    variant="contained"
                    color="error"
                    disabled={schedule.currently_active}
                    onClick={()=> setDeleteAlert(true)}
                >
                    <DeleteForeverOutlinedIcon />
                </Button>
            </div>
            {
                deleteAlert && 
                <Dialog
                    open={deleteAlert}
                    onClose={() => setDeleteAlert(false)}
                >
                    <DialogTitle>Warning</DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            Are you sure you want to delete the selected schedule?
                        </DialogContentText>
                        <DialogActions>
                            <Button 
                                onClick={() => {setDeleteAlert(false)}}
                                variant="outlined"
                            >
                                NO
                            </Button>
                            <Button
                                onClick={handleDelete}
                                variant="contained"
                                color="error"
                            >
                                YES
                            </Button>

                        </DialogActions>
                    </DialogContent>

                </Dialog>
            }
        </div>
    )

}

export default ScheduleItem;