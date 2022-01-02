import React, {useEffect, useState} from "react";
import Axios from 'axios';
Axios.defaults.withCredentials = true;
function Login() {
        const[loginName, setLoginName] = useState("");
        const[loginPassword, setLoginPassword] = useState("");
        const[loginStatus, setLoginStatus] = useState(false);
        const submitLogin = () => {
            Axios.post("http://localhost:3001/login", {
              loginName: loginName,
              loginPassword: loginPassword
            }).then((response)=> {
              if(response.data.message){
                setLoginStatus(false)
              }else{
                localStorage.setItem("token", response.data.token)
                setLoginStatus(true)
              }
            }).catch(err => err);
        };
        useEffect(()=>{
          Axios.get("http://localhost:3001/login").then((response)=>{
            if(response.data.loggedIn === true){
              setLoginStatus(true);
        }
          }).catch(err => err);
        }, []);

        const authenticated = () =>{
          Axios.get("http://localhost:3001/Authenticated", {
            headers:{
              "x-access-token": localStorage.getItem("token")
          }}).then((response)=>{
            console.log(response);
          }).catch(err => err);
        }
        return (
                <div className="Login">
                    <h1> Kolfall </h1>
        <h1>Login</h1>
        <label> Name </label>
        <input type="text" name="loginName" onChange={(event) => {
          setLoginName(event.target.value);
        } } /><label> Password </label>
        <input type="password" name="loginPassword" onChange={(event) => {
          setLoginPassword(event.target.value);
        } } />
        <button onClick={submitLogin}> Login</button>
        {loginStatus &&(
          <button onClick={authenticated}>check if auth</button>
        )}
      </div>
        );
}
export default Login