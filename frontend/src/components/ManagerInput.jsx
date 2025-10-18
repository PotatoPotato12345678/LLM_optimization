import { useState, useEffect } from "react";
import { Box, Paper, Typography, TextField } from "@mui/material";
import ShiftSetting from "./utils/ShiftSetting";

const ManagerInput = () => {
  const [content, setContent] = useState("");

  const today = new Date();
  const nextMonth = today.getMonth() === 11 ? 0 : today.getMonth() + 1;
  const nextMonthYear =
    today.getMonth() === 11 ? today.getFullYear() + 1 : today.getFullYear();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/api/shift/manager/?year=${nextMonthYear}&month=${
            nextMonth + 1
          }`,
          { credentials: "include" }
        );
        if (res.ok) {
          const data = await res.json();
          if (data.content) setContent(data.content);
        }
      } catch (err) {
        console.error("Error fetching manager data:", err);
      }
    };
    fetchData();
  }, [nextMonth, nextMonthYear]);

  const handleContentChange = async (e) => {
    const value = e.target.value;
    setContent(value);
    try {
      const payload = { content: value };
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
      if (!res.ok) {
        const errorData = await res.json();
        console.error("Failed to save hardRule:", errorData);
      }
    } catch (err) {
      console.error("Error saving hard_rule:", err);
    }
  };

  return (
    <Box
      sx={{
        p: 4,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 4,
      }}
    >
      <Paper sx={{ p: 4, width: "100%", maxWidth: 1000 }}>
        <Typography variant="h4" sx={{ mb: 3, textAlign: "center" }}>
          マネージャーの希望
        </Typography>

        {/* Content / Notes Input */}
        <Box sx={{ mb: 4 }}>
          <TextField
            label="Content"
            placeholder="General scheduling notes, shift priorities, or temporary adjustments..."
            multiline
            minRows={4}
            maxRows={8}
            fullWidth
            value={content}
            onChange={handleContentChange}
          />
        </Box>

        <ShiftSetting />
      </Paper>
    </Box>
  );
};

export default ManagerInput;
