import { useState, useEffect } from "react";
import { Box, Button, Typography, Paper } from "@mui/material";

// Weekday labels
const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

// Generate dates for a given month/year
const generateDates = (month, year) => {
  const dates = [];
  const numDays = new Date(year, month + 1, 0).getDate();
  for (let d = 1; d <= numDays; d++) {
    dates.push(new Date(year, month, d));
  }
  return dates;
};

const AvailabilityCalendar = () => {
  const today = new Date();
  const nextMonth = today.getMonth() === 11 ? 0 : today.getMonth() + 1;
  const nextMonthYear = today.getMonth() === 11 ? today.getFullYear() + 1 : today.getFullYear();
  const [dates, setDates] = useState(generateDates(nextMonth, nextMonthYear));
  const [availability, setAvailability] = useState({});

  useEffect(() => {
    // Initialize empty availability for the dates
    const init = {};
    dates.forEach((date) => {
      const key = date.toISOString().slice(0, 10);
      init[key] = { morning: "X", evening: "X" };
    });
    setAvailability(init);

    // Fetch existing availability from server
    fetchAvailability();
  }, [dates]); // runs whenever `dates` changes

  const fetchAvailability = async () => {
    try {
      const year = nextMonthYear;
      const month = nextMonth + 1; // 1-based month
      const res = await fetch(`http://localhost:8000/api/shift/employee/?year=${year}&month=${month}`, {
        method: "GET",
        credentials: "include",
      });
      if (res.ok) {
        const data = await res.json();
        // `data.availability_calendar` is assumed to be the JSON field
        console.log(data.availability_calendar)
        if (data.availability_calendar) {
          setAvailability(data.availability_calendar);
        }

      } else if (res.status === 404) {
        // No existing shift requirement, initialize empty
        const init = {};
        dates.forEach((date) => {
          const key = date.toISOString().slice(0, 10);
          init[key] = { morning: "X", evening: "X" };
        });
        setAvailability(init);
      }

    } catch (err) {
      console.error("Error fetching availability:", err);
    }
  };


  const toggleSlot = async (dateKey, slot) => {
    // Optimistic UI update
    const newValue = availability[dateKey][slot] === "O" ? "X" : "O";
    const newAvailability = {
      ...availability,
      [dateKey]: {
        ...availability[dateKey],
        [slot]: newValue,
      },
    };
    setAvailability(newAvailability);

    // Send update to backend
    try {
      const year = nextMonthYear;
      const month = nextMonth + 1;
      await fetch(`http://localhost:8000/api/shift/employee/?year=${year}&month=${month}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          availability_calendar: newAvailability,
        }),
      });
    } catch (err) {
      console.error("Error updating availability:", err);
    }
  };

  const ResetAll = async (slot) => {
    const newAvailability = {};

    // Iterate over all dates
    Object.entries(availability).forEach(([date, data]) => {
      if (slot === "morning") {
        newAvailability[date] = {
          morning: "X",
          evening: data.evening || "X",
        };
      } else if (slot === "evening") {
        newAvailability[date] = {
          morning: data.morning || "X",
          evening: "X",
        };
      }
    });

    // Update state
    setAvailability(newAvailability);

    // Send update to backend
    try {
      const year = nextMonthYear;
      const month = nextMonth + 1;
      await fetch(`http://localhost:8000/api/shift/employee/?year=${year}&month=${month}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          availability_calendar: newAvailability,
        }),
      });
    } catch (err) {
      console.error("Error updating availability:", err);
    }
  };

  const yearName = new Date().getFullYear()
  const monthName = new Date(nextMonthYear, nextMonth).toLocaleString("default", { month: "long" });
  const firstDayWeekday = new Date(nextMonthYear, nextMonth, 1).getDay();
  const emptySlots = Array.from({ length: firstDayWeekday }, (_, i) => i);

  return (
    <Box sx={{ p: 2, display: "flex", justifyContent: "center" }}>
      <Paper sx={{ p: 2, width: "100%", maxWidth: 1000, overflowX: "auto" }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          {monthName} - {yearName}
        </Typography>

        {/* Weekday header */}
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(7, 1fr)",
            mb: 1,
            backgroundColor: "#4a4949ff",
            borderRadius: 1,
            p: 1,
          }}
        >
          {weekDays.map((day) => (
            <Typography key={day} sx={{ textAlign: "center", fontWeight: "bold", color: "#fff" }}>
              {day}
            </Typography>
          ))}
        </Box>

        {/* Calendar grid */}
        <Box sx={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 2 }}>
          {emptySlots.map((i) => (
            <Box key={`empty-${i}`} />
          ))}

          {dates.map((date) => {
            const key = date.toISOString().slice(0, 10);
            return (
              <Paper key={key} sx={{ p: 1, textAlign: "center" }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  {date.getDate()}
                </Typography>
                <Button
                  variant="contained"
                  color={availability[key]?.morning === "O" ? "success" : "error"}
                  onClick={() => toggleSlot(key, "morning")}
                  sx={{ width: "100%", mb: 0.5 }}
                >
                  {availability[key]?.morning}
                </Button>
                <Button
                  variant="contained"
                  color={availability[key]?.evening === "O" ? "success" : "error"}
                  onClick={() => toggleSlot(key, "evening")}
                  sx={{ width: "100%" }}
                >
                  {availability[key]?.evening}
                </Button>
              </Paper>
            );
          })}

          <Paper sx={{ p: 1, textAlign: "center" }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Reset All
            </Typography>
            <Button
              variant="contained"
              color="error"
                onClick = {() => {ResetAll("morning")}}
              sx={{ width: "100%", mb: 0.5 }}
            >
              Morning
            </Button>
            <Button
                variant="contained"
                color= "error"
                onClick = {() => {ResetAll("evening")}}
                sx={{ width: "100%", mb: 0.5 }}
            >
              Evening
            </Button>      
          </Paper>
        </Box>
      </Paper>
    </Box>
  );
};

export default AvailabilityCalendar;