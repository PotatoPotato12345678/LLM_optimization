import { useState, useEffect } from "react";
import { Box, Button, Typography, TextField, Paper } from "@mui/material";

const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const generateDates = (month, year) => {
  const dates = [];
  const numDays = new Date(year, month + 1, 0).getDate();
  for (let d = 1; d <= numDays; d++) {
    dates.push(new Date(year, month, d));
  }
  return dates;
};

const ShiftManager = () => {
  const today = new Date();
  const nextMonth = today.getMonth() === 11 ? 0 : today.getMonth() + 1;
  const nextMonthYear =
    today.getMonth() === 11 ? today.getFullYear() + 1 : today.getFullYear();

  const [dates, setDates] = useState(generateDates(nextMonth, nextMonthYear));
  const [data, setData] = useState({});
  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [availability, setAvailability] = useState({});
  const [content, setContent] = useState("");

  /** Fetch all employees’ availability for the selected month */
  const fetchAvailability = async () => {
    try {
      const year = nextMonthYear;
      const month = nextMonth + 1;
      const res = await fetch(
        `http://localhost:8000/api/shift/employee/?year=${year}&month=${month}`,
        { credentials: "include" }
      );

      if (res.ok) {
        const data = await res.json();
        setData(data);

        // Default to first employee
        const firstEmployee = Object.keys(data)[0];
        if (firstEmployee) {
          const emp = data[firstEmployee];
          setSelectedEmployee(firstEmployee);
          setAvailability(emp.availability_calendar || {});
          setContent(emp.content || "");
        }
      } else {
        console.warn("No shift data found");
      }
    } catch (err) {
      console.error("Error fetching availability:", err);
    }
  };

  /** Fetch data once when the component mounts */
  useEffect(() => {
    fetchAvailability();
  }, []);

  /** Generate empty calendar if selected employee has no data */
  useEffect(() => {
    if (!selectedEmployee) return;

    const empData = data[selectedEmployee];
    if (empData && empData.availability_calendar) {
      setAvailability(empData.availability_calendar);
      setContent(empData.content || "");
    } else {
      // Initialize blank calendar if no data
      const init = {};
      dates.forEach((d) => {
        const key = d.toISOString().slice(0, 10);
        init[key] = { morning: "X", evening: "X" };
      });
      setAvailability(init);
      setContent("None");
    }
  }, [selectedEmployee, data, dates]);

  const monthName = new Date(nextMonthYear, nextMonth).toLocaleString("default", {
    month: "long",
  });
  const yearName = nextMonthYear;
  const firstDayWeekday = new Date(nextMonthYear, nextMonth, 1).getDay();
  const emptySlots = Array.from({ length: firstDayWeekday }, (_, i) => i);

  return (
    <Box sx={{ p: 2, display: "flex", justifyContent: "center" }}>
      <Paper sx={{ p: 2, width: "100%", maxWidth: 1000 }}>
        <Typography variant="h4" sx={{ mb: 2 }}>
          <strong>従業員シフト表提出</strong>
        </Typography>
        {/* Employee selector */}
        <Box sx={{ mb: 2 }}>
          {Object.keys(data).map((emp) => (
            <Button
              key={emp}
              variant={emp === selectedEmployee ? "contained" : "outlined"}
              sx={{ mr: 1, mb: 1 }}
              onClick={() => setSelectedEmployee(emp)}
            >
              {emp}
            </Button>
          ))}
        </Box>

        {/* Employee content */}
        <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>
            希望欄
            </Typography>
            <TextField
            label="Content"
            multiline
            minRows={4}
            maxRows={8}
            fullWidth
            value={content}
            sx={{ width: "100%", maxWidth: 1000  }}
            />
        </Box>
        
        <Paper sx={{ p: 2, width: "96%", height: "77%", maxWidth: 1000, overflowX: "visible", position: "relative" }}>

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
                <Typography
                key={day}
                sx={{ textAlign: "center", fontWeight: "bold", color: "#fff" }}
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
                    color={availability[key]?.morning === "O" ? "success" : "error"}
                    sx={{ width: "100%", mb: 0.5 }}
                    >
                    {availability[key]?.morning || "-"}
                    </Button>
                    <Button
                    variant="contained"
                    color={availability[key]?.evening === "O" ? "success" : "error"}
                    sx={{ width: "100%" }}
                    >
                    {availability[key]?.evening || "-"}
                    </Button>
                </Paper>
                );
            })}
            </Box>
        </Paper>
      </Paper>
    </Box>
  );
};

export default ShiftManager;
