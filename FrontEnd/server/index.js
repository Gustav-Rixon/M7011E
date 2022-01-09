const express = require('express');
const Axios =require( 'axios');
Axios.defaults.withCredentials = true;
const app = express();
const cors = require('cors');
const bcrypt = require("bcrypt");
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const saltRounds = 10;
const jwt = require("jsonwebtoken");
app.use(express.json());
var whitelist = ['http://localhost:3000', "http://nominatim.openstreetmap.org"];
var activeUsers = [];
app.use(cors({
    origin: whitelist,
    credentials: true

}));
app.use(cors());
app.use(cookieParser());
app.use(bodyParser.urlencoded({extended: true}));

var maxLifespan = 50000
setInterval(function checkItems(){
    activeUsers.forEach(function(item){
        if(Date.now() - maxLifespan > item.createdAt){
            activeUsers.shift() // remove first item
        }
    })
}, 10000)
const verifyJWT = (req,res,next) => {
    const token = req.header("x-access-token")

    if(!token) {
        res.send("UnAuthorised")
    } else{
        jwt.verify(token, "Test", (err, decoded) => {
            if(err){
                res.json({auth: false, message: "Authentication failed"})
            }
            else{
                req.userId = decoded.id;
                next();
            }
        })
    }
}

app.get('/Authenticated', verifyJWT, (req,res) => {
    res.send(1)
});

//TODO fixa så att vägen finns innan det läggs in i table. kalla på rixons backend function om inget returnar så invalid input
app.post("/register",  async (req, res)=>{
    const {name,zip,address,password,email,prosumer} =req.body; 
    var exists;
    if(name !== "" && email.includes("@",".") && zip !==0 && password !==""){   
   // console.log(Axios.get('http://nominatim.openstreetmap.org/search.php?street='+address+ '&postalcode='+zip+ '&format=json'))
    Axios.get('http://nominatim.openstreetmap.org/search.php?street='+address+ '&postalcode='+zip+ '&format=json').then(resp => {
                exists = resp.data.length;
                if(exists===1){
                bcrypt.hash(password, saltRounds, (err, hash) =>{
                    if (err){
                        console.log(err)
                    }
                    var shash = encodeURI(hash)
                    Axios.post('http://127.0.0.1:5000/register/username='+name+'&password='+shash+'&email='+email+'&address='+address+'&zipcode='+zip+'&prosumer='+prosumer).then(resp1 => {
                        console.log("responce"+resp1.data)
                        if (resp1.data === 1){
                            res.json({message: "Successfull registration", succ: "succ"})
                        }
                        else{
                            res.json({message: "Username already in use please use another one"})
                        }
                    }).catch(err => err);
                      

                }
    )}
                else{
                    res.json({message: "Faulty address/zipcode combination"})
    
                }
            }).catch(err => err);
        }     else{
            res.json({message:"Faulty inputs"}) 
          }
    
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";

});
app.post("/login", (req, res)=>{

    const name = req.body.loginName;
    const password = req.body.loginPassword;
    var id = null;
    var hash = null;
    Axios.get('http://127.0.0.1:5000/login/username='+name).then(resp => {
        id = resp.data.slice(89, resp.data.length-2)
        hash = resp.data.slice(15, 75)
        if(id.length > 0 || hash.length> 0){
            bcrypt.compare(password, hash, (error, answer) =>{
                     if(answer){
                         //TODO encrypt if time
                         const token = jwt.sign({id}, "Test", {
                             expiresIn: 300,
                         })
                         activeUsers.push({createdAt: Date.now(), id: id})
    
                         res.json({auth: true, token: token, id: id});
                     }else{
                        res.json({auth: false, message: "Wrong username password combination"}); 
                     }
                 });
             } else {
                 res.json({auth: false, message: "no user exists"});
             }
            })

});
app.post("/admin", (req, res)=>{

    const name = req.body.loginName;
    const password = req.body.loginPassword;
    var hash = null;
    console.log("here")
    Axios.get('http://127.0.0.1:5000/admin/login/username='+name).then(resp => {
        hash = resp.data.slice(15, resp.data.length-3)
        console.log(hash)
        if(hash.length> 0){
            bcrypt.compare(password, hash, (error, answer) =>{
                console.log(answer)
                     if(answer){
                         //TODO encrypt if time
                         const id = 1;
                         const token = jwt.sign({id}, "Test", {
                             expiresIn: 300,
                         })
                         console.log(token)
    
                         res.json({auth: true, token: token, admin: true});
                     }else{
                        res.json({auth: false, message: "Wrong username password combination"}); 
                     }
                 });
             } else {
                 res.json({auth: false, message: "no user exists"});
             }
            })

});
app.post("/picture", verifyJWT, (req, res)=>{
    const token = req.header("x-access-token");
    const id = req.header("user-id");
    const picture = req.body.picture;
    Axios.post("Write here").then(resp => {
        console.log(resp)
        res.json({data: resp.data})
    })
});
app.post("/sell", verifyJWT, (req, res)=>{   
    console.log("gottem")
    const token = req.header("x-access-token");
    const id = req.header("user-id");
    const sell = req.body.sell
    console.log(sell)
    Axios.post("http://127.0.0.1:5000/sell/house_hold/prosumer/house_hold_id="+id+"&amount="+sell+"&token="+ token).then(resp => {
        console.log(resp)
        res.json({data: resp.data})
    }).catch(err => err);
});
app.post("/ratio", verifyJWT, (req, res)=>{ 
    const ratio = req.body.ratio;
    const token = req.header("x-access-token");
    const id = req.header("user-id");
    Axios.post("http://127.0.0.1:5000/change_buffert/house_hold=" + id + '&amount='+ratio+'&token='+ token).then(resp => {
        res.json({data: resp.data})
    }).catch(err => err);
});
app.get("/mydata", verifyJWT, (req, res)=>{
    const token = req.header("x-access-token");
    const id = req.header("user-id");
    Axios.get("http://127.0.0.1:5000/data/house_hold=" + id + '&token='+ token).then(resp => {
        res.json({data: resp.data})
    }).catch(err => err);
});
app.get("/marketdata", (req, res)=>{
 
    Axios.get("http://127.0.0.1:5000/data/get_market_data").then(resp => {
        res.json({data: resp.data})
    }).catch(err => err);
});
app.get("/picture", verifyJWT, (req, res)=>{
    const token = req.header("x-access-token");
    const id = req.header("user-id");
    Axios.post("Write here").then(resp => {
        console.log(resp)
        res.json({data: resp.data})
    })
});
app.listen(3001);