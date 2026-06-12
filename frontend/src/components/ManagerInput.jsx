import { useState, useEffect } from "react";
import { Box, Paper, Typography, TextField } from "@mui/material";
import { useAuth } from "./utils/AuthContext";
import ShiftSetting from "./utils/ShiftSetting"

let timeoutIdContent;

const ManagerInput = () => {
  const { userRef } = useAuth();
  const [hardRule, setHardRule] = useState("");
  const [content, setContent] = useState("");

  const today = new Date();
  const nextMonth = today.getMonth() === 11 ? 0 : today.getMonth() + 1;
  const nextMonthYear = today.getMonth() === 11 ? today.getFullYear() + 1 : today.getFullYear();

  // 🧠 Unified PUT update function
  const updateField = async (field, value) => {
    try {
      await fetch(`http://localhost:8000/api/shift/manager/?year=${nextMonthYear}&month=${nextMonth + 1}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ [field]: value }),
      });
    } catch (err) {
      console.error(`Error updating ${field}:`, err);
    }
  };

  // 🕐 Fetch current data when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/api/shift/manager/?year=${nextMonthYear}&month=${nextMonth + 1}`,
          { credentials: "include" }
        );
        if (res.ok) {
          const data = await res.json();
          // hard_rule is the *structured* rules object owned by <ShiftSetting/>
          // below; only the free-text notes ("content") are edited here.
          if (data.content) setContent(data.content);
        }
      } catch (err) {
        console.error("Error fetching manager data:", err);
      }
    };
    fetchData();
  }, [nextMonth, nextMonthYear]);

  // ✏️ Debounced update handlers
  // Structured hard rules consumed by the optimizer (workers per shift, business
  // hours, etc.) are managed by <ShiftSetting/> below, which PUTs them under the
  // `hardRule` key. This free-text box is a local scratch pad only, so it never
  // overwrites those structured rules.
  const handleHardRuleChange = (e) => {
    setHardRule(e.target.value);
  };

  const handleContentChange = (e) => {
    const value = e.target.value;
    setContent(value);

    if (timeoutIdContent) clearTimeout(timeoutIdContent);
    timeoutIdContent = setTimeout(() => updateField("content", value), 600);
  };

  return (
    <Box sx={{ p: 4, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
      <Paper sx={{ p: 4, width: "100%", maxWidth: 1000 }}>
        <Typography variant="h4" sx={{ mb: 3, textAlign: "center" }}>
          Manager Requirements
        </Typography>

        {/* Hard Rules Input */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>
            Hard Rules
          </Typography>
          <TextField
            label="Hard Rules"
            placeholder="e.g., Each employee must have 2 days off per week, no night shifts after consecutive days, etc."
            multiline
            minRows={4}
            maxRows={8}
            fullWidth
            value={hardRule}
            onChange={handleHardRuleChange}
          />
        </Box>

        {/* Content / Notes Input */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>
            Additional Notes
          </Typography>
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
      </Paper>

      <ShiftSetting />
    </Box>

  );
};

export default ManagerInput;
