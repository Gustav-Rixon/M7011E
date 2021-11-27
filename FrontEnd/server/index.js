const express = require('express');
const app = express();
const mysql = require('mysql');

//needs to be changed to connect to new database
const db = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: '6455593e.',
    database: 'plsWork'
});

app.post('/api/insert', (req, res)=>{

    const sqlInsert = "INSERT INTO user (name, adress, zip, password) VALUES (?,?,?,?)"
    db.query(sqlInsert, [name, adress, zip, password], (err, result)=> {
        
    });

});
app.get('/', (req, res) =>{
    const sqlInsert = "INSERT INTO user (name, adress, zip, password) VALUES ('inception', 'hej', 'test', 'test2');"
    db.query(sqlInsert, (err, result)=>{
        res.send('hello world')  
    })
});
app.listen(3008, () => {
    console.log("running on port 3008");
});