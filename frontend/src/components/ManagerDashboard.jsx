import { useState, useEffect } from "react";
import { useAuth } from "./utils/AuthContext";
import { useNavigate } from "react-router-dom";
import ShiftCalendar from "./utils/ShiftCalendar";

const Manager = () => {
  const { userRef, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div>
      <h1>シフトカレンダー</h1>
      {userRef?.current ? (
        <>
          <section id="dashboard-content">
            <ShiftCalendar />
          </section>
        </>
      ) : (
        <>
          <p>Please log in to access the dashboard.</p>
          <button onClick={() => navigate("/login")}>Login</button>
        </>
      )}
    </div>
  );
};

export default Manager;
