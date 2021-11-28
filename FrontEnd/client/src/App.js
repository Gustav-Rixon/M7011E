
import { useState} from 'react';
import './App.css';
import Axios from 'axios';


function App() {

  const[name, setName] = useState("");
  const[adress, setAdress] = useState("");
  const[zip, setZip] = useState(0);
  const[password, setPassword] = useState("");
  const[email, setEmail] = useState("");

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
    <div className="App">
      <h1>Register</h1>
      <div className ="form">
        <label> Name </label>
      <input type="text" name = "name" onChange={(event)=>{
        setName(event.target.value)
      }}/>
      <label>  Adress </label>
      <input type="text" name = "adress"onChange={(event)=>{
        setEmail(event.target.value)
      }}/>
      <label> Email </label>
      <input type="text" name = "email" onChange={(event)=>{
        setAdress(event.target.value)
      }}/>
      <label> Zip </label>
      <input type="number" name = "zip" onChange={(event)=>{
        setZip(event.target.value)
      }}/>
      <label> Password </label>
      <input type="text" name = "password" onChange={(event)=>{
        setPassword(event.target.value)
      }}/>
      <label>Prosumer</label>
      <input type="checkbox" name = "checkbox" />
      <button onClick ={submitRegistration}> Submit</button>
      </div>
    </div>
  );
}

export default App;

