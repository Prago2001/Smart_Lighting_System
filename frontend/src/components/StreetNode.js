import React, { useState, useEffect } from "react";
import { useParams, useHistory } from "react-router-dom";
import { Typography, Slider, Switch, Button, Dialog,DialogActions,DialogContent,DialogContentText,DialogTitle } from "@mui/material";
import { makeStyles } from "@mui/styles";
import FlashOnIcon from "@mui/icons-material/FlashOn";
import DeviceThermostatIcon from "@mui/icons-material/DeviceThermostat";
import Chart from "react-google-charts";
import axios from "axios";
import url from "./BaseURL";
import { Link } from "react-router-dom";
import { useNodeContext } from "../NodeContext";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import "./nodes.css";
import classnames from "classnames";

const useStyles = makeStyles({
  root: {
    width: 600,
  },
});

const StreetNode = () => {
  const { id } = useParams();
  const { nodes, global, setIO, setInstValues } = useNodeContext();

  const item = nodes.find((node) => node.id === id);
  const classes = useStyles();

  const [graphData, setGraphData] = useState({ curr: [], temp: [] });
  const [currError, setCurrError] = useState(false);
  const [tempError, setTempError] = useState(false);
  const [open, setOpen] = useState(false);

  const history = useHistory();

  useEffect(() => {
    const insterval = setInterval(() => {
      setCurrError(false);
      setTempError(false);
      axios
        .get(url + "graphValues/", {
          params: { id: id },
        })
        .then((res) => {
          setGraphData(res.data);
          setInstValues(id, res.data.curr[10][1], res.data.temp[10][1]);
          console.log(res.data);
        })
        .catch((error) => {
          setCurrError(true);
          setTempError(true);
        });
    }, 15000);
    return () => clearInterval(insterval);
  }, []);

  const marks = [
    {
      value: 25,
      label: "25%",
    },
    {
      value: 50,
      label: "50%",
    },
    {
      value: 75,
      label: "75%",
    },
    {
      value: 100,
      label: "100%",
    },
  ];

  return (
    <div className="lg:container md:mx-auto mt-8 z-0">
      <div className="flex grid grid-flow-col grid-cols-6 gap-4 items-center m-8 mx-10 p-4 bg-gray-200 rounded-md  ">
        <Link to="/">
          <ArrowBackIosNewIcon />
        </Link>
        <div className="flex col-span-5 items-center justify-start text-2xl text-primary font-bold ">
          {id}
        </div>
        <div className="flex col-span-1 items-center justify-end">
          <Typography className="text-lg sm:text-sm text-primary font-bold">
            On/Off&nbsp; &nbsp;{" "}
          </Typography>
          <Switch
            checked={item.relay}
            disabled={global.isGlobal}
            color="success"
            onChange={() => {
              axios
                .put(url + "toggle/", {
                  params: { id: item.id, status: item.relay ? "off" : "on" },
                })
                .then((res) => {
                  setIO(item.id, "relay", !item.relay);
                  console.log(item);
                });
            }}
            inputProps={{ "aria-label": "controlled" }}
          />
        </div>
      </div>
      <div className="flex z-99 grid grid-flow-col grid-cols-12 gap-4 items-center m-8 mx-10 ">
        <div className="flex col-span-6 items-center bg-blue-200 bg-opacity-25 rounded-md p-6">
          <span>
            <div className="text-gray-500 font-bold">
              Light Intensity &nbsp; &nbsp;
            </div>
          </span>
          <Slider
            size="large"
            className="mx-16"
            step={null}
            disabled={global.isGlobal}
            defaultValue={item.dim}
            aria-label="Default"
            valueLabelDisplay="auto"
            marks={marks}
            min={25}
            max={100}
            value={item.dim}
            onChange={(event, newValue) => {
              if (newValue !== item.dim) {
                axios
                  .put(url + "dimming/", {
                    params: { id: id, value: newValue },
                  })
                  .then((res) => {
                    setIO(id, "dim", newValue);
                  });
              }
            }}
          ></Slider>
        </div>

        <div className="flex items-center justify-center col-span-3 bg-blue-200 bg-opacity-25 rounded-md py-9 ">
          <span>
            <div className="text-gray-500 font-bold">
              Current flowing &nbsp;
            </div>
          </span>
          <FlashOnIcon className="text-yellow-500" />
          <Typography className="text-gray-600">
            {" "}
            &nbsp;{item.current} mA
          </Typography>
        </div>
        <div className="flex items-center justify-center col-span-3 bg-blue-200 bg-opacity-25 rounded-md py-9">
          <span>
            <div className="text-gray-500 font-bold">Temperature &nbsp;</div>
          </span>
          <DeviceThermostatIcon className="text-red-500" />
          <Typography className="text-gray-600">
            {" "}
            &nbsp;{item.temp} &deg; C
          </Typography>
        </div>
      </div>

      <div className="flex grid grid-flow-col gap-4 items-center justify-center mx-20 mb-20">
        
        <div className="flex grid items-center justify-center col-span-2 mx-20 ">      
            {/* <div className={classnames("flex text-gray-500 font-bold items-center justify-center display:none",{"display-error": currError})}> */}
            {currError && (<div className={classnames("flex text-gray-500 font-bold items-center justify-center display:none")}>
              Wait for 2 minutes till the values populate...
            </div>)}
          {!currError && (<Chart
            width={"550px"}
            height={"300px"}
            chartType="LineChart"
            loader={<div>Loading Chart</div>}
            data={graphData.curr}
            options={{
              hAxis: {
                title: "Time",
                maxValue: 15,
                minValue: 0,
                viewWindow: {
                  max: 10,
                },
              },
              vAxis: {
                title: "Current",
              },
              colors: ["#F59E0B"],

              legend: { position: "none" },
              explorer: { axis: "horizontal" },
              aggregationTarget: "auto",
              animation: {
                startup: true,
                duration: 1000,
                easing: "linear",
              },
            }}
            rootProps={{ "data-testid": "1" }}
          />)}
          <div className="flex text-gray-500 font-bold items-center justify-center ">
            Current Flowing
          </div>
        </div>
        <div className="flex grid items-center justify-center col-span-2 mx-20 ">
            {/* <div className={classnames("flex text-gray-500 font-bold items-center justify-center",{"display-error": tempError})}> */}
            {tempError && (<div className={classnames("flex text-gray-500 font-bold items-center justify-center")}>
              Wait for 2 minutes till the values populate...
            </div>)}
          {!tempError && (<Chart
            width={"550px"}
            height={"300px"}
            chartType="LineChart"
            loader={<div>Loading Chart</div>}
            data={graphData.temp}
            options={{
              hAxis: {
                title: "Time",
                maxValue: 15,
                minValue: 0,
                viewWindow: {
                  max: 10,
                },
              },
              vAxis: {
                title: "Temperature",
              },
              colors: ["#EF4444"],

              legend: { position: "none" },
              explorer: { axis: "horizontal" },
              aggregationTarget: "auto",
              animation: {
                startup: true,
                duration: 1000,
                easing: "linear",
              },
            }}
            rootProps={{ "data-testid": "1" }}
          />)}
          <div className="flex text-gray-500 font-bold items-center justify-center ">
            Temperature
          </div>
        </div>
      </div>

      <div className="flex grid grid-flow-row grid-cols-9 gap-4 grid-rows-1 p-6 bg-opacity-25 rounded-md">
          <Button
              className="col-start-8 col-span-2"
              variant="contained"
              color="error" 
              // sx={buttonSx}
              //disabled={syncloading}
              onClick={() => {
                setOpen(true);
                // axios
                //   .delete(url + "deleteNode/",{
                //     params: {
                //       id: id,
                //     },
                //   }
                //   )
                //   ;
              }}
            >
              Delete Node
            </Button>
            <Dialog 
              open={open}
              onClose={() => {setOpen(false)}}
              aria-labelledby="alert-dialog-title"
              aria-describedby="alert-dialog-description"
            >
              <DialogTitle id="alert-dialog-title">
                {"ALERT: Delete Node?"}
              </DialogTitle>
              <DialogContent>
                <DialogContentText id="alert-dialog-description">
                  System will delete all node related data.
                </DialogContentText>
              </DialogContent>
              <DialogActions>
                <Button onClick={() => {setOpen(false)}}>NO</Button>
                <Button onClick={() => {
                  axios
                  .put(url + "deleteNode/",{
                    params: {
                      id: item.id,
                    },
                  }
                  )
                  .then((res) => {
                    setOpen(false);
                    history.push("/");
                });
                // history.push("/");
                }} 
                autoFocus>
                  YES
                </Button>
              </DialogActions>
            </Dialog>
            
          </div>
    </div>
  );
};

export default StreetNode;
