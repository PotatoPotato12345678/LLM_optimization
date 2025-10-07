import react from "react";
import { useAuth } from "./utils/AuthContext";
import { useNavigate } from "react-router-dom";
import { Paper } from "@mui/material";

const Home = () => {
  const { userRef, login, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div>
      <h1>Welcome to the Home Page</h1>
      <p>This is the main landing page of the application.</p>

      {userRef?.current ? (
        <>
          <p>
            Logged in as: <strong>{userRef.current.username}</strong>
          </p>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <>
          <p>Please log in to access more features.</p>
          <button onClick={() => navigate("/login")}>Login</button>
        </>
      )}
    </div>
  );
};
export default Home;
