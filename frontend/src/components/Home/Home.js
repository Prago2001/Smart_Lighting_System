import React, { useEffect, useState} from 'react';
import WbSunnyRoundedIcon from '@mui/icons-material/WbSunnyRounded';
import WbTwilightRoundedIcon from '@mui/icons-material/WbTwilightRounded';
import WbIncandescentRoundedIcon from '@mui/icons-material/WbIncandescentRounded';
import LightOutlinedIcon from '@mui/icons-material/LightOutlined';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import BoltOutlinedIcon from '@mui/icons-material/BoltOutlined';
import axios from "axios";
import url from '../BaseURL';
import classnames from "classnames";



export default function Home(){

    const [sunrise,setSunrise] = useState("");
    const [sunset,setSunset] = useState("");
    const [total,setTotal] = useState(0)
    const [active,setActive] = useState(0);
    const [relay,setRelay] = useState(false);
    const [intensity,setIntensity] = useState(25);
    const [operation,setOperation] = useState("");
    const [status,setStatus] = useState("");
    const [energy,setEnergy] = useState(0);


    useEffect(() => {
        axios
        .get(url + "information/")
        .then((res) => {
            console.log(res.data);
            localStorage.setItem('sunrise',JSON.stringify(res.data.sunrise_ts));
            localStorage.setItem('sunset',JSON.stringify(res.data.sunset_ts));
            setSunrise(res.data.sunrise);
            setSunset(res.data.sunset);
            setTotal(res.data.total_nodes);
            setActive(res.data.active_nodes);
            setRelay(res.data.relay);
            setIntensity(res.data.intensity);
            setOperation(res.data.schedule);
            setStatus(res.data.schedule_status);
            setEnergy(res.data.energy_saved);
          })
          .catch((error) => console.log(error));

    }, [])
    

    return (
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 justify-center">
            <div class="bg-yellow-500 shadow-2xl p-6 rounded-2xl">
                <div class="flex items-center">
                    <span class="flex items-center justify-center rounded-full">
                        <WbSunnyRoundedIcon fontSize="large" />
                    </span>
                    <span class="ml-2 text-2xl font-semibold text-black">Sunrise</span>
                </div>
                <span class="block text-4xl font-semibold mt-4 text-left">{sunrise}</span>
            </div>
            <div class="bg-gray-200 shadow-2xl p-6 rounded-2xl">
                <div class="flex items-center place-content-center">
                    <span class="flex items-center justify-center rounded-full">
                        <WbIncandescentRoundedIcon fontSize="large"/>
                    </span>
                    <span class="ml-2 text-2xl font-semibold text-black justify-center">Street Lights</span>
                </div>
                <span class="block text-4xl font-semibold mt-4 text-center">{active} / {total}</span>
            </div>
            <div class="bg-yellow-500 shadow-2xl p-6 rounded-2xl ">
                <div class="flex items-center place-content-end">
                    <span class="mr-2 text-2xl font-semibold text-black justify-center">Sunset</span>
                    <span class="flex items-center justify-center rounded-full">
                        <WbTwilightRoundedIcon fontSize="large"/>
                    </span>
                    
                </div>
                <span class="block text-4xl font-semibold mt-4 text-right">{sunset}</span>    
            </div>
            <div class="bg-green-500 shadow-2xl p-6 rounded-2xl col-span-2">
                <div class="flex items-center place-content-center">
                    <span class="mr-2 text-2xl font-semibold text-white  justify-center">Energy Saved</span>
                    <span class="flex items-center justify-start rounded-full">
                        <BoltOutlinedIcon fontSize="large" color="warning"/>
                    </span>
                    
                </div>
                <span class="block text-4xl font-semibold mt-4 text-center text-white">{energy} kWh</span>    
            </div>
            
            <div class="bg-gray-200 shadow-2xl p-6 rounded-2xl col-span-1">
                <div class="flex items-center place-content-start">
                    <span class="mr-2 text-2xl font-semibold text-black  justify-center">Current Status</span>
                    <span class="flex items-center justify-start rounded-full">
                        <InfoOutlinedIcon fontSize="large" color="info"/>
                    </span>
                    
                </div>
                { relay ? 
                    (<span class="block text-4xl font-semibold mt-4 text-left">Lights are ON at {intensity}% intensity</span> )
                    :
                    (<span class="block text-4xl font-semibold mt-4 text-left">Lights are OFF</span> )
                }
                <span class="block text-4xl font-semibold mt-4 text-left"></span>    
            </div>
            <div class="bg-gray-700 shadow-2xl p-6 rounded-2xl col-span-3">
                <div class="flex items-center place-content-center">
                    <span class="mr-2 text-2xl font-semibold text-gray-100 justify-center">Next Operation</span>
                    <span class="flex items-center justify-center rounded-full">
                    <LightOutlinedIcon fontSize="large" color="info"/>
                    </span>
                    
                </div>
                <span class="block text-4xl font-semibold mt-4 text-left text-gray-100">{operation}</span>    
            </div>
            
        </div>
    )
}
