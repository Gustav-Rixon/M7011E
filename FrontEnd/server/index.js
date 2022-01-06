const express = require('express');
const Axios =require( 'axios');
Axios.defaults.withCredentials = true;
const app = express();
const mysql = require('mysql');
const cors = require('cors');
const bcrypt = require("bcrypt");
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const session = require('express-session')
const saltRounds = 10;
const jwt = require("jsonwebtoken");


app.use(express.json());
var whitelist = ['http://localhost:3000', "http://nominatim.openstreetmap.org", 'http://localhost:3000'];

app.use(cors({
    origin: whitelist,
    credentials: true

}));
app.use(cors());
app.use(cookieParser());
app.use(bodyParser.urlencoded({extended: true}));


//needs to be changed to connect to new database
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '6455593e.',
    database: 'M7011e',
});
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
    res.send("Authenticated")
});

//TODO fixa så att vägen finns innan det läggs in i table. kalla på rixons backend function om inget returnar så invalid input
app.post("/register",  async (req, res)=>{
    const {name,zip,address,password,email,prosumer} =req.body;
    var exists;
   // console.log(Axios.get('http://nominatim.openstreetmap.org/search.php?street='+address+ '&postalcode='+zip+ '&format=json'))
    Axios.get('http://nominatim.openstreetmap.org/search.php?street='+address+ '&postalcode='+zip+ '&format=json').then(resp => {
                exists = resp.data.length;
                console.log(resp)
                console.log (exists)
                if(exists===1){
                bcrypt.hash(password, saltRounds, (err, hash) =>{
                    if (err){
                        console.log(err)
                    }
                    Axios.post('http://127.0.0.1:5000/register/username='+name+'&password='+hash+'&email='+email+'&address='+address+'&zipcode='+zip+'&prosumer='+prosumer).then(resp => {
                        res.json({message: "Successfull registration"})
                    }).catch(err => err);
                      

                }
    )}
                else{
                    res.json({message: "Faulty address/zipcode combination"})
    
                }
            }).catch(err => err);
    
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";

});
app.post("/login", async (req, res)=>{

    const name = req.body.loginName;
    const password = req.body.loginPassword;
    var id = null;
    var hash = null;
    console.log("here")
    Axios.get('http://127.0.0.1:5000/login/username='+name).then(resp => {
        id = resp.data.slice(89, resp.data.length-2)
        hash = resp.data.slice(15, 75)
        console.log(id)
        console.log(hash)
        if(id.length > 0 || hash.length> 0){
            bcrypt.compare(password, hash, (error, answer) =>{
                console.log(answer)
                     if(answer){
                         //TODO encrypt if time
                         const token = jwt.sign({id}, "Test", {
                             expiresIn: 300,
                         })
                         console.log(token)
    
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
    console.log(password)
    db.query("SELECT * FROM admin_table WHERE admin = ?;",
    name, 
    (err, result)=> {
        if(err) {
            res.send({err: err});
        }
         if(result.length > 0){
             bcrypt.compare(password, result[0].password, (error, answer) =>{
                 console.log(answer)
                 if(answer){
                    console.log(answer)
                    console.log(result[0].admin)
                     const id = result[0].admin
                     //TODO encrypt if time
                     const token = jwt.sign({id}, "Test", {
                         expiresIn: 300,
                     })
                     req.session.user = result

                     res.json({auth: true, token: token, result: result})
                 }else{
                    res.json({auth: false, message: "Wrong username password combination"}); 
                 }
             });
         } else {
             res.json({auth: false, message: "no user exists"});
         }
    });

});
app.listen(3001);