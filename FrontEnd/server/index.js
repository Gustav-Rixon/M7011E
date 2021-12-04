const express = require('express');
const app = express();
const mysql = require('mysql');
const cors = require('cors');

app.use(cors());
app.use(express.json());
//needs to be changed to connect to new database
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '6455593e.',
    database: 'plsWork',
});


app.get('/get', (req,res) => {
    const sqlSelect = "SELECT * FROM user";
    db.query(sqlSelect, (err, result) => {
        //console.log(result)

    });
});
app.post("/register", (req, res)=>{

    const name = req.body.name;
    const adress = req.body.adress;
    const zip = req.body.zip;
    const password = req.body.password;
    const email = req.body.email;
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";
    db.query("INSERT INTO user (name, adress, email, zip, password) VALUES (?,?,?,?,?)", 
    [name, adress, email, zip, password], 
    (err, result)=> {
        if(err) {
            console.log(err);
        }else{
            res.send("Values Inserted");
        }
    }
    );

});
app.post("/login", (req, res)=>{

    const name = req.body.loginName;
    const password = req.body.loginPassword;
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";
    db.query("SELECT * FROM user WHERE name = ? AND password = ?", 
    [name,password], 
    (err, result)=> {
        if(err) {
            res.send({err: err});
        }else{
         if(result.length > 0){
             res.send(result);
         } else {
             res.send({message: "Login information is invalid. Please check both username and password."});
         }
        }
    }
    );

});
app.listen(3001);