import { useState, useEffect } from "react";
import { Box, Typography, TextField } from "@mui/material";
import AvailabilityCalendar from "./utils/AvailabilityCalendar";
import { useAuth } from "./utils/AuthContext";

let timeoutId;

const EmployeeInput = () => {
  const { userRef } = useAuth();
  const [content, setContent] = useState("");

  const nextMonth = new Date().getMonth() === 11 ? 0 : new Date().getMonth() + 1;
  const nextMonthYear = new Date().getMonth() === 11 ? new Date().getFullYear() + 1 : new Date().getFullYear();

  // Function to update content to backend
  const updateContent = async (value) => {
    try {
      await fetch(`http://localhost:8000/api/shift/employee/?year=${nextMonthYear}&month=${nextMonth + 1}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ content: value }),
      });
    } catch (err) {
      console.error("Error updating content:", err);
    }
  };

  // Handle input change with debounce
  const handleChange = (e) => {
    const value = e.target.value;
    setContent(value);

    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(() => updateContent(value), 500); // 500ms debounce
  };

  // Optional: fetch current content when component mounts
  useEffect(() => {
    const fetchContent = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/api/shift/employee/?year=${nextMonthYear}&month=${nextMonth + 1}`,
          { credentials: "include" }
        );
        if (res.ok) {
          const data = await res.json();
          if (data.content) setContent(data.content);
        }
      } catch (err) {
        console.error("Error fetching content:", err);
      }
    };
    fetchContent();
  }, [nextMonth, nextMonthYear]);

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Preference
      </Typography>

      {/* Content Input */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Additional Notes / Preferences
        </Typography>
        <TextField
          label="Content"
          placeholder="Write your preferences or notes here..."
          multiline
          minRows={4}
          maxRows={8}
          fullWidth
          value={content}
          onChange={handleChange}
          sx={{ width: "95%", maxWidth: 1000  }}
        />
      </Box>

      <Typography variant="h4" sx={{ mb: 3 }}>
        Calendar
      </Typography>

      <Box sx={{ mb: 4 }}>
        <Typography variant="h6">
          Please submit your availability for the next month here
        </Typography>
      </Box>

      {/* Availability Calendar */}
      <Box>
        <AvailabilityCalendar />
      </Box>
    </Box>
  );
};

export default EmployeeInput;
