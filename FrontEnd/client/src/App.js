
import './App.css';
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import React, { Component }  from 'react';
import Login from "./components/Login.js";
import Register from "./components/Register.js";
import Admin from "./components/Admin.js";
import LoginPage from './components/LoginPage.js';
import AdminPage from './components/AdminPage.js';

// Standard background for the client with the routing to all pages in the componentsfolder
function App() {


  return (
    <><div className="App">
      <Router>
      <nav className="navbar navbar-expand-lg navbar-light fixed-top">
        <div className="container">
              <li className="nav-item">
                <Link className="nav-link" to={"/login"}>Login</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to={"/register"}>Sign up</Link>
              </li>
        </div>
      </nav>

      <div className="auth-wrapper">
        <div className="auth-inner">
          <Routes>
            <Route exact path='/' element={<Login/>} />
            <Route path="/login" element={<Login/>} />
            <Route path="/register" element={<Register/>}/>
            <Route path="/admin" element={<Admin/>}/>
            <Route path="/adminpage" element={<AdminPage/>}/>
            <Route path="/loginpage" element={<LoginPage/>}/>
          </Routes>
        </div>
      </div>
      </Router>
    </div>
</>
  );
}

export default App;