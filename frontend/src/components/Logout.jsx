import { useEffect } from "react";
import { useAuth } from "./utils/AuthContext";
import { useNavigate } from "react-router-dom";

const Logout = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const handleLogout = async () => {
      try {
        await logout();
        navigate("/login"); // redirect after logout
      } catch (err) {
        console.error(err);
      }
    };
    handleLogout();
  }, [logout, navigate]);

  return <p>Logging out...</p>;
};

export default Logout;
