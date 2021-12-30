import React, {useState} from "react";
import Axios from 'axios';

function Admin() {
        const[loginName, setLoginName] = useState("");
        const[loginPassword, setLoginPassword] = useState("");
        const[loginStatus, setLoginStatus] = useState("");
        const submitLogin = () => {
            Axios.post("http://localhost:3001/admin", {
              loginName: loginName,
              loginPassword: loginPassword
            }).then((response)=> {
              if(response.data.message){
                setLoginStatus(response.data.message)
              }else{
                setLoginStatus(response.data)
              }
            }).catch(err => err);;
        }
        return (
                <div className="Login">
                    <h1> Kolfall </h1>
        <h1>Login</h1>
        <label> Admin</label>
        <input type="text" name="loginName" onChange={(event) => {
          setLoginName(event.target.value);
        } } /><label> Password </label>
        <input type="password" name="loginPassword" onChange={(event) => {
          setLoginPassword(event.target.value);
        } } />
        <button onClick={submitLogin}>Login</button>
        <h1>{loginStatus}</h1>
      </div>
        );
}
export default Admin