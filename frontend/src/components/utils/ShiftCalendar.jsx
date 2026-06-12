import { useState, useEffect } from "react";
import { Box, Typography, Paper, Button, IconButton, Stack } from "@mui/material";
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

// Turn the optimizer's flat assignment list into a per-date lookup:
//   [{employee, date, shift}] -> { "2026-07-01": { morning: "alice, bob" } }
const assignmentsToMap = (payload) => {
  const assignments = Array.isArray(payload?.assignments) ? payload.assignments : [];
  const map = {};
  assignments.forEach(({ date, shift, employee }) => {
    if (!map[date]) map[date] = {};
    map[date][shift] = map[date][shift]
      ? `${map[date][shift]}, ${employee}`
      : employee;
  });
  return map;
};

const localDateKey = (date) => {
  // Avoid toISOString()'s UTC shift, which can roll the date back a day.
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
};

const ShiftCalendar = () => {
  const { user } = useAuth();
  const today = new Date();

  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [dates, setDates] = useState(generateDates(currentMonth, currentYear));
  const [shiftData, setShiftData] = useState({});
  const [publishStatus, setPublishStatus] = useState(false);
  const [hasSchedule, setHasSchedule] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  const isManager = !!user?.is_manager;

  const fetchShiftData = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/api/optimizedShift/${isManager ? "manager" : "employee"}/?year=${currentYear}&month=${currentMonth + 1}`,
        { credentials: "include" }
      );
      if (res.ok) {
        const data = await res.json();
        setPublishStatus(data.publish_status);
        setShiftData(assignmentsToMap(data.data));
        setHasSchedule(true);
      } else {
        setPublishStatus(false);
        setShiftData({});
        setHasSchedule(false);
      }
    } catch (err) {
      console.error(err);
      setPublishStatus(false);
      setShiftData({});
      setHasSchedule(false);
    }
  };

  useEffect(() => {
    setDates(generateDates(currentMonth, currentYear));
    fetchShiftData();
    setMessage("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentMonth, currentYear, user]);

  const prevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear((y) => y - 1);
    } else setCurrentMonth((m) => m - 1);
  };

  const nextMonthFunc = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear((y) => y + 1);
    } else setCurrentMonth((m) => m + 1);
  };

  // Manager: run the optimization pipeline for the displayed month.
  const handleGenerate = async () => {
    setBusy(true);
    setMessage("Generating schedule…");
    try {
      const res = await fetch(
        `http://localhost:8000/api/shift/manager/?year=${currentYear}&month=${currentMonth + 1}`,
        { method: "POST", credentials: "include" }
      );
      const body = await res.json().catch(() => ({}));
      if (res.ok) {
        setMessage(`Schedule generated (status: ${body?.data?.status ?? "ok"}).`);
        await fetchShiftData();
      } else {
        setMessage(`Could not generate: ${body?.error ?? res.status}`);
      }
    } catch (err) {
      setMessage(`Could not generate: ${err}`);
    } finally {
      setBusy(false);
    }
  };

  // Manager: publish the generated schedule to employees.
  const handlePublish = async () => {
    setBusy(true);
    try {
      const res = await fetch(
        `http://localhost:8000/api/optimizedShift/manager/?year=${currentYear}&month=${currentMonth + 1}`,
        { method: "POST", credentials: "include" }
      );
      const body = await res.json().catch(() => ({}));
      setMessage(res.ok ? "Schedule published." : `Could not publish: ${body?.error ?? res.status}`);
      await fetchShiftData();
    } catch (err) {
      setMessage(`Could not publish: ${err}`);
    } finally {
      setBusy(false);
    }
  };

  const monthName = new Date(currentYear, currentMonth).toLocaleString("default", { month: "long" });
  const firstDayWeekday = new Date(currentYear, currentMonth, 1).getDay();
  const emptySlots = Array.from({ length: firstDayWeekday });

  // Managers see the draft schedule; employees only see it once published.
  const scheduleVisible = isManager || publishStatus;
  const showNotPublishedOverlay = !isManager && !publishStatus;

  return (
    <Box sx={{ p: 2, display: "flex", justifyContent: "center", position: "relative" }}>
      <Paper sx={{ p: 2, width: "100%", height: "100%", maxWidth: 1000, overflowX: "visible", position: "relative" }}>
        {/* Month header */}
        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", mb: 2 }}>
          <IconButton onClick={prevMonth}>＜</IconButton>
          <Typography variant="h5" sx={{ mx: 2 }}>{monthName} {currentYear}</Typography>
          <IconButton onClick={nextMonthFunc}>＞</IconButton>
        </Box>

        {/* Manager controls */}
        {isManager && (
          <Stack direction="row" spacing={2} sx={{ mb: 2, justifyContent: "center", alignItems: "center" }}>
            <Button variant="contained" onClick={handleGenerate} disabled={busy}>
              Generate schedule
            </Button>
            <Button variant="outlined" onClick={handlePublish} disabled={busy || !hasSchedule}>
              Publish
            </Button>
            {message && <Typography variant="body2">{message}</Typography>}
          </Stack>
        )}

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
            const key = localDateKey(date);
            const morning = scheduleVisible ? shiftData[key]?.morning || "-" : "-";
            const evening = scheduleVisible ? shiftData[key]?.evening || "-" : "-";

            return (
              <Paper key={key} sx={{ p: 1, textAlign: "center" }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>{key}</Typography>
                <Button
                  variant="contained"
                  sx={{
                    width: "100%",
                    mb: 0.5,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "pre-line",
                    fontSize: "0.75rem",
                    minWidth: 0,
                    px: 0.5,
                    pointerEvents: "none",
                    cursor: "default",
                    backgroundColor: "#70B2B2",
                    color: "white",
                    "&:hover": { backgroundColor: "#70B2B2" },
                  }}
                  title={morning}
                >
                  {morning}
                </Button>

                <Button
                  variant="contained"
                  sx={{
                    width: "100%",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "pre-line",
                    fontSize: "0.75rem",
                    minWidth: 0,
                    px: 0.5,
                    pointerEvents: "none",
                    cursor: "default",
                    backgroundColor: "#70B2B2",
                    color: "white",
                    "&:hover": { backgroundColor: "#70B2B2" },
                  }}
                  title={evening}
                >
                  {evening}
                </Button>
              </Paper>
            );
          })}
        </Box>

        {showNotPublishedOverlay && (
          <Box sx={{ position: "absolute", top: 60, left: 0, width: "100%", height: "100%", backgroundColor: "rgba(255,255,255,0.7)", display: "flex", justifyContent: "center", alignItems: "center", fontSize: 24, fontWeight: "bold", color: "red", zIndex: 10 }}>
            Not published
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default ShiftCalendar;
