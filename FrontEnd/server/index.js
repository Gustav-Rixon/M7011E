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
var whitelist = ['http://localhost:3000', "http://nominatim.openstreetmap.org", "'http://127.0.0.1:5000"];
var activeUsers = [];

app.use(cors({
    origin: whitelist,
    credentials: true

}));
var FormData = require('form-data');
const multer = require('multer');
const upload = multer();
app.use(cors());
app.use(cookieParser());
app.use(bodyParser.urlencoded({extended: true}));

var maxLifespan = 300000
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
                jwt.verify(token, "admin", (err, decoded) => {
                    if(err){
                        res.json({auth: false, message: "Authentication failed"})
                    }
                    else{
                        req.userId = decoded.id;
                        next();
                    }
                })
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
    if(name !== "" && email.includes("@",".") && zip !==0 && password !=="" && !name.includes("/", "=", "?", " ", "*", "<", ">", "|", ":", "/\\\//g")){   
   // console.log(Axios.get('http://nominatim.openstreetmap.org/search.php?street='+address+ '&postalcode='+zip+ '&format=json'))
         await Axios.get('http://nominatim.openstreetmap.org/search.php?street='+address+ '&postalcode='+zip+ '&format=json').then(resp => {
                exists = resp.data.length;
        }).catch(err => err);
                if(exists===1){
                    bcrypt.hash(password, saltRounds, (err, hash) =>{
                        if (err){
                            console.log(err)
                        }
                        var vhash = hash.replace(/\//g, "slash");
                        var shash = encodeURIComponent(vhash)
                        Axios.post('http://127.0.0.1:5000/register/username='+name+'&password='+shash+'&email='+email+'&address='+address+'&zipcode='+zip+'&prosumer='+prosumer).then(resp1 => {
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
                         activeUsers.push({createdAt: Date.now(), id: id+", "})
    
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
    Axios.get('http://127.0.0.1:5000/admin/login/username='+name).then(resp => {
        hash = resp.data.slice(15, resp.data.length-3)
        if(hash.length> 0){
            bcrypt.compare(password, hash, (error, answer) =>{
                     if(answer){
                         //TODO encrypt if time
                         const id = 1;
                         const token = jwt.sign({id}, "admin", {
                             expiresIn: 300000000000000000000000000,
                         })
    
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
app.post("/sell", (req, res)=>{   
    const token = req.body.token;
    const id = req.body.id;
    const sell = req.body.sell;
    Axios.post("http://127.0.0.1:5000/sell/house_hold/prosumer/house_hold_id="+id+"&amount="+sell+"&token="+token).then(resp => {
        res.json({message: resp.data})
    }).catch(err => err);
});
app.post("/ratio", (req, res)=>{ 
    const token = req.body.token;
    const tempratio = req.body.tempratio;
    const id = req.body.id;
    Axios.post("http://127.0.0.1:5000/change_buffert/house_hold="+id+'&amount='+tempratio+'&token='+token).then(resp => {
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
app.post("/picture", (req, res)=>{
    const token = req.body.token;
    const type = req.body.type;
    const id = req.body.id;
      Axios.get("http://127.0.0.1:5000/user/get_user_pic?id="+ id+"&token="+ token + "&type="+ type)
      .then(function (response) {
          res.send(response.data)
      })
      .catch(function (error) {
        console.log(error);
      });
      
});
app.post("/logout", (req, res)=>{
    const id = req.body.id
    for( var i = 0; i < activeUsers.length; i++){ 
        if ( activeUsers[i]["id"] === id+", ") { 
    
            activeUsers.splice(i, 1); 
        }
    }
});
app.get("/admindata", verifyJWT, (req, res)=>{
    const token = req.header("x-access-token");
    const id = req.header("user-id");
    Axios.get("http://127.0.0.1:5000/admin/view?token="+token+"&id="+ id).then(resp => {
        res.json({data: resp.data})
    }).catch(err => err);
});
app.get("/loggedin", verifyJWT, (req,res)=>{
     var temparray = []
     
     for (var i in activeUsers) {
         let n= 0;
        while (n <= temparray.length) {
            console.log("hello"+temparray[n])
            console.log(activeUsers[i]["id"])
            if(activeUsers[i]["id"] !== temparray[n] && activeUsers[i]["id"] !== temparray[n-1]){
                temparray.push(activeUsers[i]["id"])
            }
            n++;

          }
      }
      res.send(temparray)
})
app.post("/adminchange", (req,res) =>{
    var message = "Responce:"
    const {id,name,zip,address,password,email,prosumer,token,adminid} =req.body;
    if(name !== "" && !name.includes("/", "=", "?", " ", "*", "<", ">", "|", ":", "/\\\//g")){
        Axios.post("http://127.0.0.1:5000/admin/tool/change_user_info?token="+ token +"&id="+adminid+"&target_id="+id+"&target_row=user_name&user_name="+name).then(resp => {
            console.log(resp.data)
        }).catch(message += "couldnt change name, ");
    }
    if(address !== "" && zip !== 0){
        Axios.post("http://127.0.0.1:5000/admin/tool/change_user_info?token="+ token +"&id="+adminid+"&target_id="+id+"&target_row=address_zipcode&address="+address+"&zipcode"+ zip).then(resp => {
            console.log(resp.data)
        }).catch(message += "address/zip couldn't change, ");
    }
    if(password !== ""){
        bcrypt.hash(password, saltRounds, (err, hash) =>{
            if (err){
                console.log(err)
            }
            var vhash = hash.replace(/\//g, "slash");
            var shash = encodeURIComponent(vhash)
        Axios.post("http://127.0.0.1:5000/admin/tool/change_user_info?token="+ token +"&id="+adminid+"&target_id="+id+"&target_row=password&password="+shash).then(resp => {
            console.log(resp.data)
        }).catch(message += "password couldn't change, ");
    })}
    if(email !== ""&& email.includes("@",".")){
        Axios.post("http://127.0.0.1:5000/admin/tool/change_user_info?token="+ token +"&id="+adminid+"&target_id="+id+"&target_row=email&email="+ email).then(resp => {
            console.log(resp.data)
        }).catch(message += "email couldn't change, ");
    }
    else{
        message = "Nothing changed"
    }
    res.send(message)

})
app.listen(3001);