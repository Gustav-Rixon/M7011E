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
var whitelist = ['http://localhost:3000', "http://nominatim.openstreetmap.org"];

app.use(cors({
    origin: ['http://localhost:3000', "http://nominatim.openstreetmap.org"],
    credentials: true

}));
app.use(cors());
app.use(cookieParser());
app.use(bodyParser.urlencoded({extended: true}));
app.use (
    session({
        key: "userId",
        secret: "Test",
        resave: false,
        saveUninitialized: false,
        cookie:{
            expires: 60 *  1000
        },
    })

);

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
    await Axios.get('http://nominatim.openstreetmap.org/search.php?street='+address+ '&postalcode='+zip+ '&format=json').then(resp => {
                console.log(resp)
                exists = resp.data.length;
                console.log (exists)
            })
    
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";
    console.log("was here")

    db.query("SELECT user_id FROM user WHERE user_name = ?;",
    name, 
    (err, result)=> {
        console.log(result.length)
        if(err) {
            res.send({err: err});
            console.log("stuck")
        }
         if(result.length > 0){
            res.send({message: "Login information is invalid. User already registered."});
         } else {
            bcrypt.hash(password, saltRounds, (err, hash) =>{
                if (err){
                    console.log(err)
                }
                if(exists>0){
                    db.query("INSERT INTO user (user_name, password, email, address, zipcode, prosumer) VALUES (?,?,?,?,?,?)", 
                    [name, hash, email, address, zip, prosumer], 
                    (err, result)=> {
                        if(err) {
                            console.log(err);
                        }else{
                           console.log("hi") //res.json("USER REGISTERED");
                        }
                    }
                    );
                }
                else{
                    console.log("address faulty")

                }
                
            });
         }
    });

});
app.get("/login", (req, res)=> {
    if(req.session.user){
        res.send({loggedIn: true, user: req.session.user})
    } else{
        res.send({loggedIn: false, user: req.session.user})
    }
});
app.post("/login", async (req, res)=>{

    const name = req.body.loginName;
    const password = req.body.loginPassword;
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";
    db.query("SELECT user_name, password, user_id FROM user WHERE user_name = ?;",
    name, 
    (err, result)=> {
        if(err) {
            res.send({err: err});
        }
         if(result.length > 0){
             bcrypt.compare(password, result[0].password, (error, answer) =>{
                 if(answer){

                     const id = result[0].user_id
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
app.get("/admin", (req, res)=> {
    if(req.session.user){
        res.send({loggedIn: true, user: req.session.user})
    } else{
        res.send({loggedIn: false, user: req.session.user})
    }
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