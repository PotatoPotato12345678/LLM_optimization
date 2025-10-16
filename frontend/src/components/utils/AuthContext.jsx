import { createContext, useContext, useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const userRef = useRef(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // optional

  // Fetch user info from server and populate state
  const getClientUsername = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/user/", {
        credentials: "include",
      });

      if (res.ok) {
        const data = await res.json();
        userRef.current = {
          username: data.username,
          is_manager: data.is_manager,
        };
      } else {
        userRef.current = null;
      }

      setUser(userRef.current);
      setLoading(false);
      return userRef.current;
    } catch (err) {
      console.error("Error fetching user info:", err);
      userRef.current = null;
      setUser(null);
      setLoading(false);
      return null;
    }
  };

  useEffect(() => {
    // Fetch user on mount to persist login state
    getClientUsername();
  }, []);

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
    try {
      await fetch("http://localhost:8000/api/user/", {
        method: "DELETE",
        credentials: "include",
      });
      userRef.current = null;
      setUser(null);
      navigate("/");
    } catch (err) {
      console.error(err);
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
        loading, // optional
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
