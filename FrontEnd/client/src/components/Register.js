import React, { useState } from "react";
import Axios from "axios";
import { useNavigate } from "react-router-dom";
Axios.defaults.withCredentials = false;
// a function to clean the input to address and zip so that it can be used in Nominatim API
function clean(value) {
  value = value.toLowerCase();
  value = value.replace(/å/g, "a");
  value = value.replace(/ä/g, "a");
  value = value.replace(/ö/g, "o");
  value = value.replace(/\s/g, "+");
  return value;
}
// Register component for Frontend
function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [zip, setZip] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [loginStatus, setLoginStatus] = useState("");
  const [prosumer, setProsumer] = useState("0");
  const submitRegistration = () => {
    //TODO fixa om tid finns Skriv if sats för alla steg
    Axios.post("http://localhost:3001/register", {
      name: name,
      address: address,
      zip: zip,
      password: password,
      email: email,
      prosumer: prosumer,
    })
      .then((response) => {
        if (response.data.succ) {
          alert("Successfull Registration");
          navigate("/login");
        }
        if (response.data.message) {
          setLoginStatus(response.data.message);
        }
      })
      .catch((error) => console.log(error));
  };
  return (
    <div className="Register">
      <h1> Kolfall </h1>
      <h2>Register</h2>
      <label> Username </label>
      <input
        type="text"
        name="name"
        onChange={(event) => {
          setName(event.target.value);
        }}
      />

      <label> Address </label>
      <input
        type="text"
        name="address"
        onChange={(event) => {
          setAddress(clean(event.target.value));
        }}
      />
      <label> Email </label>
      <input
        type="text"
        name="email"
        onChange={(event) => {
          setEmail(event.target.value);
        }}
      />
      <label> Zip </label>
      <input
        type="text"
        name="zip"
        onChange={(event) => {
          setZip(clean(event.target.value));
        }}
      />
      <label> Password </label>
      <input
        type="password"
        name="password"
        onChange={(event) => {
          setPassword(event.target.value);
        }}
      />
      <label>Prosumer</label>
      <input
        type="checkbox"
        name="checkbox"
        onChange={(event) => {
          setProsumer(event.target.checked ? "1" : "0");
        }}
      />
      <button onClick={submitRegistration}> Register</button>
      <h1>{loginStatus}</h1>
    </div>
  );
}
export default Register;
