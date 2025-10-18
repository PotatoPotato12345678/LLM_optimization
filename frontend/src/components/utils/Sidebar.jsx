import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  IconButton,
  Divider,
  Typography,
} from "@mui/material";
import { useAuth } from "./AuthContext";

const Sidebar = () => {
  const [open, setOpen] = useState(false);
  const { user } = useAuth();
  const toggleDrawer = (state) => () => setOpen(state);
  const location = useLocation();

  // --- Different menu sets based on login state ---
  const GuestMenu = [
    { text: "Home", path: "/" },
    { text: "Login", path: "/login" },
    { text: "About", path: "/about" },
  ];

  const EmployeeMenu = [
    { text: "Home", path: "/" },
    { text: "Dashboard", path: "/dashboard/employee" },
    { text: "Shift Input", path: "/input/employee" },
    { text: "Settings", path: "/settings" },
    { text: "Logout", path: "/logout" },
  ];

  const ManagerMenu = [
    { text: "Home", path: "/" },
    { text: "Dashboard", path: "/dashboard/manager" },
    { text: "Shift Management", path: "/dashboard/shiftManager" },
    { text: "Shift Optimization", path: "/input/manager" },
    { text: "Logout", path: "/logout" },
  ];

  // Choose which menu to display
  let menuItems = GuestMenu;
  if (user) {
    menuItems = user.is_manager ? ManagerMenu : EmployeeMenu;
  }

  return (
    <>
      {!open && (
        <IconButton
          onClick={toggleDrawer(true)}
          sx={{
            position: "fixed",
            top: 16,
            left: 16,
            zIndex: 2000,
            backgroundColor: "white",
            boxShadow: 2,
            borderRadius: "8px",
            width: 48,
            height: 48,
            "&:hover": { backgroundColor: "#f0f0f0" },
          }}
        >
          <Typography variant="h5">☰</Typography>
        </IconButton>
      )}

      <Drawer anchor="left" open={open} onClose={toggleDrawer(false)}>
        <List sx={{ width: 240 }}>
          {menuItems.map((item) => {
            const isActive = item.path && location.pathname === item.path;
            return (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  component={item.path ? Link : "button"}
                  to={item.path || undefined}
                  onClick={() => {
                    if (item.action) item.action();
                    else setOpen(false);
                  }}
                  sx={{
                    backgroundColor: isActive ? "#e0e0e0" : "transparent",
                  }}
                >
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
        <Divider />
        {user && (
          <Typography
            variant="body2"
            sx={{ m: 2, color: "gray", textAlign: "center" }}
          >
            Logged in as: <strong>{user.username}</strong>
            <br />
            Role: {user.is_manager ? "Manager" : "Employee"}
          </Typography>
        )}
      </Drawer>
    </>
  );
};

export default Sidebar;
