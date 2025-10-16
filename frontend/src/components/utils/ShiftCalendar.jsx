import { useState, useEffect } from "react";
import { Box, Typography, Paper, Button, IconButton } from "@mui/material";
import { useAuth } from "./AuthContext";

const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

// Generate dates only
const generateDates = (month, year) => {
  const dates = [];
  const numDays = new Date(year, month + 1, 0).getDate();
  for (let d = 1; d <= numDays; d++) {
    dates.push(new Date(year, month, d));
  }
  return dates;
};

const ShiftCalendar = () => {
  const { user } = useAuth();
  const today = new Date();

  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [dates, setDates] = useState(generateDates(currentMonth, currentYear));
  const [shiftData, setShiftData] = useState({});
  const [publishStatus, setPublishStatus] = useState(false);

  const fetchShiftData = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/api/optimizedShift/${user.is_manager ? "manager" : "employee"}/?year=${currentYear}&month=${currentMonth + 1}`,
        { credentials: "include" }
      );
      if (res.ok) {
        const data = await res.json();
        setPublishStatus(data.publish_status);
        setShiftData(data.publish_status && data.data ? data.data : {});
      } else {
        setPublishStatus(false);
      }
    } catch (err) {
      console.error(err);
      setPublishStatus(false);
    }
  };

  useEffect(() => {
    setDates(generateDates(currentMonth, currentYear));
    fetchShiftData();
  }, [currentMonth, currentYear, user]);

  const prevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear((y) => y - 1);
    } else setCurrentMonth((m) => m - 1);
    console.log(shiftData);
  };

  const nextMonthFunc = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear((y) => y + 1);
    } else setCurrentMonth((m) => m + 1);
  };

  const monthName = new Date(currentYear, currentMonth).toLocaleString("default", { month: "long" });
  const firstDayWeekday = new Date(currentYear, currentMonth, 1).getDay();
  const emptySlots = Array.from({ length: firstDayWeekday});

  return (
    <Box sx={{ p: 2, display: "flex", justifyContent: "center", position: "relative" }}>
      <Paper sx={{ p: 2, width: "100%", height: "100%", maxWidth: 1000, overflowX: "visible", position: "relative" }}>
        {/* Month header */}
        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", mb: 2 }}>
          <IconButton onClick={prevMonth}>＜</IconButton>
          <Typography variant="h5" sx={{ mx: 2 }}>{monthName} {currentYear}</Typography>
          <IconButton onClick={nextMonthFunc}>＞</IconButton>
        </Box>

        {/* Weekday header */}
        <Box sx={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", mb: 1, backgroundColor: "#4a4949ff", borderRadius: 1, p: 1 }}>
          {weekDays.map((day) => (
            <Typography key={day} sx={{ textAlign: "center", fontWeight: "bold", color: "#fff" }}>{day}</Typography>
          ))}
        </Box>

        {/* Calendar grid */}
        <Box sx={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 2 }}>
          {emptySlots.map((_, i) => <Box key={`empty-${i}`} />)}

          {dates.map((date) => {
            const key = date.toISOString().slice(0, 10);
            if(key.slice(5, 7) == currentMonth){return null;}
            const morning = publishStatus ? shiftData[key]?.morning || "-" : "-";
            const evening = publishStatus ? shiftData[key]?.evening || "-" : "-";

            return (
              <Paper key={key} sx={{ p: 1, textAlign: "center" }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>{key}</Typography>
                <Button variant="contained" color="secondary" sx={{ width: "100%", mb: 0.5, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "pre-line", fontSize: "0.75rem", minWidth: 0, px: 0.5 }} disabled title={morning}>{morning}</Button>
                <Button variant="contained" color="secondary" sx={{ width: "100%", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "pre-line", fontSize: "0.75rem", minWidth: 0, px: 0.5 }} disabled title={evening}>{evening}</Button>
              </Paper>
            );
          })}
        </Box>

        {!publishStatus && (
          <Box sx={{ position: "absolute", top: 60, left: 0, width: "100%", height: "100%", backgroundColor: "rgba(255,255,255,0.7)", display: "flex", justifyContent: "center", alignItems: "center", fontSize: 24, fontWeight: "bold", color: "red", zIndex: 10 }}>
            Not published
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default ShiftCalendar;
