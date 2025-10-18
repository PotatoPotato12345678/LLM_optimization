import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Divider,
  Grid,
  Snackbar,
  Alert,
  Paper,
} from "@mui/material";

const ShiftSetting = () => {
  const [settings, setSettings] = useState({
    num_shifts_per_day: 2,
    time_open: "09:00",
    time_close: "20:00",
  });

  const [saved, setSaved] = useState(false);

  const nextMonth =
    new Date().getMonth() === 11 ? 0 : new Date().getMonth() + 1;
  const nextMonthYear =
    new Date().getMonth() === 11
      ? new Date().getFullYear() + 1
      : new Date().getFullYear();

  // Fetch manager's hard_rule JSON on mount
  useEffect(() => {
    console.log("Current settings:", settings);
  }, [settings]);

  // Save the JSON settings to hard_rule
  const handleSave = async () => {
    try {
      const payload = { hardRule: settings };
      const res = await fetch(
        `http://localhost:8000/api/shift/manager/?year=${nextMonthYear}&month=${
          nextMonth + 1
        }`,
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

  const handleChange = (field, value) => {
    setSettings((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>
        基本情報の設定
      </Typography>
      <Box sx={{ p: 4, display: "flex", justifyContent: "center" }}>
        <Paper sx={{ p: 4, width: "100%" }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item sx={{ flex: 1 }}>
              <TextField
                label="Business open time"
                type="time"
                fullWidth
                value={settings.time_open ?? "09:00"}
                onChange={(e) => handleChange("time_open", e.target.value)}
              />
            </Grid>

            <Grid item sx={{ flex: 1 }}>
              <TextField
                label="Business close time"
                type="time"
                fullWidth
                value={settings.time_close ?? "22:00"}
                onChange={(e) => handleChange("time_close", e.target.value)}
              />
            </Grid>

            <Grid item sx={{ flex: 1 }}>
              <TextField
                label="Number of shifts per day"
                type="number"
                fullWidth
                InputProps={{ inputProps: { min: 1, max: 10 } }}
                value={settings.num_shifts_per_day ?? 2}
                onChange={(e) =>
                  handleChange(
                    "num_shifts_per_day",
                    Math.max(1, parseInt(e.target.value || 1, 10))
                  )
                }
              />
            </Grid>

            <Grid item xs={12} sx={{ textAlign: "right", mt: 1 }}>
              <Button variant="contained" color="primary" onClick={handleSave}>
                Save
              </Button>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />
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
    </Box>
  );
};

export default ShiftSetting;
