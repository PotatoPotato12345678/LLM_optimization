import { createContext, useContext, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";


const AuthContext = createContext();
export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const userRef = useRef(user);

  const getClientUsername= async () => {
    try {
      const res = await fetch("http://localhost:8000/api/user/", {
        credentials: "include",
      });
      if (res.ok) {
        const data = JSON.parse(await res.text());
        userRef.current = {
          username: data.username,
          is_manager: data.is_manager
        };
      } else {
        userRef.current = null;
      }
      setUser(userRef.current);
      
      return true;
    } catch (err) {
      console.error("Error fetching user info:", err);
      return false;
    }
  };

  const login = async ({ username, password }) => {
    try {
      const res = await fetch("http://localhost:8000/api/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "include",
      });

      if (!res.ok) {
        const data = await res.json();
        navigate("/login");
        throw new Error(data.error || "Login failed");
      }
      
      await getClientUsername();

      if (userRef.current.is_manager) {
        navigate("/dashboard/manager");
      } else {
        navigate("/dashboard/employee");
      } 
      return true;
    } catch (err) {
      throw new Error(err.message);
    }
  };

  const logout = async () => {
    userRef.current = null;
    setUser(userRef.current);
    try {
      await fetch("http://localhost:8000/api/logout/", {
        method: "POST",
        credentials: "include",
      }).then(async () => {
        navigate("/");
      });
      await getClientUsername();
    } catch (err) {
      throw new Error(err.message);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        userRef,
        getClientUsername,
        login,
        logout,
      }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
