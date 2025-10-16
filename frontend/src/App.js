import './App.css';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import {Home, Login, Logout, Dashboard, Manager, ShiftManager, ShiftSetting, Settings, EmployeeInput} from "./components";
import {AuthProvider, Sidebar} from "./components/utils";

const App = () => {
  return (
    <div className="App">
      <Router>
        <AuthProvider>
          <Sidebar/>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="/dashboard/employee" element={<Dashboard />} />
            <Route path="/availabilityCalendar/employee" element={<EmployeeInput />} />
            <Route path="/dashboard/manager" element={<Manager />} />
            <Route path="/dashboard/shiftManager" element={<ShiftManager />} />
            <Route path="/shiftSetting" element={<ShiftSetting />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </AuthProvider>
      </Router>
    </div>
  );
}

export default App;
