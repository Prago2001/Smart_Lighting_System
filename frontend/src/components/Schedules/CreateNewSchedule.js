import React, { useState, useEffect } from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Button from "@mui/material/Button";
import { TextField } from "@mui/material";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";
import Typography from "@mui/material/Typography";
import Slot from "./Slot";
import axios from "axios";
import url from "../BaseURL";

export default function CreateNewSchedule(props) {
  const [open, setOpen] = useState(props.open);
  const [name, setName] = useState("");
  const [slots, setSlots] = useState(3);
  const sunrise = JSON.parse(localStorage.getItem("sunrise"));
  const sunset = JSON.parse(localStorage.getItem("sunset"));
  const [makeActive, setMakeActive] = useState(false);
  const [schedule, setSchedule] = useState([
    { from: sunset, to: "", i: 100 },
    { from: "", to: "", i: 100 },
    { from: "", to: sunrise, i: 100 },
  ]);
  const [disableSubmitButton,setDisable] = useState(true);

  const handleClose = () => {
    setOpen(false);
    props.onClose();
  };
  const handleSubmit = () => {
    // setOpen(false);
    console.log(schedule);
    props.onClose();
    axios
      .post(url + "createOrEditSchedule/", {
        schedule_name: name,
        no_of_slots: slots,
        make_active: makeActive,
        schedule: schedule,
      })
      .then((res) => {
        setOpen(false);
        axios
            .get(url + 'getAllSchedules/')
            .then((res) => {
                props.setSchedules(res.data.schedules);
            })
      });
  };

  const handleChange = (event) => {
    const newValue = event.target.value;

    console.log(slots - newValue);
    if (slots - newValue === -1) {
      const data = {
        from: schedule.slice(-2, -1)[0].to,
        to: schedule.slice(-1)[0].from,
        i: 100,
      };
      setSchedule([...schedule.slice(0, -1), data, ...schedule.slice(-1)]);
    } else if (slots - newValue === -2) {
      const data = [
        { from: schedule.slice(-2, -1)[0].to, to: "", i: 100 },
        { from: "", to: schedule.slice(-1)[0].from, i: 100 },
      ];
      setSchedule([...schedule.slice(0, -1), ...data, ...schedule.slice(-1)]);
    } else if (slots - newValue === 1) {
      setSchedule([...schedule.slice(0, -2), ...schedule.slice(-1)]);
    } else if (slots - newValue === 2) {
      setSchedule([...schedule.slice(0, -3), ...schedule.slice(-1)]);
    }
    setSlots(newValue);
  };

  return (
    <Dialog
      open={open}
      fullWidth={true}
      sx={{
        fontSize: 24,
      }}
      maxWidth="xl"
    >
      <DialogTitle>Create New Schedule</DialogTitle>
      <form>
        <DialogContent>
          <TextField
            label="Schedule Name"
            variant="outlined"
            required
            value={name}
            onChange={(e) => {
                setName(e.target.value);
                setDisable(false);
                if(e.target.value === ""){
                    setDisable(true);
                }
            }}
            fullWidth
            size="large"
            sx={{
              my: 4,
            }}
          />
          <br />
          <FormControl sx={{ my: 2 }}>
            <InputLabel htmlFor="slots-label">Slots</InputLabel>
            <Select
              value={slots}
              label="Slots"
              onChange={handleChange}
              id="slots-label"
            >
              <MenuItem value={3}>3</MenuItem>
              <MenuItem value={4}>4</MenuItem>
              <MenuItem value={5}>5</MenuItem>
            </Select>
            <br />
            <FormControlLabel
              control={
                <Checkbox
                  checked={makeActive}
                  onChange={(e) => setMakeActive(e.target.checked)}
                />
              }
              label="Mark schedule as active? (System will follow this schedule)"
              sx={{
                my: 3,
              }}
            />
          </FormControl>
          <DialogContentText
            sx={{
              fontSize: 18,
              color: "black",
              mb: 3,
            }}
          >
            Sunrise Time: {new Date(sunrise).toLocaleTimeString()} <br />
            Sunset Time: {new Date(sunset).toLocaleTimeString()}
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
          <Button variant="outlined" onClick={handleClose}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleSubmit} type="Submit" disabled={disableSubmitButton}>
            Submit
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
