// src/auth/ProtectedRoute.js
import { useEffect, useState } from "react";
import { Outlet, Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

function ProtectedRoute() {
  const [isAuth, setIsAuth] = useState(null);
  const { userRef } = useAuth();

  useEffect(() => {
    if (userRef.current) {
      setIsAuth(true);
      return;
    } else {
      setIsAuth(false);
    }
  }, []);

  if (isAuth === false) {return <Navigate to="/login" replace />;}

  return <Outlet />;
}

export default ProtectedRoute;
