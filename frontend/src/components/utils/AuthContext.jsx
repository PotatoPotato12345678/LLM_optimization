import { createContext, useContext, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext();
export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const userRef = useRef(null);
  const [user, setUser] = useState(null);

  const getClientUsername = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/user/", {
        credentials: "include",
      });
      if (res.ok) {
        const data = JSON.parse(await res.text());
        userRef.current = {
          username: data.username,
          is_manager: data.is_manager,
        };
      } else {
        userRef.current = null;
      }
      setUser(userRef.current);

      return userRef.current;
    } catch (err) {
      console.error("Error fetching user info:", err);
      return null;
    }
  };

  const login = async ({ username, password }) => {
    try {
      const res = await fetch("http://localhost:8000/api/user/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "include",
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Login failed");
      }

      const loggedInUser = await getClientUsername();

      if (loggedInUser?.is_manager) {
        console.log("Navigating to manager dashboard");
        navigate("/dashboard/manager");
      } else {
        console.log("Navigating to employee dashboard");
        navigate("/dashboard/employee");
      }
      return true;
    } catch (err) {
      throw new Error(err.message);
    }
  };

  const logout = async () => {
    try {
      await fetch("http://localhost:8000/api/user/", {
        method: "DELETE",
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
        user,
        userRef,
        getClientUsername,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
