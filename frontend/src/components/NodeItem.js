import { React, useState, useEffect } from "react";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import { Grid } from "@mui/material";
import Brightness6Icon from "@mui/icons-material/Brightness6";
import FlashOnIcon from "@mui/icons-material/FlashOn";
import DeviceThermostatIcon from "@mui/icons-material/DeviceThermostat";
import { Link } from "react-router-dom";
import axios from "axios";
import url from "./BaseURL";
import { useNodeContext } from "../NodeContext";
import classnames from "classnames";


const NodeItem = ({ item, ticked }) => {
  const { global,setIO } = useNodeContext();
  const [isActive,setIsActive] = useState (item.is_active);

  return (
    <div className={classnames("flex flex-wrap items-center justify-center hover:shadow-md hover:scale-100 rounded-md py-4",
    {'bg-blue-100' : isActive === true},
    {'bg-red-100' : isActive === false}
    )}>
      <Grid
        container
        xs={12}
        // spacing={1}
        className="flex items-center justify-center"
      >
        <Grid item xs={4} className="flex items-center justify-center">
          <Link to={`/node/${item.id}`}>
            <div className="flex font-bold text-gray-500 text-xl justify-start">
              {item.id}
            </div>
          </Link>
        </Grid>
        <Grid item xs={2} className="flex items-center justify-center">
          <div className="flex justify-end">
            <Switch
              checked={item.relay}
              disabled={global.isGlobal}
              onChange={() => {
                axios
                  .put(url + "toggle/", {
                    params: { id: item.id, status: item.relay ? "off" : "on" },
                  })
                  .then((res) => {
                    if(res.data.operation === true){
                      setIO(item.id, "relay", !item.relay);
                    }
                    else{
                      setIsActive(false);
                    }
                    
                    console.log(item);
                  });
              }}
              inputProps={{ "aria-label": "controlled" }}
            />
          </div>
        </Grid>
        <Grid item xs={2} className="flex items-center justify-center">
          <Brightness6Icon className="text-blue-500" />
          <Typography className="text-gray-600">&nbsp; {item.dim} %</Typography>
        </Grid>
        <Grid item xs={2} className="flex items-center justify-center">
          <FlashOnIcon className="text-yellow-500" />
          <Typography className="text-gray-600">
            &nbsp; {item.current} mA
          </Typography>
        </Grid>
        <Grid item xs={2} className="flex items-center justify-center">
          <DeviceThermostatIcon className="text-red-500" />
          <Typography className="text-gray-600">
            &nbsp; {item.temp} &deg; C
          </Typography>
        </Grid>
      </Grid>
    </div>
  );
};

export default NodeItem;
