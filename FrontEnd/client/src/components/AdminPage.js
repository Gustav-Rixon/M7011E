import React, {useEffect, useState} from "react";
import Axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { JsonToTable } from "react-json-to-table";
import { Listbox } from '@headlessui/react'
Axios.defaults.withCredentials = false;
function clean(value){
  value = value.toLowerCase();
  value = value.replace(/å/g, 'a');
  value = value.replace(/ä/g, 'a');
  value = value.replace(/ö/g, 'o');
  value = value.replace(/\s/g, '+')
  return value;
}
//TODO fixa sälj update ratio + bild
const options = ["Mangoes", "Apples", "Oranges"];
function AdminPage() { 
        const [data, setData] = useState([]);
        const [active, setActive] = useState([]);
        const navigate = useNavigate();
        const[name, setName] = useState("");
        const[id, setId] = useState("");
        const[address, setAddress] = useState("");
        const[zip, setZip] = useState("");
        const[password, setPassword] = useState("");
        const[email, setEmail] = useState("");
        const[block, setBlock] = useState("");
        //const[loginStatus, setLoginStatus] = useState("");
        const[prosumer, setProsumer] = useState('0');
        const[ratio, setRatio] = useState("NaN");
        const[tempratio, setTempRatio] = useState("NaN");
        const[sell, setSell] = useState("0");
        const[wind, setWind] = useState("NaN");
        const[consumption, setConsumption] = useState("NaN");
        const[production, setProduction] = useState("NaN");
        const[buffer, setBuffer] = useState("NaN");
        const[bufferCap, setBufferCap] = useState("NaN");
        const[temp, setTemp] = useState("NaN");
        const[netProd, setNetProd] = useState("0")
        const[marketprice, setmarketprice] = useState("0")
        const[pictureURL, setPictureURL] = useState("");
        const token = localStorage.getItem('id_token');
        const [isOpen, setIsOpen] = useState(false);
        const [selectedOption, setSelectedOption] = useState(null);

        const toggling = () => setIsOpen(!isOpen);

        const onOptionClicked = value => () => {
          setSelectedOption(value);
          setIsOpen(false);
          console.log(selectedOption);
        };
                const blockUser = () => {
          Axios.post("http://localhost:3001/admin", {
          }).then((response)=> {
            if(response.data.message){
            }else{
              localStorage.setItem("admintoken", response.data.token)
              localStorage.setItem("adminid", 1)
              navigate('/AdminPage');
            }
          }).catch(err => err);
      };
      const removeUser = () => {
        Axios.post("http://localhost:3001/admin", {
        }).then((response)=> {
          if(response.data.message){
          }else{
            localStorage.setItem("admintoken", response.data.token)
            localStorage.setItem("adminid", 1)
            navigate('/AdminPage');
          }
        }).catch(err => err);
      };
        const changeUser = () => {
          Axios.post("http://localhost:3001/adminchange", {
                    id: id,
                    name: name,
                    address: address, 
                    zip: zip, 
                    password:password,
                    email:email,
                    prosumer:prosumer,
                    token: localStorage.getItem("admintoken"),
                    adminid: localStorage.getItem("adminid")
                  }).then((response)=> {
                    if(response.data.succ){
                      alert("Successfull Registration")
                      navigate('/sign-in');
                    }
                    if(response.data.message){
                      
                    }
                  }).catch(error => console.log(error));
              };
        const changePowerplantStatus = () => {
          Axios.post("http://localhost:3001/admin", {
          }).then((response)=> {
            if(response.data.message){
            }else{
              localStorage.setItem("admintoken", response.data.token)
              localStorage.setItem("adminid", 1)
              navigate('/AdminPage');
            }
          }).catch(err => err);
        };
        const changePowerplantProduction = () => {
          Axios.post("http://localhost:3001/admin", {
          }).then((response)=> {
            if(response.data.message){
            }else{
              localStorage.setItem("admintoken", response.data.token)
              localStorage.setItem("adminid", 1)
              navigate('/AdminPage');
            }
          }).catch(err => err);
        };
        const changeElectricityprice = () => {
          Axios.post("http://localhost:3001/admin", {
          }).then((response)=> {
            if(response.data.message){
            }else{
              localStorage.setItem("admintoken", response.data.token)
              localStorage.setItem("adminid", 1)
              navigate('/AdminPage');
            }
          }).catch(err => err);
        };
        const changeFactoryRatio = () => {
          Axios.post("http://localhost:3001/admin", {
          }).then((response)=> {
            if(response.data.message){
            }else{
              localStorage.setItem("admintoken", response.data.token)
              localStorage.setItem("adminid", 1)
              navigate('/AdminPage');
            }
          }).catch(err => err);
        };
        const getUsers = () => {
          Axios.get("http://localhost:3001/loggedin", {
            headers:{
              "x-access-token": localStorage.getItem("admintoken"),
            }
          }).then((response)=> {
            console.log(response.data)
            if(response.data){
              setActive(response.data)


              console.log(active)
            }else{
             // localStorage.setItem("admintoken", null),
            //  localStorage.setItem("adminid", null),
              navigate("/admin")
              alert("Session timed out! Please log in again if you wish to continue")
            }
          }).catch(err => err);
        };
        
      const getAdminData = () =>{
        Axios.get("http://localhost:3001/admindata", {
          headers:{
            "x-access-token": localStorage.getItem("admintoken"),
            "user-id": localStorage.getItem("adminid")
          }
        }).then((response)=> {
          if(response.data.auth !== false){
            setData(response.data.data)
              
          }
        }).catch(err => err);
    };
    const getMarketData = () =>{
      Axios.get("http://localhost:3001/marketdata", {
      }).then((response)=> {
        setmarketprice(response.data.data["Market Info"][0].market_price)
        }).catch(err => err);
  };
  //  const logout = () =>{
  //      localStorage.setItem("admintoken", null),
    //    localStorage.setItem("adminid", null),
      //  navigate("/admin")
 //   }

      useEffect(() => {
        //do at refresh
        getAdminData()
        getUsers()
        const interval = setInterval(() => {
          getUsers()
        }, 10000);

        return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
      }, [])
        return (
          
        <div className="AdminPage">
          <h1>Currently active ids: {active}</h1>
           <h1> Kolfall </h1>
        <h2>--------------------Change User-------------------------</h2>
        <label> Id</label>
        <input type="text" name="id" onChange={(event) => {
          setId(event.target.value);
        } } />
        <label> New Username </label>
        <input type="text" name="name" onChange={(event) => {
          setName(event.target.value);
        } } />
        <label> New  Address </label>
        <input type="text" name="address" onChange={(event) => {
          setAddress(clean(event.target.value));
        } } />
        <label> New Email </label>
        <input type="text" name="email" onChange={(event) => {
          setEmail(event.target.value);
        } } />
        <label> New Zip </label>
        <input type="text" name="zip" onChange={(event) => {
          setZip(clean(event.target.value));
        } } />
        <label> New Password </label>
        <input type="password" name="password" onChange={(event) => {
          setPassword(event.target.value);
        } } /> 
        <label>New Prosumer</label>
        <input type="checkbox" name="checkbox" onChange={(event) =>{
          setProsumer(event.target.checked ? '1' : '0')
        }
        } />
        <button onClick={changeUser}> Change</button>
        <h2>--------------------Block User-------------------------</h2>
        <label> Id</label>
        <input type="text" name="id" onChange={(event) => {
          setId(event.target.value);
        } } />
        <label> Block Time (s)</label>
        <input type="text" name="block" onChange={(event) => {
          setBlock(event.target.value);
        } } />
        <button onClick={blockUser}> Block</button>
        <JsonToTable json={data} />
      </div>
        );
}
export default AdminPage