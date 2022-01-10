import React, {useEffect, useState} from "react";
import Axios from 'axios';
import { useNavigate } from 'react-router-dom';
import ReactSlider from 'react-slider'
Axios.defaults.withCredentials = false;
//TODO fixa sälj update ratio + bild
function LoginPage() { 

        const navigate = useNavigate();
        const id = localStorage.getItem("id");
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

        const submitSale = () => {
            console.log("got here")
            Axios.post("http://localhost:3001/sell", {
              sell: sell,
              headers:{
                "x-access-token": localStorage.getItem("token"),
                "user-id": localStorage.getItem("id")
              }
            }).then((response)=> {
              if(response.data.message){
              console.log(response.data.message + sell)
              }else{
                console.log(response.data.alert)
              }
            }).catch(err => err);
        };
        const submitRatio = () => {
          console.log(ratio)
          Axios.post("http://localhost:3001/ratio", {
            id: id,
            token: token,
            ratio: ratio,
            headers:{
              "x-access-token": localStorage.getItem("token"),
              "user-id": localStorage.getItem("id")
            }
          }).then((response)=> {
            if(response.data.message){
              //setLoginStatus(response.data.message)
            }else{
            
            }
          }).catch(err => err);
      };
        const submitPicture = () =>{
          Axios.post("http://localhost:3001/picture", {
            pictureURL: pictureURL,
            headers:{
              "x-access-token": localStorage.getItem("token"),
              "user-id": localStorage.getItem("id")
            }
          }).then((response)=> {
            if(response.data.message){
              //setLoginStatus(response.data.message)
            }else{
              console.log("have to put stuff here")
            }
          }).catch(err => err);
      };
      const getData = () =>{
        Axios.get("http://localhost:3001/mydata", {
          headers:{
            "x-access-token": localStorage.getItem("token"),
            "user-id": localStorage.getItem("id")
          }
        }).then((response)=> {
          if(response.data.auth !== false){
            setRatio(response.data.data[id][0].buffert_ratio)
            setTemp(response.data.data[id][0].temp)
            setProduction(response.data.data[id][0].production)
            setWind(response.data.data[id][0].wind)
            setBuffer(response.data.data[id][0].buffert_content)
            setBufferCap(response.data.data[id][0].buffert_capacity)
            setConsumption(response.data.data[id][0].consumption)
            const temp = parseFloat(production)
            const temp2 = parseFloat(consumption)
            setNetProd(temp - temp2)
          }else{
            navigate("/sign-in")
            alert("You have timed out please log in again")
          }
        }).catch(err => err);
    };
    const getMarketData = () =>{
      Axios.get("http://localhost:3001/marketdata", {
      }).then((response)=> {
        setmarketprice(response.data.data["Market Info"][0].market_price)
        }).catch(err => err);
  };

      useEffect(() => {
        getData()
        getMarketData()
        const interval = setInterval(() => {
          getData()
        }, 10000);

        return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
      }, [])
        return (
                <div className="LoginPage">
        <h1>Welcome to Kolfall</h1>
        <h1>Your personal data:</h1>
        <h1>Wind:{wind}  m/s</h1>
        <h1>Temperature:{temp} C</h1>
        <h1>Cosumption:{consumption}   kW/h</h1>
        <h1>Production:{production}   kW/h</h1>
        <h1>Net Production:{netProd}   kW/h</h1>
        <h1>Buffer:{buffer}/{bufferCap}  kW/h</h1>
        <h1>Current market price:{marketprice}kr per kW/h</h1>
        <label> Sell </label>
        <input type="text" name="sell"  onChange={(event) => {
          setSell(event.target.value);
        } } />
        <button onClick={submitSale}> Sell</button>
        <label> Picture URL </label>
        <input type="text" name="pictureUrl"  onChange={(event) => {
          setPictureURL(event.target.value);
        } } />
        <button onClick={submitPicture}> Submit picture</button>  
        <h1>Ratio:{ratio}</h1>
        <button onClick={submitRatio}> Confirm new ratio</button>
        <ReactSlider
    className="horizontal-slider"
    thumbClassName="example-thumb"
    trackClassName="example-track"
    onAfterChange={(value, index) => setTempRatio(value/100)}
    renderThumb={(props, state) => <div {...props}>{state.valueNow}</div>}
/>
      </div>
        );
}
export default LoginPage