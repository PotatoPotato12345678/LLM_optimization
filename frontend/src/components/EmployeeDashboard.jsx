import { useState, useEffect } from "react";
import { useAuth } from "./utils/AuthContext";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const [shiftReq, setShiftReq] = useState("");
  const [editText, setEditText] = useState("");
  const { userRef, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:8000/api/employee", {
      method: "GET",
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) {
          console.error("Failed to fetch shift requirements");
        }
        return res.json();
      })
      .then((data) => {
        console.log(data);
        setShiftReq(data);
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent page reload
    console.log("Submitted shift requirement:", editText);
    fetch("http://localhost:8000/api/shift/employee", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: editText }),
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) {
          console.error("Failed to submit shift requirement");
        }
        return res.json();
      })
      .then((data) => {
        setShiftReq(editText);
        setEditText("");
      });
  };

  return (
    <div>
      <h1>Welcome to the Dashboard</h1>
      <p>This is the dashboard after login </p>
      {userRef?.current ? (
        <>
          <section id="user-info">
            <p>
              Logged in as: <strong>{userRef.current.username}</strong>
            </p>
            <button onClick={logout}>Logout</button>
          </section>
          <section id="dashboard-content">
            <h2>Dashboard Content</h2>
            <p>
              This section contains the client's shift requirement information.
            </p>
            {shiftReq ? (
              <pre>{JSON.stringify(shiftReq, null, 2)}</pre>
            ) : (
              <>
                <form onSubmit={handleSubmit}>
                  <p>Edit your shift requirement:</p>
                  <textarea
                    name="shiftRequirement"
                    id="shiftRequirement"
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    rows={5}
                    cols={50}
                  />
                  <br />
                  <button type="submit">Submit</button>
                </form>
              </>
            )}
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
