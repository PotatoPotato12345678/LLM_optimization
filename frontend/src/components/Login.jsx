import { useState } from "react";
import { useAuth } from "./utils/AuthContext";
import {
  Box,
  TextField,
  Button,
  Paper,
  Divider,
  useTheme,
} from "@mui/material";

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

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
      }}
    >
      <Paper elevation={3} sx={{ padding: 3, width: theme.spacing(50) }}>
        <h1>Welcome to the Login Page</h1>
        <p>Please enter your credentials to log in.</p>
        <Paper
          elevation={3}
          style={{ display: "inline-block", width: "80%", padding: "10px" }}
        >
          <h3>Debug Employee</h3>
          <table style={{ display: "inline-block" }}>
            <tr>
              <td>username:</td>
              <td>
                <strong>employee_1</strong>
              </td>
            </tr>
            <tr>
              <td>password:</td>
              <td>
                <strong>e_1</strong>
              </td>
            </tr>
          </table>
        </Paper>
        <Box
          component="form"
          onSubmit={handleLogin}
          noValidate
          sx={{ mx: theme.spacing(8) }}
        >
          <Divider />
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
