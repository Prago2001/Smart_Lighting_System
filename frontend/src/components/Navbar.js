import { React, useState, useEffect } from "react";
import axios from "axios";
import url from "./BaseURL";
import { Link } from "react-router-dom";
import EmojiObjectsIcon from "@mui/icons-material/EmojiObjects";
import Notifications from "react-notifications-menu";
// import Alert from '@mui/material/Alert';
// import AlertTitle from '@mui/material/AlertTitle';
function Navbar({ fixed }) {
  // const DEFAULT_NOTIFICATION = {
  //   image:
  //     "https://t3.ftcdn.net/jpg/01/34/49/84/360_F_134498430_vn2ciA0xKdMnxKIl1oAv4cY6qkybEBnz.webp",
  //   message: "Temperature Exceeding-Check it out!",
  //   detailPage: "/nodes",
  //   receivedTime: "3h ago",
  // };

  const [data, setData] = useState([]);
  
  useEffect(() => {
    axios.get(url + "alerts/")
      .then((res) => {
      setData(res.data.alerts);
      console.log(res.data.alerts);
      })
      .catch((error) => console.log(error));

    const interval = setInterval(() => {
      axios.get(url + "alerts/").then((res) => {
        setData(res.data.alerts);
        console.log(res.data.alerts);
      })
      .catch((error) => console.log(error));
    },300000);
    return () => clearInterval(interval);

  },[])


  // const [navbarOpen, setNavbarOpen] = React.useState(false);
  return (
    <nav class="bg-gray-700 py-4 md:py-4 text-white text-2xl font-semibold">
      <div class="grid grid-cols-3 sm:grid-cols-6 justify-center">

        <div class="flex justify-center items-center col-span-2 col-start-1">
          <EmojiObjectsIcon className="flex items-center" />
          <span className="ml-2">Light It Up!</span>
        </div>
        <div class="flex justify-center items-center col-span-2 col-start-3">
          <span class="text-4xl uppercase">{JSON.parse(localStorage.getItem("area_name"))}</span>
        </div>
        <div class="flex justify-center items-center col-span-2 col-start-5">
          <Notifications
            icon="https://assets.ifttt.com/images/channels/651849913/icons/monochrome_large.png"
            data={data}
            // markAsRead={data => console.log(data)}
            header={{
              title: "Alerts",
              option: { text: "Mark as Read All", onClick:( () => {
                let array = new Array();
                data.map((record) => {
                  array.push(record.id)
                })
                axios.put(url + 'alerts/',{
                  params : {id_array : array}
                })
                .then((res) => {
                  setData([]);
                })
              })}
            }}
          />
        </div>

        
      </div>
    </nav>

  )

}

export default Navbar;
