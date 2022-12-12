import { React, useState, useEffect, useRef } from "react";
import axios from "axios";
import { Typography, Slider, Button, Tabs, Tab, Box, Dialog,DialogActions,DialogContent,DialogContentText,DialogTitle } from "@mui/material";
import NodeItem from "./NodeItem";
import { Link } from "react-router-dom";
import Checkbox from "@mui/material/Checkbox";
import CircularProgress from "@mui/material/CircularProgress";
import { green } from "@mui/material/colors";
import url from "./BaseURL";
import { useNodeContext } from "../NodeContext";
import PropTypes from "prop-types";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import { TimeSelecter } from "./TimeSelecter";
import RemoveCircleIcon from "@mui/icons-material/RemoveCircle";
import AddCircleIcon from "@mui/icons-material/AddCircle";
import HourglassBottomIcon from "@mui/icons-material/HourglassBottom";
import "./nodes.css";
import classnames from "classnames";

const Nodes = () => {
  const {
    nodes,
    global,
    tabVal,
    setNodes,
    setGlobalToggle,
    setGlobalDim,
    setInstValues,
    setGlobalTick,
  } = useNodeContext();
  const [loading, setLoading] = useState(false);
  // loadingOnOff: set true on pressing All On/Off button
  const [loadingOnOff, setLoadingOnOff] = useState(false);
  // loadingTelemetry: set true on pressing Telemetry button
  const [loadingTelemetry, setLoadingTelemetry] = useState(false);
  const [syncloading, setSyncloading] = useState(false);
  const [applyloading, setApplyloading] = useState(false);
  const [tab, setTab] = useState(tabVal);
  const [sun, setSun] = useState({ sunrise: 0, sunset: 0 });
  const [autoSchedule, setAutoSchedule] = useState([]);
  // pointerEvent: set true to make all clickable things unclickable. 
  const [pointerEvent, setPointerEvent] = useState(false);
  const [telemetryStatus, setTelemetryStatus] = useState(true);
  const [scheduleStatus, setScheduleStatus] = useState(true);
  // AlerDialog open or close?
  const [open, setOpen] = useState(false);

  const handleChangeTab = (event, newValue) => {
    setTab(newValue);
  };

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

  const buttonSx = {
    ...(loading && {
      bgcolor: green[700],
      "&:hover": {
        bgcolor: green[900],
      },
    }),
  };

  const handleChange = (event, newValue) => {

    if (newValue !== global.globalValue) {
      // current dimming value
      console.log(newValue);
      setPointerEvent(true);
      axios
        .put(url + "dimming/", {
          params: { 
            isGlobal: true, 
            value: newValue },
        })
        .then((res) => {
          setGlobalDim(newValue);
          console.log(nodes);
          setPointerEvent(false);
        });
    }
  };
  useEffect(() => {
    axios.get(url + "getNodes/").then((res) => {
      setNodes(res.data.nodes);
      console.log(res.data.nodes);
      console.log(nodes);
    });
  }, []);

  useEffect(() => {
    axios
      .get(url + "setTelemetry/",)
      .then((res) => {
        console.log("useEffect of setTelemetry");
        setTelemetryStatus(res.data.status);
      })
    if (global.isGlobal === true) {
      axios
        .get(url + "toggle/", 
        // {
        //   params: {
        //     isGlobal: true,
        //     status: global.globalStatus ? "on" : "off",
        //   },
        // }
        )
        .then((res) => {
          console.log(res.data.relay)
          // setGlobalToggle(global.globalStatus);
          setGlobalToggle(res.data.relay);
          console.log(nodes);
        });
      axios
        .get(url + "dimming/", 
        // {
          // params: { 
          //   isGlobal: true, value: global.globalValue },
        // }
        )
        .then((res) => {
          // set current value
          setGlobalDim(res.data.intensity);
          console.log(nodes);
        });

    }
  }, [global.isGlobal]);

  useEffect(() => {
    axios.get(url + "activateSchedule/")
    .then((res) => {
      setScheduleStatus(res.data.status);
    })

    axios.get(url + "getSchedule/").then((res) => {
      console.log(res);
      setSun({ sunrise: res.data.sunrise, sunset: res.data.sunset });
      setAutoSchedule(res.data.schedule);
    });
  }, []);

  const handleButtonClick = () => {
    if (!loading) {
      setLoading(true);
      axios.get(url + "discover/").then((res) => {
        setLoading(false);
        setNodes(res.data.nodes);
      });
    }
  };

  function TabPanel(props) {
    const { children, value, index, ...other } = props;

    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`simple-tabpanel-${index}`}
        aria-labelledby={`simple-tab-${index}`}
        {...other}
      >
        {value === index && (
          <Box sx={{ p: 3 }}>
            <Typography>{children}</Typography>
          </Box>
        )}
      </div>
    );
  }

  TabPanel.propTypes = {
    children: PropTypes.node,
    index: PropTypes.number.isRequired,
    value: PropTypes.number.isRequired,
  };

  function a11yProps(index) {
    return {
      id: `simple-tab-${index}`,
      "aria-controls": `simple-tabpanel-${index}`,
    };
  }

  return (
    // <div className="lg:container md:mx-auto mt-8 z-0">
    <div className={classnames("lg:container md:mx-auto mt-8 z-0", {"content-pointer-event-none": pointerEvent})}>
      <div className="flex grid grid-flow-col grid-cols-6 gap-4 items-center m-8 mx-10 p-6 bg-gray-200 rounded-md  ">
        <div className="flex col-span-4 items-center justify-start text-2xl text-primary font-bold ">
          Area Name
        </div>
      </div>
      <Box className="p-6 m-4">
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs
            value={tab}
            onChange={handleChangeTab}
            aria-label="basic tabs example"
          >
            <Tab label="AUTO" {...a11yProps(0)} />
            <Tab label="MANUAL" {...a11yProps(1)} />
          </Tabs>
        </Box>
        <TabPanel value={tab} index={0}>
          <div className="flex grid grid-flow-row-dense grid-cols-9 grid-rows-2 gap-4 items-center p-4 bg-blue-200 bg-opacity-25 rounded-md">
            <div className="flex col-span-3 items-center justify-center p-4 rounded-md ">
              <LightModeIcon className="text-yellow-500" />
              <span className="font-bold text-gray-700">
                &nbsp; Sunrise Time: &nbsp;
              </span>
              <span className="p-4 bg-gray-50 rounded-md shadow-md text-white bg-blue-500 font-bold">
                {sun.sunrise}
              </span>
            </div>
            <div className="flex col-span-3 items-center justify-center p-4 rounded-md ">
              <div className="flex col-span-3 items-center justify-start p-4 bg-blue-100 rounded-md">
                <HourglassBottomIcon className="text-gray-700" />
                <span className="font-bold text-gray-700">
                  &nbsp; For Non-Peak Hours: &nbsp;
                </span>
              </div>
            </div>
            <div className="flex col-span-3 items-center justify-center rounded-md ">
              <DarkModeIcon className="text-blue-500" />
              <span className="font-bold text-gray-700">
                &nbsp; Sunset Time: &nbsp;
              </span>
              <span className="p-4 bg-gray-50 rounded-md shadow-md text-white bg-blue-500 font-bold">
                {sun.sunset}
              </span>
            </div>

            {autoSchedule.map((s, idx) => (
              <div className="flex col-start-3 col-span-5 items-center justify-center rounded-md">
                <div className="flex items-center justify-center rounded-md mr-16">
                  <div className="flex col-start-3 col-span-5 items-center justify-center rounded-md">
                    <div className="flex items-center justify-center rounded-md mr-16">
                      <TimeSelecter
                        val={s}
                        idx={idx}
                        sch={autoSchedule}
                        setSch={setAutoSchedule}
                      />
                    </div>
                  </div>
                  {/* <div className="flex col-start-8 col-span-1 items-center justify-center p-4 rounded-md">
                  <div className="flex items-center justify-center rounded-md mr-16">
                    <RemoveCircleIcon className="text-red-500" />
                  </div>
                </div> */}
                </div>
              </div>
            ))}
          </div>
          <div className="flex grid grid-flow-row grid-cols-9 gap-4 grid-rows-1 p-4 bg-blue-200 bg-opacity-25 rounded-md">
          <Button
              className="col-start-4 col-span-2"
              variant="contained"
              sx={buttonSx}
              //disabled={syncloading}
              backgroundColor="red"
              onClick={() => {
                if(scheduleStatus)
                {
                  setOpen(true);
                }
                else {
                axios
                  .put(url + "activateSchedule/",{
                    params: {
                      status: !scheduleStatus,
                    },
                  }
                  )
                  .then((res) => {
                  setScheduleStatus(!scheduleStatus);
                });
              }
              }}
            >
              {scheduleStatus ? "Disable ":"Enable "}Schedules
              {loading && (
                <CircularProgress
                  color="success"
                  size={24}
                  sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    marginTop: "-12px",
                    marginLeft: "-12px",
                  }}
                />
              )}
            </Button>
            <Dialog 
              open={open}
              onClose={() => {setOpen(false)}}
              aria-labelledby="alert-dialog-title"
              aria-describedby="alert-dialog-description"
            >
              <DialogTitle id="alert-dialog-title">
                {"ALERT: Disable Schedules?"}
              </DialogTitle>
              <DialogContent>
                <DialogContentText id="alert-dialog-description">
                  System will not follow schedules on disabling schedules.
                </DialogContentText>
              </DialogContent>
              <DialogActions>
                <Button onClick={() => {setOpen(false)}}>NO</Button>
                <Button onClick={() => {
                  axios
                  .put(url + "activateSchedule/",{
                    params: {
                      status: !scheduleStatus,
                    },
                  }
                  )
                  .then((res) => {
                  setScheduleStatus(!scheduleStatus);
                  setOpen(false);
                });
                }} 
                autoFocus>
                  YES
                </Button>
              </DialogActions>
            </Dialog>
            <Button
              className="col-start-6 col-span-2"
              variant="outlined"
              sx={buttonSx}
              disabled={syncloading || !scheduleStatus}
              onClick={() => {
                setSyncloading(true);
                axios.get(url + "sync/").then((res) => {
                  setSyncloading(false);
                });
              }}
            >
              Sync with Auto
              {loading && (
                <CircularProgress
                  color="success"
                  size={24}
                  sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    marginTop: "-12px",
                    marginLeft: "-12px",
                  }}
                />
              )}
            </Button>
            <Button
              className="col-start-8 col-span-2"
              variant="contained"
              sx={buttonSx}
              disabled={applyloading}
              onClick={() => {
                //run validation
                setApplyloading(true);
                setPointerEvent(true);
                axios
                  .post(url + "setSchedule/", {
                    schedule: autoSchedule,
                  })
                  .then((res) => {
                    //if (res.data.succ == "done")
                      setApplyloading(false);
                      setPointerEvent(false);

                  });
              }}
            >
              Apply Changes
              {loading && (
                <CircularProgress
                  color="success"
                  size={24}
                  sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    marginTop: "-12px",
                    marginLeft: "-12px",
                  }}
                />
              )}
            </Button>
          </div>
        </TabPanel> 
        <TabPanel value={tab} index={1}>
          <div className="flex grid grid-flow-col grid-cols-13 gap-4 items-center mx-10 p-4 bg-blue-200 bg-opacity-25 rounded-md">
            <div className="flex items-center col-span-2 justify-start">
              <Checkbox
                checked={global.isGlobal}
                onChange={() => {
                  setGlobalTick(!global.isGlobal);
                }}
                inputProps={{ "aria-label": "controlled" }}
              />
              <span>
                <Typography className="text-gray-500">
                  Global connection &nbsp; &nbsp;
                </Typography>
              </span>
            </div>

            <div className="flex col-span-1 items-center justify-end">
              <Button
                variant="contained"
                sx={buttonSx}
                disabled={loading}
                onClick={handleButtonClick}
              >
                Discover
                {loading && (
                  <CircularProgress
                    color="success"
                    size={24}
                    sx={{
                      position: "absolute",
                      top: "50%",
                      left: "50%",
                      marginTop: "-12px",
                      marginLeft: "-12px",
                    }}
                  />
                )}
              </Button>
            </div>
            <div className="flex col-start-6 col-span-4 items-center">
              <span>
                <Typography className="text-gray-500">
                  Light Intensity &nbsp; &nbsp;
                </Typography>
              </span>
              <span>{/* <AddCircle onClick={handleIncr} /> */}</span>
              <Slider
                className="ml-2"
                disabled={!global.isGlobal}
                step={null}
                defaultValue={global.globalValue}
                marks={marks}
                min={25}
                max={100}
                // to update
                value={global.globalValue}
                onChange={handleChange}
                sx={{
                  "& .MuiSlider-mark": {
                    height: "8px",
                  },
                }}
              ></Slider>
            </div>

            <div className="flex col-start-10 col-span-2 items-centers justify-end ">
              <Button
                disabled={!global.isGlobal || loadingOnOff}
                onClick={() => {
                  setPointerEvent(true);
                  setLoadingOnOff(true);
                  axios
                    .put(url + "toggle/", {
                      params: {
                        isGlobal: true,
                        status: global.globalStatus ? "off" : "on",
                      },
                    })
                    .then((res) => {
                      setGlobalToggle(!global.globalStatus);
                      console.log(nodes);
                      setPointerEvent(false);
                      setLoadingOnOff(false);
                    });
                }}
                color={global.globalStatus ? "success" : "error"}
                variant={global.globalStatus ? "contained" : "outlined"}
              >
                All On/Off
                {loadingOnOff && (
                  <CircularProgress
                    color="success"
                    size={24}
                    sx={{
                      position: "absolute",
                      top: "50%",
                      left: "50%",
                      marginTop: "-12px",
                      marginLeft: "-12px",
                    }}
                  />
                )}
              </Button>
            </div>

            <div className="flex col-start-13 col-span-2 items-centers ">
              <Button
                disabled={loadingTelemetry}
                onClick={() => {
                  setPointerEvent(true);
                  setLoadingTelemetry(true);

                  axios
                    .put(url + "setTelemetry/", {
                      params: {
                        status: !telemetryStatus,
                      },
                    })
                    .then((res) => {
                      setTelemetryStatus(!telemetryStatus);
                      setPointerEvent(false);
                      setLoadingTelemetry(false);
                    });

                  // console.log("Hi this is telemetry button")
                  // setPointerEvent(false);
                  // setLoadingTelemetry(false);
                }}
                color={telemetryStatus ? "success" : "error"}
                variant={telemetryStatus ? "contained" : "outlined"}
              >
                Telemetry
                {loadingTelemetry && (
                  <CircularProgress
                    color="success"
                    size={24}
                    sx={{
                      position: "absolute",
                      top: "50%",
                      left: "50%",
                      marginTop: "-12px",
                      marginLeft: "-12px",
                    }}
                  />
                )}
              </Button>
            </div>
          </div>
          <ul className="flex items-center justify-center grid grid-flow-row grid-cols-3 grid-rows-3 gap-4 p-6">
            {nodes.map((item) => (
              <li key={item.id}>
                <NodeItem item={item} />
              </li>
            ))}
          </ul>
        </TabPanel>
      </Box>
      {/* <Box sx={{ width: "30%" }}>
        <Alert className="m-8" severity="warning">
          Temperature Exceeding- Check it out!
        </Alert>
      </Box> */}
    </div>
  );
};

export default Nodes;
