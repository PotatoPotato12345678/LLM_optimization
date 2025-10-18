import { useState } from "react";
import { useAuth } from "./utils/AuthContext";
import {
  Box,
  TextField,
  Button,
  Paper,
  Divider,
  Typography,
  useTheme,
} from "@mui/material";

const debugUsers = [
  { label: "Manager", username: "manager_1", password: "m_1" },
  { label: "Employee 1", username: "employee_1", password: "e_1" },
  { label: "Employee 2", username: "employee_2", password: "e_2" },
  { label: "Employee 3", username: "employee_3", password: "e_3" },
];

const Login = () => {
  const { login } = useAuth();
  const theme = useTheme();
  const [inputData, setInputData] = useState({
    username: "",
    password: "",
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await login(inputData);
    } catch (err) {
      console.log(err.message);
    }
  };

  const handleDebugLogin = async (username, password) => {
    try {
      await login({ username, password });
    } catch (err) {
      console.error("Debug login failed:", err.message);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
      }}
    >
      <Paper elevation={3} sx={{ padding: 3, width: theme.spacing(80) }}>
        <Typography variant="h4" mb={1}>Welcome to the Login Page</Typography>
        <Typography mb={2}>Please enter your credentials to log in.</Typography>

        {/* Debug cards */}
        <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
          {debugUsers.map((user) => (
            <Paper
              key={user.username}
              elevation={3}
              sx={{
                p: 2,
                flex: 1,
                textAlign: "center",
                cursor: "pointer",
                ":hover": { backgroundColor: "#f0f0f0" },
              }}
              onClick={() => handleDebugLogin(user.username, user.password)}
            >
              <Typography variant="p">{user.label}</Typography>
            </Paper>
          ))}
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Regular login form */}
        <Box component="form" onSubmit={handleLogin} noValidate>
          <TextField
            label="Username"
            fullWidth
            required
            margin="normal"
            value={inputData.username}
            onChange={(e) =>
              setInputData({ ...inputData, username: e.target.value })
            }
          />
          <TextField
            label="Password"
            type="password"
            fullWidth
            required
            margin="normal"
            value={inputData.password}
            onChange={(e) =>
              setInputData({ ...inputData, password: e.target.value })
            }
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 2 }}
          >
            Login
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Login;
