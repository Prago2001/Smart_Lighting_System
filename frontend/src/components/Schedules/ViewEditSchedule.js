import React, { useState, useEffect } from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Button from "@mui/material/Button";
import Snackbar from '@mui/material/Snackbar';
import Typography from "@mui/material/Typography";
import Slot from "./Slot";
import axios from "axios";
import url from "../BaseURL";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import Divider from "@mui/material/Divider";
import CancelIcon from '@mui/icons-material/Cancel';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Alert from '@mui/material/Alert';

export default function ViewEditSchedule(props) {
  const [open, setOpen] = useState(true);
  const [name, setName] = useState(props.name);
  const [slots, setSlots] = useState(null);
  const sunrise = JSON.parse(localStorage.getItem("sunrise"));
  const sunset = JSON.parse(localStorage.getItem("sunset"));
  const [makeActive, setMakeActive] = useState(null);
  const [schedule, setSchedule] = useState([]);
  const [makeActiveAlert,setMakeActiveAlert] = useState(false);
  const [editFeedback,setEditFeedback] = useState(false);

  const handleClose = () => {
    setOpen(false);
    props.closeEditSchedule();
  };

  const handleEdit = () => {
    setEditFeedback(false);
    axios
      .put(url + "createOrEditSchedule/",{
        schedule_name: name,
        schedule: schedule,
      })
      .then((res) => {
        console.info("Edit Schedule Successful");
        if(res.data.message === "Success"){
          setEditFeedback(true);
        }
      })
  }

  const handleActivate = () => {
    axios
        .put(url + 'changeActiveSchedule/', {
            schedule : {
                schedule_name: name
            }
        })
        .then((res) => {
            setMakeActive(true);
            setMakeActiveAlert(false)
            props.updateScheduleList();
        })
  }

  useEffect(() => {
    axios
      .get(url + "getScheduleInfo/", {
        params: {
          schedule_name: props.name,
        },
      })
      .then((res) => {
        setName(res.data.schedule_name);
        setSlots(res.data.no_of_slots);
        setMakeActive(res.data.currently_active);
        setSchedule(res.data.slots);
      });
  }, []);

  return (
    <Dialog
      open={open}
      fullWidth={true}
      sx={{
        fontSize: 24,
      }}
      maxWidth="xl"
    >
      <DialogTitle sx={{ fontSize: 26 }}>
        Edit Schedule
        <IconButton
          onClick={handleClose}
          sx={{
            position: "absolute",
            right: 8,
            top: 8,
          }}
        >
          <CloseIcon fontSize="large" />
        </IconButton>
      </DialogTitle>
      <Divider />
      <form>
        <DialogContent>
          <DialogContentText
            sx={{
              fontSize: 18,
              color: "black",
              mb: 3,
            }}
            className="space-y-2"
          >
            <Typography variant="h6">
              Name of Schedule: <span className="font-bold">{name}</span>
            </Typography>
            <Typography variant="h6">
              Number of slots: <span className="font-bold">{slots}</span>
            </Typography>
            <Typography variant="h6">
              Schedule Active: <span className="font-bold">
                {
                    makeActive ? <CheckCircleIcon className="text-green-600"/> : <CancelIcon className="text-red-500"/>
                }
              </span>
              
            </Typography>
            <Typography variant="h6">
              Sunrise Time:{" "}
              <span className="font-bold">
                {new Date(sunrise).toLocaleTimeString()}
              </span>
            </Typography>
            <Typography variant="h6">
              Sunset Time:{" "}
              <span className="font-bold">
                {new Date(sunset).toLocaleTimeString()}
              </span>
            </Typography>
          </DialogContentText>

          {schedule.map((value, index) => (
            <Slot
              value={value}
              index={index}
              schedule={schedule}
              setSchedule={setSchedule}
            />
          ))}
        </DialogContent>
        <DialogActions>
          <Button 
            variant="contained"
            color="error"
            onClick={() => setMakeActiveAlert(true)}
            disabled={makeActive}
           >
            Activate Schedule
           </Button>
           {
            <Dialog
              open={makeActiveAlert}
              sx={{
                fontSize:20
              }}
            >
              <DialogTitle>
                Alert!
              </DialogTitle>
              <DialogContent>
                <DialogContentText>
                  The system will follow the selected schedule
                </DialogContentText>
                <DialogActions>
                  <Button
                    variant='contained'
                    onClick={() => setMakeActiveAlert(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="contained"
                    color="error"
                    onClick={handleActivate}
                  >
                    Activate
                  </Button>
                </DialogActions>
              </DialogContent>

            </Dialog>
           }
           <Button
            variant="contained"
            onClick={handleEdit}
           >
            Apply Changes
           </Button>

        </DialogActions>
      </form>
      <Snackbar
        open={editFeedback}
        autoHideDuration={3000}
        anchorOrigin ={{vertical:'top',horizontal:'right'}}
        onClose={() => setEditFeedback(false)}
      >
        <Alert severity="success" sx={{ width: '100%',fontSize:24 }}>
          Edit operation was successful!
        </Alert>

      </Snackbar>
    </Dialog>
  );
}
