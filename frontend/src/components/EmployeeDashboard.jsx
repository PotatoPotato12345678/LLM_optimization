import { useAuth } from "./utils/AuthContext";
import { useNavigate } from "react-router-dom";
import ShiftCalendar from "./utils/ShiftCalendar";

const Dashboard = () => {
  const { userRef } = useAuth();
  const navigate = useNavigate();

  return (
    <div>
      <h1>Welcome to the Dashboard</h1>
      {userRef?.current ? (
        <>
          <section id="dashboard-content">
            <h2>Shift Calendar</h2>
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

export default Dashboard;
