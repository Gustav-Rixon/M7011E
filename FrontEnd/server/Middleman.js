const express = require("express");
const Axios = require("axios");
Axios.defaults.withCredentials = true;
const app = express();
const cors = require("cors");
const fs = require("fs");
let rawdata = fs.readFileSync("../../conf/configuration.json");
let keys = JSON.parse(rawdata);
const bcrypt = require("bcrypt");
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");
const saltRounds = 10;
const jwt = require("jsonwebtoken");
app.use(express.json());
var whitelist = [
  "http://localhost:3000",
  "http://nominatim.openstreetmap.org",
  "'http://127.0.0.1:5000",
];
var activeUsers = [];
app.use(
  cors({
    origin: whitelist,
    credentials: true,
  })
);
const { response } = require("express");
app.use(cors());
app.use(cookieParser());
app.use(bodyParser.urlencoded({ extended: true }));
// refreshes every ten seconds and removes the users whos log in session has timed out.
var maxLifespan = 300000;
setInterval(function checkItems() {
  activeUsers.forEach(function (item) {
    if (Date.now() - maxLifespan > item.createdAt) {
      activeUsers.shift(); // remove first item
    }
  });
}, 10000);
//verifies if the JWT is still active or if there is one(used to keep check on who is online).
const verifyJWT = (req, res, next) => {
  const token = req.header("x-access-token");
  if (!token) {
    res.send("UnAuthorised");
  } else {
    jwt.verify(token, keys["JWT_KEYS"]["user_key"], (err, decoded) => {
      if (err) {
        jwt.verify(token, keys["JWT_KEYS"]["admin_key"], (err, decoded) => {
          if (err) {
            res.json({ auth: false, message: "Authentication failed" });
          } else {
            req.userId = decoded.id;
            next();
          }
        });
      } else {
        req.userId = decoded.id;
        next();
      }
    });
  }
};

//Registers users by sending a request to the Backend api if there arent any faulty input that disallows the request from being sent.
//It Hashes the password and converts the hash into something we can send through an url.
app.post("/register", async (req, res) => {
  const { name, zip, address, password, email, prosumer } = req.body;
  var exists;
  if (
    name !== "" &&
    email.includes("@", ".") &&
    zip !== 0 &&
    password !== "" &&
    !name.includes("/", "=", "?", " ", "*", "<", ">", "|", ":", "/\\//g")
  ) {
    await Axios.get(
      "http://nominatim.openstreetmap.org/search.php?street=" +
        address +
        "&postalcode=" +
        zip +
        "&format=json"
    )
      .then((resp) => {
        exists = resp.data.length;
      })
      .catch((err) => err);
    if (exists === 1) {
      bcrypt.hash(password, saltRounds, (err, hash) => {
        if (err) {
          console.log(err);
        }
        var vhash = hash.replace(/\//g, "slash");
        var shash = encodeURIComponent(vhash);
        Axios.post(
          "http://127.0.0.1:5000/register/username=" +
            name +
            "&password=" +
            shash +
            "&email=" +
            email +
            "&address=" +
            address +
            "&zipcode=" +
            zip +
            "&prosumer=" +
            prosumer
        )
          .then((resp1) => {
            if (resp1.data === 1) {
              res.json({ message: "Successfull registration", succ: "succ" });
            } else {
              res.json({
                message: "Username already in use please use another one",
              });
            }
          })
          .catch((err) => err);
      });
    } else {
      res.json({ message: "Faulty address/zipcode combination" });
    }
  } else {
    res.json({ message: "Faulty inputs" });
  }

  //Login lets users login if their username exists and if the encrypted pasword matches the hash in the database.
});
app.post("/login", (req, res) => {
  console.log(keys["JWT_KEYS"]["admin_key"]);
  const name = req.body.loginName;
  const password = req.body.loginPassword;
  var id = null;
  var hash = null;
  Axios.get("http://127.0.0.1:5000/login/username=" + name).then((resp) => {
    id = resp.data.slice(89, resp.data.length - 2);
    hash = resp.data.slice(15, 75);
    if (id.length > 0 || hash.length > 0) {
      bcrypt.compare(password, hash, (error, answer) => {
        if (answer) {
          const token = jwt.sign({ id }, keys["JWT_KEYS"]["user_key"], {
            expiresIn: 300,
          });
          activeUsers.push({ createdAt: Date.now(), id: id + ", " });

          res.json({ auth: true, token: token, id: id });
        } else {
          res.json({
            auth: false,
            message: "Wrong username password combination",
          });
        }
      });
    } else {
      res.json({ auth: false, message: "no user exists" });
    }
  });
});
//Admin lets admin login if their username exists and if the encrypted pasword matches the hash in the database.
app.post("/admin", (req, res) => {
  const name = req.body.loginName;
  const password = req.body.loginPassword;
  var hash = null;
  Axios.get("http://127.0.0.1:5000/admin/login/username=" + name).then(
    (resp) => {
      hash = resp.data.slice(15, resp.data.length - 3);
      if (hash.length > 0) {
        bcrypt.compare(password, hash, (error, answer) => {
          if (answer) {
            const id = 1;
            const token = jwt.sign({ id }, keys["JWT_KEYS"]["admin_key"], {
              expiresIn: 900,
            });

            res.json({ auth: true, token: token, admin: true });
          } else {
            res.json({
              auth: false,
              message: "Wrong username password combination",
            });
          }
        });
      } else {
        res.json({ auth: false, message: "no user exists" });
      }
    }
  );
});
//Sell sends token id and amount.
app.post("/sell", (req, res) => {
  const token = req.body.token;
  const id = req.body.id;
  const sell = req.body.sell;
  Axios.post(
    "http://127.0.0.1:5000/sell/house_hold/prosumer/house_hold_id=" +
      id +
      "&amount=" +
      sell +
      "&token=" +
      token
  )
    .then((resp) => {
      res.json({ message: resp.data });
    })
    .catch((err) => err);
});
//ratio Recieves token, ratio to be and id and sends it to the backend api.
app.post("/ratio", (req, res) => {
  const token = req.body.token;
  const tempratio = req.body.tempratio;
  const id = req.body.id;
  Axios.post(
    "http://127.0.0.1:5000/change_buffert/house_hold=" +
      id +
      "&amount=" +
      tempratio +
      "&token=" +
      token
  )
    .then((resp) => {
      res.json({ data: resp.data });
    })
    .catch((err) => err);
});
//Mydata gets your personal data if your token is verified.
app.get("/mydata", verifyJWT, (req, res) => {
  const token = req.header("x-access-token");
  const id = req.header("user-id");
  Axios.get("http://127.0.0.1:5000/data/house_hold=" + id + "&token=" + token)
    .then((resp) => {
      res.json({ data: resp.data });
    })
    .catch((err) => err);
});
//market data is public knowledge so all you need to do is send the request.
app.get("/marketdata", (req, res) => {
  Axios.get("http://127.0.0.1:5000/data/get_market_data")
    .then((resp) => {
      res.json({ data: resp.data });
    })
    .catch((err) => err);
});
//Picture takes a token a type(admin/user) and id to get your personal picture.
app.post("/picture", (req, res) => {
  const token = req.body.token;
  const type = req.body.type;
  const id = req.body.id;
  Axios.get(
    "http://127.0.0.1:5000/get_user_pic?id=" +
      id +
      "&token=" +
      token +
      "&type=" +
      type
  )
    .then(function (response) {
      res.send(response.data);
    })
    .catch(function (error) {
      console.log(error);
    });
});
//logout removes the user from tthe active list.
app.post("/logout", (req, res) => {
  const id = req.body.id;
  for (var i = 0; i < activeUsers.length; i++) {
    if (activeUsers[i]["id"] === id + ", ") {
      activeUsers.splice(i, 1);
    }
  }
});
//Admindata gets all the data if verification of id and token gues through.
app.get("/admindata", verifyJWT, (req, res) => {
  const token = req.header("x-access-token");
  const id = req.header("user-id");
  Axios.get(
    "http://127.0.0.1:5000/admin/tools/view?token=" + token + "&id=" + id
  )
    .then((resp) => {
      res.json({ data: resp.data });
    })
    .catch((err) => err);
});
//Adminblock blocks the target for the cycles if adminid and token are correct.
app.post("/adminblock", (req, res) => {
  const token = req.body.token;
  const id = req.body.id;
  const block = req.body.block;
  const adminid = req.body.adminid;
  Axios.post(
    "http://127.0.0.1:5000/admin/tools/block_user_from_trade?target=" +
      id +
      "&cycle=" +
      block +
      "&id=" +
      adminid +
      "&token=" +
      token
  )
    .then((resp) => {
      res.json({ data: resp.data });
    })
    .catch((err) => err);
});
//Admindelete takes in an adminid, token and a target id to remove a user from the system
app.post("/admindelete", (req, res) => {
  const token = req.body.token;
  const id = req.body.id;
  const adminid = req.body.adminid;
  Axios.post(
    "http://127.0.0.1:5000/admin/tools/remove_user?target=" +
      id +
      "&id=" +
      adminid +
      "&token=" +
      token
  )
    .then((resp) => {
      res.send("Please check the table below that the user has been removed");
    })
    .catch((err) => err);
});
//loggedin shows the ids that are currently logged in after jwt verification for the admin and removes dupplicates if a user is online on several browsers.
app.get("/loggedin", verifyJWT, (req, res) => {
  var temparray = [];

  for (var i in activeUsers) {
    let n = 0;
    while (n <= temparray.length) {
      if (
        activeUsers[i]["id"] !== temparray[n] &&
        activeUsers[i]["id"] !== temparray[n - 1]
      ) {
        temparray.push(activeUsers[i]["id"]);
      }
      n++;
    }
  }
  res.send(temparray);
});
//Adminchange takes in any variable to be changed for user id if given id, admin id and token + what to change.
app.post("/adminchange", (req, res) => {
  var message = "Responce:";
  const { id, name, zip, address, password, email, prosumer, token, adminid } =
    req.body;
  if (
    name !== "" &&
    !name.includes("/", "=", "?", " ", "*", "<", ">", "|", ":", "/\\//g")
  ) {
    Axios.post(
      "http://127.0.0.1:5000/admin/tools/change_user_info?token=" +
        token +
        "&id=" +
        adminid +
        "&target_id=" +
        id +
        "&target_row=user_name&user_name=" +
        name
    )
      .then((resp) => {})
      .catch((message += "couldnt change name, "));
  }
  if (address !== "" && zip !== 0) {
    Axios.post(
      "http://127.0.0.1:5000/admin/tools/change_user_info?token=" +
        token +
        "&id=" +
        adminid +
        "&target_id=" +
        id +
        "&target_row=address_zipcode&address=" +
        address +
        "&zipcode" +
        zip
    )
      .then((resp) => {})
      .catch((message += "address/zip couldn't change, "));
  }
  if (password !== "") {
    bcrypt.hash(password, saltRounds, (err, hash) => {
      if (err) {
        console.log(err);
      }
      var vhash = hash.replace(/\//g, "slash");
      var shash = encodeURIComponent(vhash);
      Axios.post(
        "http://127.0.0.1:5000/admin/tools/change_user_info?token=" +
          token +
          "&id=" +
          adminid +
          "&target_id=" +
          id +
          "&target_row=password&password=" +
          shash
      )
        .then((resp) => {})
        .catch((message += "password couldn't change, "));
    });
  }
  if (email !== "" && email.includes("@", ".")) {
    Axios.post(
      "http://127.0.0.1:5000/admin/tools/change_user_info?token=" +
        token +
        "&id=" +
        adminid +
        "&target_id=" +
        id +
        "&target_row=email&email=" +
        email
    )
      .then((resp) => {})
      .catch((message += "email couldn't change, "));
  } else {
    message = "Nothing changed";
  }
  res.send(message);
});
//Factorydata takes in a token and an Id and gives out the information of the powerplants.
app.get("/factorydata", (req, res) => {
  const token = req.header("x-access-token");
  const adminid = req.header("user-id");
  Axios.get(
    "http://127.0.0.1:5000/admin/tools/view_power_plants?id=" +
      adminid +
      "&token=" +
      token
  )
    .then((resp) => {
      res.send(resp.data);
    })
    .catch((err) => err);
});
//Factoryproduction takes in a token, ratio, adminid and target factory tochange the amount of generated power.
app.post("/factoryproduction", (req, res) => {
  const token = req.body.token;
  const power = req.body.power;
  const target = req.body.target;
  const adminid = req.body.adminid;
  Axios.post(
    "http://127.0.0.1:5000/admin/tools/change_power?target=" +
      target +
      "&id=" +
      adminid +
      "&token=" +
      token +
      "&power=" +
      power
  )
    .then((resp) => {
      res.send(resp.data);
    })
    .catch((err) => err);
});
//Factorytomarket takes in a token, ratio, adminid and target factory to an amount from the buffer to the market
app.post("/factorytomarket", (req, res) => {
  const token = req.body.token;
  const amount = req.body.amount;
  const target = req.body.target;
  const adminid = req.body.adminid;
  Axios.post(
    "http://127.0.0.1:5000/admin/tools/send_to_market?target=" +
      target +
      "&id=" +
      adminid +
      "&token=" +
      token +
      "&amount=" +
      amount
  )
    .then((resp) => {
      res.send(resp.data);
    })
    .catch((err) => err);
});
//Factoryratio takes in a token, ratio, adminid and target factory to change its ratio going to the market or its buffer.
app.post("/factoryratio", (req, res) => {
  const token = req.body.token;
  const ratio = req.body.ratio;
  const adminid = req.body.adminid;
  const target = req.body.target;
  Axios.post(
    "http://127.0.0.1:5000/admin/tools/change_power_ratio?ratio=" +
      ratio +
      "&id=" +
      adminid +
      "&token=" +
      token +
      "&target=" +
      target
  )
    .then((resp) => {
      res.send("yes");
    })
    .catch((err) => err);
});

app.post("/marketprice", (req, res) => {
  const token = req.body.token;
  const price = req.body.price;
  const adminid = req.body.adminid;
  Axios.post(
    "http://127.0.0.1:5000/admin/tools/change_market_price?market_price=" +
      price +
      "&id=" +
      adminid +
      "&token=" +
      token
  )
    .then((resp) => {
      res.send(response.data);
    })
    .catch((err) => err);
});
app.listen(3001);
