
import './App.css';
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";

import Login from "./components/Login.js";
import Register from "./components/Register.js";
import Admin from "./components/Admin.js";


function App() {


  return (
    <><div className="App">
      <Router>
      <nav className="navbar navbar-expand-lg navbar-light fixed-top">
        <div className="container">
              <li className="nav-item">
                <Link className="nav-link" to={"/sign-in"}>Login</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to={"/sign-up"}>Sign up</Link>
              </li>
        </div>
      </nav>

      <div className="auth-wrapper">
        <div className="auth-inner">
          <Routes>
            <Route exact path='/' element={<Login/>} />
            <Route path="/sign-in" element={<Login/>} />
            <Route path="/sign-up" element={<Register/>}/>
            <Route path="/admin" element={<Admin/>}
             />
          </Routes>
        </div>
      </div>
      </Router>
    </div>
</>
  );
}

export default App;