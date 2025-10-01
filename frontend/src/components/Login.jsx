import {useState} from 'react';
import { useAuth} from "./utils/AuthContext";
import {
  Box,
  TextField,
  Button,
  Paper,
  Divider,
  ListItem,
} from "@mui/material";


const Login = () => {
    const { login } = useAuth();
    const inputData = useState({
        username: "",
        password: ""
    });

    const handleLogin = () => {
        login(inputData);
    };

    return (
        
        <div>
            <h1>Welcome to the Login Page</h1>
            <p>Please enter your credentials to log in.</p>
            <Paper elevation={3} sx={{ padding: 3, width: theme.spacing(50) }}>
            <Box
              component="form"
              onSubmit={handleSubmit}
              noValidate
              sx={{ mx: cw }}>
              <ListItem>
                <LoginWith icon={<GoogleIcon />} func={handleGoogleLogin} />
                <LoginWith icon={<XIcon />} func={handleXLogin} />
              </ListItem>
              <Divider />
              <TextField
                label="Username"
                fullWidth
                required
                margin="normal"
                value={inputInfo.username}
                onChange={(e) =>
                  setInputInfo({ ...inputInfo, username: e.target.value })
                }
              />
              <TextField
                label="Password"
                type="password"
                fullWidth
                required
                margin="normal"
                value={inputInfo.password}
                onChange={(e) =>
                  setInputInfo({ ...inputInfo, password: e.target.value })
                }
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                sx={{ mt: 2 }}>
                Login
              </Button>
            </Box>
          </Paper>
        </div>

    );
}
export default Login;