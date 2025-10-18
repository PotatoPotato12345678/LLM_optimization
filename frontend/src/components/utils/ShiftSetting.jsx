import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  TextField,
  FormControlLabel,
  Checkbox,
  Button,
  Divider,
  Grid,
  Snackbar,
  Alert,
  Paper,
} from "@mui/material";

const ShiftSetting = () => {
  const [settings, setSettings] = useState({
    workplace_name: "",
    num_shifts_per_day: 2,
    working_days: ["Mon", "Tue", "Wed", "Thu", "Fri"],
    holidays: [],
    allow_weekend_work: false,
    max_consecutive_shifts: 5,
    min_rest_hours: 8,
    publish_auto: false,
  });

  const [saved, setSaved] = useState(false);

  const nextMonth = new Date().getMonth() === 11 ? 0 : new Date().getMonth() + 1;
  const nextMonthYear =
    new Date().getMonth() === 11 ? new Date().getFullYear() + 1 : new Date().getFullYear();

  // Fetch manager's hard_rule JSON on mount
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/api/shift/manager/?year=${nextMonthYear}&month=${nextMonth + 1}`,
          { credentials: "include" }
        );
        if (res.ok) {
          const data = await res.json();
          // data.hard_rule assumed to be a JSON object
          if (data.hard_rule) {
            setSettings(data.hard_rule);
          }
        }
      } catch (err) {
        console.error("Error fetching manager hard_rule:", err);
      }
    };
    fetchSettings();
  }, [nextMonth, nextMonthYear]);

  // Save the JSON settings to hard_rule
  const handleSave = async () => {
    try {
      // Only send the settings object as hardRule
      const payload = { hardRule: settings };

      const res = await fetch(
        `http://localhost:8000/api/shift/manager/?year=${nextMonthYear}&month=${nextMonth + 1}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(payload),
        }
      );
      if (res.ok) setSaved(true);
      else {
        const errorData = await res.json();
        console.error("Failed to save hardRule:", errorData);
      }
    } catch (err) {
      console.error("Error saving hard_rule:", err);
    }
  };


  const toggleDay = (day) => {
    setSettings((prev) => {
      const workingDays = prev.working_days || [];
      const isActive = workingDays.includes(day);
      return {
        ...prev,
        working_days: isActive
          ? workingDays.filter((d) => d !== day)
          : [...workingDays, day],
      };
    });
  };

  const handleChange = (field, value) => {
    setSettings((prev) => ({ ...prev, [field]: value }));
  };

  const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  return (
    <Box sx={{ p: 4, display: "flex", justifyContent: "center" }}>
      <Paper sx={{ p: 4, width: "100%", maxWidth: 900 }}>
        <Typography variant="h4" sx={{ mb: 3 }}>
          Workplace Settings / Hard Rule
        </Typography>

        <Grid container spacing={3}>
          {/* Workplace Name */}
          <Grid item xs={12} sm={6}>
            <TextField
              label="Workplace Name"
              value={settings.workplace_name}
              onChange={(e) => handleChange("workplace_name", e.target.value)}
              fullWidth
            />
          </Grid>

          {/* Number of Shifts */}
          <Grid item xs={12} sm={6}>
            <TextField
              label="Number of Shifts per Day"
              type="number"
              value={settings.num_shifts_per_day}
              onChange={(e) =>
                handleChange("num_shifts_per_day", Number(e.target.value))
              }
              fullWidth
              inputProps={{ min: 1, max: 5 }}
            />
          </Grid>

          {/* Working Days */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Working Days
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
              {weekDays.map((day) => (
                <Button
                  key={day}
                  variant={
                    (settings.working_days || []).includes(day)
                      ? "contained"
                      : "outlined"
                  }
                  onClick={() => toggleDay(day)}
                >
                  {day}
                </Button>
              ))}
            </Box>
          </Grid>

          {/* Allow Weekend Work */}
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={settings.allow_weekend_work || false}
                  onChange={(e) =>
                    handleChange("allow_weekend_work", e.target.checked)
                  }
                />
              }
              label="Allow weekend work"
            />
          </Grid>

          <Divider sx={{ width: "100%", my: 2 }} />

          {/* Advanced Rules */}
          <Grid item xs={12} sm={6}>
            <TextField
              label="Max Consecutive Shifts"
              type="number"
              fullWidth
              value={settings.max_consecutive_shifts}
              onChange={(e) =>
                handleChange("max_consecutive_shifts", Number(e.target.value))
              }
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Min Rest Hours Between Shifts"
              type="number"
              fullWidth
              value={settings.min_rest_hours}
              onChange={(e) =>
                handleChange("min_rest_hours", Number(e.target.value))
              }
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={settings.publish_auto || false}
                  onChange={(e) =>
                    handleChange("publish_auto", e.target.checked)
                  }
                />
              }
              label="Automatically publish generated shifts"
            />
          </Grid>

          {/* Save button */}
          <Grid item xs={12}>
            <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSave}
                sx={{ mt: 2 }}
              >
                Save Settings
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Snackbar */}
      <Snackbar
        open={saved}
        autoHideDuration={3000}
        onClose={() => setSaved(false)}
      >
        <Alert severity="success">Settings saved successfully!</Alert>
      </Snackbar>
    </Box>
  );
};

export default ShiftSetting;
