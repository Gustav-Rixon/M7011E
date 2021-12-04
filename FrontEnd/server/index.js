const express = require('express');
const app = express();
const mysql = require('mysql');
const cors = require('cors');
const bcrypt = require("bcrypt");
const saltRounds = 10;

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

//TODO fixa så att vägen finns innan det läggs in i table. kalla på rixons backend function om inget returnar så invalid input
app.post("/register", (req, res)=>{

    const name = req.body.name;
    const adress = req.body.adress;
    const zip = req.body.zip;
    const password = req.body.password;
    const email = req.body.email;
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";
    bcrypt.hash(password, saltRounds, (err, hash) =>{
        if (err){
            console.log(err)
        }

        db.query("INSERT INTO user (name, adress, email, zip, password) VALUES (?,?,?,?,?)", 
        [name, adress, email, zip, hash], 
        (err, result)=> {
            if(err) {
                console.log(err);
            }else{
                res.send("Values Inserted");
            }
        }
        );
    });

});
app.post("/login", (req, res)=>{

    const name = req.body.loginName;
    const password = req.body.loginPassword;
    //TODO fixa querry för ny databas
    //const sqlInsert = "INSERT INTO user (name, email, adress, zip, password) VALUES (?,?,?,?,?)";

    db.query("SELECT * FROM user WHERE name = ?;",
    name, 
    (err, result)=> {
        if(err) {
            res.send({err: err});
        }
         if(result.length > 0){
             bcrypt.compare(password, result[0].password, (error, answer) =>{
                 if(answer){
                     res.send(result)
                 }else{
                    res.send({message: "Login information is invalid. Password does not match the name."}); 
                 }
             });
         } else {
             res.send({message: "Login information is invalid. User not registered."});
         }
    });

});
app.listen(3001);