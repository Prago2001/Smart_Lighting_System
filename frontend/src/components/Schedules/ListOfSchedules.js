import React, { useState,useEffect } from "react";
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import CreateNewSchedule from './CreateNewSchedule';
import axios from "axios";
import url from "../BaseURL";
import ScheduleItem from "./ScheduleItem";



function ListOfAllSchedules(){

    const [newSchedule,setNewSchedule] = useState(false);
    const [listSchedules,setList] = useState([]);

    useEffect(() => {
        axios
            .get(url + 'getAllSchedules/')
            .then((res) => {
                setList(res.data.schedules);
            })

    },[])

    const handleCreateScheduleClose = () => {
        setNewSchedule(false);
    }

    return (
        <div>
            <div className='text-2xl bg-blue-100 p-4 rounded-md text-gray-700 font-semibold mb-2'>
                List of All Schedules
            </div>
            <div className='grid justify-end my-6'>
                <Button
                    variant='contained'
                    onClick={() => setNewSchedule(true)}
                >
                    Create new schedule
                </Button>
                {newSchedule && 
                    <CreateNewSchedule 
                        open={true} 
                        onClose={handleCreateScheduleClose}
                        setSchedules={setList}
                    />
                }
            </div>
            <Stack spacing={1}>
                {
                    listSchedules.map((schedule,index) => (
                        
                        <ScheduleItem 
                            schedule={schedule} 
                            id={index} 
                            schedules={listSchedules}
                            setSchedules={setList}
                        />
                        
                    ))
                }
            </Stack>
        </div>
    )
}



export default ListOfAllSchedules;