import { useState, useEffect } from "react";
import { Box, Button, Typography, Paper } from "@mui/material";

const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

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
  const nextMonthYear =
    today.getMonth() === 11 ? today.getFullYear() + 1 : today.getFullYear();
  const [dates] = useState(generateDates(nextMonth, nextMonthYear));
  const [availability, setAvailability] = useState({});

  useEffect(() => {
    const init = {};
    dates.forEach((date) => {
      const key = date.toISOString().slice(0, 10);
      init[key] = { morning: "X", evening: "X" };
    });
    console.log(init);
    setAvailability(init);
    (async () => {
      try {
        const year = nextMonthYear;
        const month = nextMonth + 1;
        const res = await fetch(
          `http://localhost:8000/api/shift/employee/?year=${year}&month=${month}`,
          {
            method: "GET",
            credentials: "include",
          }
        );
        if (res.ok) {
          const data = await res.json();
          if (data.availability_calendar)
            setAvailability(data.availability_calendar);
        }
      } catch (err) {
        console.error("Error fetching availability:", err);
      }
    })();
  }, [dates, nextMonth, nextMonthYear]);

  // fetchAvailability logic moved into useEffect to satisfy lint rules

  const toggleSlot = async (dateKey, slot) => {
    const newValue = availability[dateKey][slot] === "O" ? "X" : "O";
    const newAvailability = {
      ...availability,
      [dateKey]: { ...availability[dateKey], [slot]: newValue },
    };
    setAvailability(newAvailability);
    updateBackend(newAvailability);
  };

  const updateBackend = async (newAvailability) => {
    try {
      const year = nextMonthYear;
      const month = nextMonth + 1;
      await fetch(
        `http://localhost:8000/api/shift/employee/?year=${year}&month=${month}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ availability_calendar: newAvailability }),
        }
      );
    } catch (err) {
      console.error("Error updating availability:", err);
    }
  };

  const toggleAllWeekday = (weekdayIndex) => {
    const newAvailability = { ...availability };

    // Collect all keys for this weekday
    const weekdayKeys = dates
      .filter((date) => date.getDay() === weekdayIndex)
      .map((date) => date.toISOString().slice(0, 10));

    // Check if all are identical
    const firstKey = weekdayKeys[0];
    const allIdentical = weekdayKeys.every(
      (key) =>
        newAvailability[key].morning === newAvailability[firstKey].morning &&
        newAvailability[key].evening === newAvailability[firstKey].evening
    );

    weekdayKeys.forEach((key) => {
      if (allIdentical) {
        // Oscillate
        const morning = newAvailability[key].morning === "O" ? "X" : "O";
        const evening = newAvailability[key].evening === "O" ? "X" : "O";
        newAvailability[key] = { morning, evening };
      } else {
        // Set all to O
        newAvailability[key] = { morning: "O", evening: "O" };
      }
    });

    setAvailability(newAvailability);
    updateBackend(newAvailability);
  };

  const ResetAll = (slot) => {
    const newAvailability = {};
    Object.entries(availability).forEach(([date, data]) => {
      newAvailability[date] = {
        morning: slot === "morning" ? "X" : data.morning || "X",
        evening: slot === "evening" ? "X" : data.evening || "X",
      };
    });
    setAvailability(newAvailability);
    updateBackend(newAvailability);
  };

  const monthName = new Date(nextMonthYear, nextMonth).toLocaleString(
    "default",
    { month: "long" }
  );
  const yearName = nextMonthYear;
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
          {weekDays.map((day, idx) => (
            <Typography
              key={day}
              sx={{
                textAlign: "center",
                fontWeight: "bold",
                color: "#fff",
                cursor: "pointer",
              }}
              onClick={() => toggleAllWeekday(idx)}
            >
              {day}
            </Typography>
          ))}
        </Box>

        {/* Calendar grid */}
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(7, 1fr)",
            gap: 2,
          }}
        >
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
                  color={
                    availability[key]?.morning === "O" ? "success" : "error"
                  }
                  onClick={() => toggleSlot(key, "morning")}
                  sx={{ width: "100%", mb: 0.5 }}
                >
                  {availability[key]?.morning}
                </Button>
                <Button
                  variant="contained"
                  color={
                    availability[key]?.evening === "O" ? "success" : "error"
                  }
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
              onClick={() => ResetAll("morning")}
              sx={{ width: "100%", mb: 0.5 }}
            >
              Morning
            </Button>
            <Button
              variant="contained"
              color="error"
              onClick={() => ResetAll("evening")}
              sx={{ width: "100%" }}
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
