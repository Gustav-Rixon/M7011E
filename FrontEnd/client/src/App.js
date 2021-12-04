
import { useEffect, useState} from 'react';
import './App.css';
import Axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";

import Login from "./components/Login.js";
import Register from "./components/Register.js";


function App() {

  const[name, setName] = useState("");
  const[adress, setAdress] = useState("");
  const[zip, setZip] = useState(0);
  const[password, setPassword] = useState("");
  const[email, setEmail] = useState("");
  //const[loginName, setLoginName] = useState("");
  //const[loginPassword, setLoginPassword] = useState("");
  //const[loginStatus, setLoginStatus] = useState("");

  const submitRegistration = () => {
    Axios.post("http://localhost:3001/register", {
      name: name,
      adress: adress, 
      zip: zip, 
      password:password,
      email:email
    }).then(()=> {
      alert("Added successfully to Kolfall")
    });
  };
  //Behöver lägga till/ta bost grejer för nya databasen
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
            <Route path="/sign-up" element={<Register/>} />
          </Routes>
        </div>
      </div>
      </Router>
    </div>
</>
  );
}

export default App;