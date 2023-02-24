import React, { useState,useEffect } from "react";
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import CreateNewSchedule from './CreateNewSchedule';

function ListOfAllSchedules(){

    const [newSchedule,setNewSchedule] = useState(false);

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
                    onClose={handleCreateScheduleClose}/>
                }
            </div>
            <Stack spacing={1}>
                <ScheduleItem />
            </Stack>
        </div>
    )
}

function ScheduleItem(){
    return(
        <div className='grid grid-flow-col grid-cols-10 gap-4 items-center  text-xl font-normal p-4  bg-gray-100 rounded-md'>
            <div className='flex col-span-4 justify-start'>
                Schedule Name
            </div>
            <div className='flex col-span-1 justify-center'>
                Currently Active
            </div>
            <div className='flex col-span-5 justify-end'>
                <ButtonGroup size='large' variant='outlined'>
                    <Button
                        
                        color='primary'
                    >
                        VIEW/EDIT
                    </Button>
                    <Button
                        
                        color='error'
                    >
                        DELETE
                    </Button>
                </ButtonGroup>
            </div>
        </div>
    )

}

export default ListOfAllSchedules;