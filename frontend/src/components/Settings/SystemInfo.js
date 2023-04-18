import React, { useState,useEffect } from "react";
import Typography from '@mui/material/Typography';
import axios from "axios";
import url from "../BaseURL";

export default function SystemInfo(){
    const [version,setVersion] = useState("");
    const [releaseDate,setReleaseDate] = useState("");
    const [city,setCity] = useState("");
    const [lat,setLat] = useState("");
    const [lon,setLon] = useState("");

    useEffect(() => {
      axios
      .get(url + "systemInformation/")
      .then((res) => {
        setVersion(res.data.version);
        setReleaseDate(res.data.release_date);
        setCity(res.data.city);
        setLat(res.data.lat);
        setLon(res.data.lon);
      })
      .catch((err) => {
        console.error("Error in system information");
      })
    
      
    }, [])
    


    return (
        <div>
            <Typography variant='h5'>
                System Information
            </Typography>
            <Typography variant="overline">
                System Location: {city} <br/>
                Latitude: {lat} &emsp; Longitude: {lon} <br/>
                Version Number: {version} <br/>
                Release Date: {releaseDate}
            </Typography>
        </div>
    )
}