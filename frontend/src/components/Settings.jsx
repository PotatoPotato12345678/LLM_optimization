import { useState, useEffect } from "react";
import { Box, TextField, Button, Paper, Typography, Divider } from "@mui/material";
import { useAuth } from "./utils/AuthContext";

const Settings = () => {
  const { user, getClientUsername } = useAuth();
  const [formData, setFormData] = useState({ username: "" });
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchUser = async () => {
      const currentUser = await getClientUsername();
      if (currentUser) setFormData({ username: currentUser.username });
    };
    fetchUser();
  }, [user, getClientUsername]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:8000/api/user/", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData),
      });
      if (!res.ok) throw new Error("Update failed");
      setMessage("Profile updated successfully!");
      await getClientUsername(); // Refresh context
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    }
  };

  return (
    <Box sx={{ display: "flex", justifyContent: "center", mt: 5 }}>
      <Paper sx={{ p: 4, width: 400 }}>
        <Typography variant="h5" gutterBottom>
          Edit Profile
        </Typography>
        <Divider sx={{ mb: 2 }} />
        {message && <Typography sx={{ mb: 2 }}>{message}</Typography>}
        <Box component="form" onSubmit={handleUpdate}>
          <TextField
            fullWidth
            label="Username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            margin="normal"
          />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
            Update Profile
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Settings;
