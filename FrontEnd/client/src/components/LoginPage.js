import React, {useEffect, useState} from "react";
import { useNavigate } from 'react-router-dom';
import ReactSlider from 'react-slider'
import axios from "axios";
axios.defaults.withCredentials = false;

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
        const[picBase, setpicBase] = useState("");
        const[netProd, setNetProd] = useState("0")
        const[marketprice, setmarketprice] = useState("0")
        const[selectedFile, setSelectedFile] = useState();
        const[isSelected, setIsSelected] = useState(false);

	const changeHandler = (event) => {

		setSelectedFile(event.target.files[0]);

		setIsSelected(true);

	};

  //TODO skicka från index.js
	const handleSubmission = () => {
    var data = new FormData();
      data.append('file', selectedFile);
      data.append('userid', localStorage.getItem("id"));
      var config = {
        method: 'POST',
        url: 'http://127.0.0.1:5000/uploader?type=user',
        data : data
      };
    
    axios(config)
    .then(function (response) {
      console.log(JSON.stringify(response.data));
      alert("reload to see the picture")
    })
    .catch(function (error) {
      console.log(error);
    });
    alert("reload to see the picture")
	};
  //"../../../../Documents/GitHub/M7011E/Database/ProfilePictures/users/" 
  const getPicture = () =>{
    axios.post("http://localhost:3001/picture", {
      id: localStorage.getItem("id"),
      token: localStorage.getItem("token"),
      type: "user"
    }).then((response)=> {
      if(response.data) {
        setpicBase(response.data)
      }else{
      }

    }).catch(err => err);
  };

        const submitSale = () => {
            axios.post("http://localhost:3001/sell", {
              sell: sell,
              token: localStorage.getItem("token"),
              id: localStorage.getItem("id")
            }).then((response)=> {
              alert(response.data.message)
              getData()
            }).catch(err => err);
        };
        const submitRatio = () => {
          axios.post("http://localhost:3001/ratio", {
            tempratio: tempratio,
            token: localStorage.getItem("token"),
            id: localStorage.getItem("id")
          }).then((response)=> {
            if(response){
              getData()
            }
          }).catch(err => err);
      };
      const getData = () =>{
        axios.get("http://localhost:3001/mydata", {
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
            setNetProd(response.data.data[id][0].net_production)
          }else{
            localStorage.setItem("token", null)
            localStorage.setItem("id", null)
            navigate("/sign-in")
            alert("You have timed out please log in again")
          }
        }).catch(err => err);
    };
    const getMarketData = () =>{
      axios.get("http://localhost:3001/marketdata", {
      }).then((response)=> {
        setmarketprice(response.data.data["market_price"])
        }).catch(err => err);
  };
    const logout = () =>{
      axios.post("http://localhost:3001/logout", {
        id: localStorage.getItem("id")
      }).then(
        localStorage.setItem("token", null),
        localStorage.setItem("id", null),
        navigate("/sign-in")
        ).catch(err => err);
    };
  

      useEffect(() => {
        getPicture()
        getData()
        getMarketData()
        const interval = setInterval(() => {
          getData()
          getMarketData()
        }, 10000);

        return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
      }, [])
        return (
        <div className="LoginPage">
          <button onClick={logout}> logout</button>
          <h1>Welcome to Kolfall</h1>
          <img src={`data:image/jpeg;base64,${picBase}`} />
          <h1>----------------------Your personal data---------------------</h1>
          <h1>Wind:{wind}  m/s</h1>
          <h1>Temperature:{temp} °C</h1>
          <h1>Cosumption:{consumption}   kWh</h1>
          <h1>Production:{production}   kWh</h1>
          <h1>Net Production:{netProd}   kWh</h1>
          <h1>Buffer:{buffer}/{bufferCap}  kWh</h1>
          <h1>Current market price:{marketprice}/kWh</h1>
            <h1> ---------------------------Prosumer Actions ---------------------------</h1>
            <label> Sell from your buffer</label>
              <input type="text" name="sell"  onChange={(event) => {
                setSell(event.target.value);
              } } />
                <button onClick={submitSale}> Sell</button>
                <h1>Ratio:{ratio*100}%</h1>
        <button onClick={submitRatio}> Confirm new ratio</button>
        <ReactSlider
    className="horizontal-slider"
    thumbClassName="example-thumb"
    trackClassName="example-track"
    onAfterChange={(value, index) => setTempRatio(value)}
    renderThumb={(props, state) => <div {...props}>{state.valueNow}</div>}
/>
           <h1> ---------------------------Upload Profile Picture---------------------------</h1>    
                <input type="file" name="file" onChange={changeHandler} />

{isSelected ? (

  <div>

    <p>Filename: {selectedFile.name}</p>

    <p>Filetype: {selectedFile.type}</p>

    <p>Size in bytes: {selectedFile.size}</p>

  </div>

) : (

  <p>Select a file to show details</p>

)}

<div>

  <button onClick={handleSubmission}>Submit</button>

</div>
      </div>
        );
}
export default LoginPage