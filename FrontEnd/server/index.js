const express = require('express');
const app = express();
const mysql = require('mysql');
const cors = require('cors');
const bcrypt = require("bcrypt");
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const session = require('express-session')
const { Axios } = require('../client/node_modules/axios');
const saltRounds = 10;
app.use(express.json());
app.use(cors());

//needs to be changed to connect to new database
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '6455593e.',
    database: 'M7011e',
});


app.get('/get', (req,res) => {
    const sqlSelect = "SELECT * FROM user";
    db.query(sqlSelect, (err, result) => {
        //console.log(result)

    });
});

//TODO fixa så att vägen finns innan det läggs in i table. kalla på rixons backend function om inget returnar så invalid input
app.post("/register", (req, res)=>{

    const name = req.body.name;
    const address = req.body.address;
    const zip = req.body.zip;
    const password = req.body.password;
    const email = req.body.email;
    const prosumer = req.body.prosumer
    console.log(prosumer)
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
            console.log("orimligt")
         } else {
            bcrypt.hash(password, saltRounds, (err, hash) =>{
                if (err){
                    console.log(err)
                }
        
                db.query("INSERT INTO user (user_name, password, email, address, zipcode, prosumer) VALUES (?,?,?,?,?,?)", 
                [name, hash, email, address, zip, prosumer], 
                (err, result)=> {
                    if(err) {
                        console.log(err);
                    }else{
                        res.send({message: "Values Inserted"});
                    }
                }
                );
                res.send({message: "Registration successfull"})
            });
         }
    });

});
app.post("/login", (req, res)=>{

    const name = req.body.loginName;
    const password = req.body.loginPassword;
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";
    db.query("SELECT user_name, password FROM user WHERE user_name = ?;",
    name, 
    (err, result)=> {
        if(err) {
            res.send({err: err});
        }
         if(result.length > 0){
             bcrypt.compare(password, result[0].password, (error, answer) =>{
                 if(answer){
                     res.send(result[0].user_name)
                 }else{
                    res.send({message: "Login information is invalid. Wrong Password or Username"}); 
                 }
             });
         } else {
             res.send({message: "Login information is invalid. User not registered."});
         }
    });

});
app.post("/admin", (req, res)=>{

    const name = req.body.loginName;
    const password = req.body.loginPassword;
    console.log(password)
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";
    db.query("SELECT admin, password FROM admin WHERE admin = ?;",
    name, 
    (err, result)=> {
        if(err) {
            res.send({err: err});
        }
        if(password === result[0].password){
                     res.send(result[0].admin)
        }else{
                    res.send({message: "Admin information is invalid. Wrong Password or Username"}); 
        }
             
    });

});
app.listen(3001);