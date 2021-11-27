import { useState, useEffect} from 'react';
import './App.css';
import Axios from 'axios';


function App() {

  const[name, setName] = useState('')
  const[adress, setAdress] = useState('')
  const[zip, setZip] = useState('')
  const[password, setPassword] = useState('')
  const[email, setEmail] = useState('')

  const submitRegistration = () => {
    Axios.post('http://localhost:3008/')
  }
  return (
    <div className="App">
      <h1>Register</h1>
      <div className ="form">
        <label> Name </label>
      <input type="text" name = "name" onChange={(e)=>{
        setName(e.target.value)
      }}/>
      <label> Email </label>
      <input type="text" name = "adress"onChange={(e)=>{
        setEmail(e.target.value)
      }}/>
      <label> Adress </label>
      <input type="text" name = "email"onChange={(e)=>{
        setAdress(e.target.value)
      }}/>
      <label> Zip </label>
      <input type="text" name = "zip"onChange={(e)=>{
        setZip(e.target.value)
      }}/>
      <label> Password </label>
      <input type="text" name = "password"onChange={(e)=>{
        setPassword(e.target.value)
      }}/>
      <label>Prosumer</label>
      <input type="checkbox" name = "checkbox" />
      <button>onClick={submitRegistration} Submit</button>
      </div>
    </div>
  );
}

export default App;

