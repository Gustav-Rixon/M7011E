import React, { useEffect, useState } from "react";
import Axios from "axios";
import { useNavigate } from "react-router-dom";
Axios.defaults.withCredentials = false;
//Login component for Frontend allows registered users to login
function Login() {
  const navigate = useNavigate();
  const [loginName, setLoginName] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginStatus, setLoginStatus] = useState("");
  const submitLogin = () => {
    Axios.post("http://localhost:3001/login", {
      loginName: loginName,
      loginPassword: loginPassword,
    })
      .then((response) => {
        if (response.data.message) {
          setLoginStatus(response.data.message);
        } else {
          localStorage.setItem("token", response.data.token);
          localStorage.setItem("id", response.data.id);
          navigate("/loginpage");
        }
      })
      .catch((err) => err);
  };
  return (
    <div className="Login">
      <h1> Kolfall </h1>
      <h1>Login</h1>
      <label> Name </label>
      <input
        type="text"
        name="loginName"
        onChange={(event) => {
          setLoginName(event.target.value);
        }}
      />
      <label> Password </label>
      <input
        type="password"
        name="loginPassword"
        onChange={(event) => {
          setLoginPassword(event.target.value);
        }}
      />
      <button onClick={submitLogin}> Login</button>
      <h1>{loginStatus}</h1>
    </div>
  );
}
export default Login;
