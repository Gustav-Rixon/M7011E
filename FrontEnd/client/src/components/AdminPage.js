import React, {useEffect, useState} from "react";
import Axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { JsonToTable } from "react-json-to-table";
import ReactSlider from 'react-slider'
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
function AdminPage() { 
        const [data, setData] = useState([]);
        const [marketData, setMarketData] = useState([]);
        const [active, setActive] = useState([]);
        const navigate = useNavigate();
        const[name, setName] = useState("");
        const[id, setId] = useState("");
        const[proId, setProId] = useState("");
        const[blockId, setBlockId] = useState("");
        const[delId, setDelId] = useState("");
        const[address, setAddress] = useState("");
        const[zip, setZip] = useState("");
        const[password, setPassword] = useState("");
        const[email, setEmail] = useState("");
        const[block, setBlock] = useState("");
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
        const[price, setprice] = useState("")
        const[picBase, setpicBase] = useState("");;
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
      data.append('userid', localStorage.getItem("adminid"));
      var config = {
        method: 'POST',
        url: 'http://127.0.0.1:5000/uploader?type=admin',
        data : data
      };
    
    Axios(config)
    .then(function (response) {
      console.log(JSON.stringify(response.data));
      alert("reload to see the picture")
    })
    .catch(function (error) {
      console.log(error);
    });
    alert("reload to see the picture")
	};



        const blockUser = () => {
          Axios.post("http://localhost:3001/adminblock", {
            token: localStorage.getItem("admintoken"),
            adminid: localStorage.getItem("adminid"),
            id: blockId,
            block: block

          }).then((response)=> {
            alert(response.data.data)
          }).catch(err => err);
      };
      const deleteUser = () => {
          Axios.post("http://localhost:3001/admindelete", {
            token: localStorage.getItem("admintoken"),
            adminid: localStorage.getItem("adminid"),
            id: delId,

          }).then((response)=> {
            alert(response.data)
            window.location.reload(false);
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
                    token: localStorage.getItem("admintoken"),
                    adminid: localStorage.getItem("adminid")
                  }).then((response)=> {
                    if(response.data){
                      alert(response.data)
                    }
                  }).catch(error => console.log(error));
              };
        const changeProd = () => {
          Axios.post("http://localhost:3001/adminprodchange", {
            id: proId,
            prosumer: prosumer,
            token: localStorage.getItem("admintoken"),
            adminid: localStorage.getItem("adminid")
        }).then((response)=> {
          if(response.data.message){
            alert(response.data.message)
          }
        }).catch(error => console.log(error));
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
        const submitElectricityPrice = () => {
          Axios.post("http://localhost:3001/marketprice", {
            price: price,
            token: localStorage.getItem("admintoken"),
            adminid: localStorage.getItem("adminid")
          }).then((response)=> {
          console.log(response.data)
          }).catch(error => console.log(error));
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
        console.log(response.data.data)
        setMarketData(response.data.data)
        }).catch(err => err);
  };
  const getPicture = () =>{
    Axios.post("http://localhost:3001/picture", {
      id: localStorage.getItem("adminid"),
      token: localStorage.getItem("admintoken"),
      type: "admin"
    }).then((response)=> {
      if(response.data) {
        setpicBase(response.data)
      }else{
      }

    }).catch(err => err);
  };

      useEffect(() => {
        //do at refresh
        //getPicture()
        getAdminData()
        getUsers()
        getMarketData()
        const interval = setInterval(() => {
          getMarketData()
          getUsers()
        }, 10000);

        return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
      }, [])
        return (
          
        <div className="AdminPage">
          <img src={`data:image/jpeg;base64,${picBase}`} />
          <h1> Kolfall </h1>
          <h1>Currently active ids: {active}</h1>
        <h2>--------------------Change User--------------------</h2>
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
        
         <button onClick={changeUser}> Change</button>
        <h2>Change prosumer status</h2>
        <label> Id:</label>
        <input type="text" name="proid" onChange={(event) => {
          setProId(event.target.value);
        } } />
        <input type="checkbox" name="checkbox" onChange={(event) =>{
          setProsumer(event.target.checked ? '1' : '0')
        }
        } />
        <button onClick={changeProd}> Change </button>
        <h2>-------------------------Block Prosumer-------------------------</h2>
        <label> Id:</label>
        <input type="text" name="id" onChange={(event) => {
          setBlockId(event.target.value);
        } } />
        <label> Block Time (s):</label>
        <input type="text" name="block" onChange={(event) => {
          setBlock(event.target.value);
        } } />
        <button onClick={blockUser}> Block</button>
        <h2>-------------------------Delete User-------------------------</h2>
        <label> Id:</label>
        <input type="text" name="id" onChange={(event) => {
          setDelId(event.target.value);
        } } />
        <button onClick={deleteUser}> Delete</button>
        <JsonToTable json={data} />
        <h2>-------------------------Upload Admin Picture-------------------------</h2>
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
        <h2>-------------------------Market-------------------------</h2>
        <label> Set Market Price:</label>
        <input type="text" name="price" onChange={(event) => {
          setprice(event.target.value);
        } } />
        <button onClick={submitElectricityPrice}> Confirm</button>
          <JsonToTable json={marketData} />
        <h2>-------------------------Power Plant-------------------------</h2>

        <ReactSlider
    className="horizontal-slider"
    thumbClassName="example-thumb"
    trackClassName="example-track"
    onAfterChange={(value, index) => setTempRatio(value)}
    renderThumb={(props, state) => <div {...props}>{state.valueNow}</div>}
/> 
      </div>
        );
}
export default AdminPage