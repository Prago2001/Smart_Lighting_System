import { React, useState, useEffect, useRef } from "react";
import axios from "axios";
import { Typography, Slider, Button, Tabs, Tab, Box, Dialog,DialogActions,DialogContent,DialogContentText,DialogTitle } from "@mui/material";
import NodeItem from "./NodeItem";
import { Link } from "react-router-dom";
import Checkbox from "@mui/material/Checkbox";
import CircularProgress from "@mui/material/CircularProgress";
import { green,yellow } from "@mui/material/colors";
import {darken} from "@mui/material/styles";
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
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Fade from "@mui/material/Fade";
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Stack from '@mui/material/Stack';
import DisplayLogs from "./Logs/DisplayLogs";
import ListOfAllSchedules from "./Schedules/ListOfSchedules";
import DisplaySettings from "./Settings/DisplaySettings";
import Home from "./Home/Home";


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
  const [displaySuccessTab,setDisplaySuccessTab] = useState(false);
  const [retryAlert,setRetryAlert] = useState(false);
  const [retryNodes,setRetryNodes] = useState([]);
  const [displayAlertTab,setDisplayAlertTab] = useState(false);
  const [failedNodes,setFailedNodes] = useState([]);
  const [logs,setLogs] = useState([]);

  const handleChangeTab = (event, newValue) => {
    setTab(newValue);
    if(newValue == 1)
    {
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
          // console.log(res.data.relay)
          // setGlobalToggle(global.globalStatus);
          setGlobalToggle(res.data.relay);
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
          // console.log(nodes);
        });
      axios.get(url + "getNodes/").then((res) => {
        setNodes(res.data.nodes);
        console.log(res.data.nodes);
        console.log(nodes);
      });
    }
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

  // const buttonSx = {
  //   ...(loading && {
  //     bgcolor: green[700],
  //     "&:hover": {
  //       bgcolor: green[900],
  //     },
  //   }),
  // };

  const handleChange = (event, newValue) => {

    if (newValue !== global.globalValue) {
      // current dimming value
      console.log(newValue);
      setPointerEvent(true);
      setLoadingOnOff(true);
      setDisplayAlertTab(false);
      setDisplaySuccessTab(false);
      axios
        .put(url + "dimming/", {
          params: { 
            isGlobal: true, 
            value: newValue },
        })
        .then((res) => {
          setGlobalDim(newValue);
          setLoadingOnOff(false);
          setPointerEvent(false);
          
          if(res.data.operation == false){
            setRetryAlert(true);
            setRetryNodes(res.data.nodes);
            axios.get(url + "getRetryJobStatus/",{
            }).then((res) => {
              // console.log('Retry job done...')
              setRetryAlert(false);
              if(res.data.operation == false){
                setFailedNodes(res.data.nodes);
                setDisplayAlertTab(true);
              }
              else{
                setDisplaySuccessTab(true);
              }
              axios.get(url + "getNodes/").then((res) => {
                setNodes(res.data.nodes);
              });
              
            })
          }
          else{
            setDisplaySuccessTab(true);
            axios.get(url + "getNodes/").then((res) => {
              setNodes(res.data.nodes);
            });
          }
        });
      
    }
  };
  

  useEffect(() => {
    // axios
    //   .get(url + "setTelemetry/",)
    //   .then((res) => {
    //     console.log("useEffect of setTelemetry");
    //     setTelemetryStatus(res.data.status);
    //   })
    //   .catch((error) => console.log(error));
    if (global.isGlobal === true) {
      axios
        .get(url + "toggle/")
        .then((res) => {
          console.log(res.data.relay)
          setGlobalToggle(res.data.relay);
          console.log(nodes);
        })
        .catch((error) => console.log(error));
      axios
        .get(url + "dimming/")
        .then((res) => {
          setGlobalDim(res.data.intensity);
          console.log(nodes);
        })
        .catch((error) => console.log(error));

    }
  }, [global.isGlobal]);
  useEffect(() => {
    axios.get(url + "getNodes/").then((res) => {
      setNodes(res.data.nodes);
      console.log(res.data.nodes);
      console.log(nodes);
    })
    .catch((error) => console.log(error));
  }, []);

  useEffect(() => {
    // axios.get(url + "activateSchedule/")
    // .then((res) => {
    //   setScheduleStatus(res.data.status);
    // })
    // .catch((error) => console.log(error));
    axios
      .get(url + "areaName/")
      .then((res) => {
        localStorage.setItem('area_name',JSON.stringify(res.data.area_name));
      })
      .catch((error) => console.log(error));
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
      <Dialog
        open={retryAlert}
        sx = {{
          justifyContent: "flex-start",
          alignItems: "flex-start",
          fontSize:16,
          fontWeight: 'bold',
        }}
      >
        <DialogTitle>
          {"Operation failed for following nodes"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            <ul class='list-disc'>
              {retryNodes.map(id => <li>{id}</li>)}
            </ul>
          </DialogContentText>
          <br></br>
          <DialogContentText>
            <strong>Please Wait</strong>
          </DialogContentText>
          <DialogContentText>
            Retrying automatically in few moments...
          </DialogContentText>
            <br></br>
            <CircularProgress />
        </DialogContent>
      </Dialog>
      <div className="flex grid grid-flow-row grid-rows-2 items-center m-2 mx-10">
        <div className="flex col-span-4 items-center justify-start text-2xl text-primary font-bold bg-gray-200 p-3 rounded-md">
          {JSON.parse(localStorage.getItem("area_name"))}
        </div>
        <div className="flex col-span-4 justify-start text-2xl text-primary font-bold">
          {
            (() => {
              if(displaySuccessTab == true){
                return(
                  <Fade
                      sx={{ width: 1,fontSize:16, fontWeight: 'bold',}}
                      in={displaySuccessTab}
                      timeout={{ enter: 0, exit: 100 }} 
                    >
                      <Alert 
                        severity="success"
                        action={
                          <IconButton
                            aria-label="close"
                            color="inherit"
                            size="small"
                            onClick={() => {
                              setDisplaySuccessTab(false);
                            }}
                          >
                            <CloseIcon />
                          </IconButton>
                        }
                      >
                        <AlertTitle>Success</AlertTitle>
                        Operation was successful on all Street Lights!
                      </Alert>
                    </Fade>
                )
              }
              else if(displayAlertTab == true){
                return(
                  <Fade
                    sx={{ width: 1,fontSize:16, fontWeight: 'bold',}}
                    in={displayAlertTab}
                    timeout={{ enter: 0, exit: 0 }} 
                  >
                    <Alert 
                      severity="error"
                      action={
                        <IconButton
                            aria-label="close"
                            color="inherit"
                            size="small"
                            onClick={() => {
                              setDisplayAlertTab(false);
                            }}
                          >
                            <CloseIcon />
                          </IconButton>
                      }
                    >
                        <AlertTitle>Error</AlertTitle>
                        Operation failed for following lights:
                        <ul class='list-disc'>
                          {failedNodes.map(id => <li>{id}</li>)}
                        </ul>
                    </Alert>
                  </Fade>
                )
              }
            })()
          }
        </div>
      </div>
      
        

      <Box className="p-6 m-4">
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs
            value={tab}
            onChange={handleChangeTab}
            aria-label="basic tabs example"
          >
            <Tab label="HOME" {...a11yProps(0)} />
            <Tab label="MANUAL" {...a11yProps(1)} />
            <Tab label="SCHEDULES" {...a11yProps(2)} />
            <Tab label="LOGS" {...a11yProps(3)}/>
            <Tab label="SETTINGS" {...a11yProps(4)}/>
          </Tabs>
        </Box>
        <TabPanel value={tab} index={0}>
          <Home />
          {/* <DarkModeIcon className="text-blue-500" />
              <span className="font-bold text-gray-700">
                &nbsp; Sunset Time: &nbsp;
              </span>
              <span className="p-4 bg-gray-50 rounded-md shadow-md text-white bg-blue-500 font-bold">
                {sun.sunset}
              </span> */}
              {/* <LightModeIcon className="text-yellow-500" />
              <span className="font-bold text-gray-700">
                &nbsp; Sunrise Time: &nbsp;
              </span>
              <span className="p-4 bg-gray-50 rounded-md shadow-md text-white bg-blue-500 font-bold">
                {sun.sunrise}
              </span> */}

        </TabPanel> 
        <TabPanel value={tab} index={1}>
          <div className="flex grid grid-flow-col grid-cols-12 gap-5 items-center p-4 px-2 bg-blue-200 bg-opacity-25 rounded-md mb-7">
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

            <div className="flex col-span-2 items-center justify-center">
              <Button
                size="large"
                variant="contained"
                // sx={buttonSx}
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
            <div className="flex col-span-4 items-center justify-center">
              <span>
                <Typography className="text-gray-500">
                  Light Intensity &nbsp; &nbsp;
                </Typography>
              </span>
              <span>{/* <AddCircle onClick={handleIncr} /> */}</span>
              <Slider
                className="ml-2"
                disabled={!global.isGlobal || !global.globalStatus}
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

            <div className="flex  col-span-2 items-centers justify-center ">
              <Button
                size='large'
                disabled={!global.isGlobal || loadingOnOff}
                onClick={() => {
                  setPointerEvent(true);
                  setLoadingOnOff(true);
                  setDisplayAlertTab(false);
                  setDisplaySuccessTab(false);
                  axios
                    .put(url + "toggle/", {
                      params: {
                        isGlobal: true,
                        status: global.globalStatus ? "off" : "on",
                      },
                    })
                    .then((res) => {
                      
                      setGlobalToggle(!global.globalStatus);
                      // console.log(nodes);
                      setPointerEvent(false);
                      setLoadingOnOff(false);
                      
                      console.log(res.data.nodes)
                      if(res.data.operation == false){
                        setRetryAlert(true);
                        setRetryNodes(res.data.nodes);
                        console.log(retryAlert);
                        axios.get(url + "getRetryJobStatus/",{
                        }).then((res) => {
                          // console.log('Retry job done...')
                          if(res.data.operation == false){
                            setFailedNodes(res.data.nodes);
                            setDisplayAlertTab(true);
                          }
                          else{
                            setDisplaySuccessTab(true);
                          }
                          axios.get(url + "getNodes/").then((res) => {
                            setNodes(res.data.nodes);
                          });
                          setRetryAlert(false);
                        })
                      }
                      else{
                        setDisplaySuccessTab(true);
                        axios.get(url + "getNodes/").then((res) => {
                          setNodes(res.data.nodes);
                        });
                      }
                      
                      
                    });
                  
                }}
                color={global.globalStatus ? "error" : "success"}
                variant="contained"
              >
                Switch All {global.globalStatus ? "Off" : "On"}
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
            <div className="flex  col-span-2 items-centers justify-center ">
              <Button
                variant="contained"
                size='large'
                sx = {{
                  color:'black',
                  backgroundColor:'#ffcc00',
                  ':hover' : {
                    backgroundColor: darken('#ffcc00', 0.1),
                  }
                }}
                disabled={syncloading || !scheduleStatus || !global.isGlobal}
                onClick={() => {
                  setSyncloading(true);
                  setDisplayAlertTab(false);
                  setDisplaySuccessTab(false);
                  setPointerEvent(true);
                  
                  axios.get(url + "sync/").then((res) => {
                    
                    axios.get(url + "getRetryJobStatus/",{

                      }).then((res) => {
                      // console.log('Retry job done...')
                        if(res.data.operation == false){
                          setFailedNodes(res.data.nodes);
                          setDisplayAlertTab(true);
                        }
                        else{
                          setDisplaySuccessTab(true);
                        }
                        setSyncloading(false);
                        setPointerEvent(false);
                        axios.get(url + "getNodes/").then((res) => {
                          setNodes(res.data.nodes);
                        });
                        axios
                          .get(url + "toggle/")
                          .then((res) => {
                            console.log(res.data.relay)
                            setGlobalToggle(res.data.relay);
                            console.log(nodes);
                          })
                          .catch((error) => console.log(error));
                        axios
                          .get(url + "dimming/")
                          .then((res) => {
                            setGlobalDim(res.data.intensity);
                            console.log(nodes);
                          })
                          .catch((error) => console.log(error));
                        });

                  });
                }}
              >
                Sync with Auto
                {syncloading && (
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

            {/* <div className="flex  col-span-2 items-centers justify-end">
              <Button
                size='small'
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
                variant={telemetryStatus ? "outlined" : "contained"}
              >
                Switch {telemetryStatus ? "OFF" : "ON"} Telemetry 
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
            </div> */}
          </div>
          <Stack spacing={2}>
            {
              nodes.map((item) => (
                <NodeItem item={item} />
              ))
            }
          </Stack>
          {/* <ul className="flex items-center justify-center grid grid-flow-col auto-cols-max gap-4 p-6">
            {nodes.map((item) => (
              <li key={item.id}>
                <NodeItem item={item} />
              </li>
            ))}
          </ul> */}
        </TabPanel>
        <TabPanel value={tab} index={2}>
          <ListOfAllSchedules />
        </TabPanel>
        <TabPanel value={tab} index={3}>
          <DisplayLogs/>
        </TabPanel>
        <TabPanel value={tab} index={4}>
          <DisplaySettings/>
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
