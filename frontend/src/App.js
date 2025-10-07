import './App.css';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import {Home, Login, Dashboard, Manager} from "./components";
import {AuthProvider} from "./components/utils";

const App = () => {
  return (
    <div className="App">
      <Router>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard/employee" element={<Dashboard />} />
            <Route path="/dashboard/manager" element={<Manager />} />
          </Routes>
        </AuthProvider>
      </Router>
    </div>
  );
}

export default App;
