import path from "path";
import http from "http";
import express from "express";
import session from "express-session";
import passport from "passport"
import passportDiscord from "passport-discord"
import dotenv from "dotenv";

dotenv.config();

// express setup
const app = express();
app.use(session({ secret: "fortesting2", maxAge: 1000, resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

// passport setup
passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj, done) => done(null, obj));
passport.use(new passportDiscord.Strategy({
  clientID: process.env.CLIENT_ID,
  clientSecret: process.env.CLIENT_SECRET,
  callbackURL: "http://localhost:3000/callback",
  scope: ["identify", "guild", "guilds.join"]
}, (accessToken, refreshToken, profile, cb) => {
  // console.log(accessToken, refreshToken, profile, cb);
  cb(null, profile);
}));

// utility functions
let checkAuth = (req, res, next) => {
  // console.log("$$$$");
  // console.log(req.session);
  // console.log("$$$$");
  // console.log(req.account);
  // console.log("$$$$");
  // console.log(req.isAuthenticated());

  if (req.isAuthenticated()) {
    console.log(`'${req.user}' completed auth flow`);
    return next();
  }

  res.statusCode = 401;
  res.end("not logged in");
};

// routes
app.get("/", (req, res) => {
  res.send("hello");
});

// routes: auth (some stuff temporary)
app.get("/callback",
  passport.authenticate("discord", { failureRedirect: "/callback/failure" }),
  (req, res) => {
    res.redirect("/callback/success");
  }
);

app.get("/callback/failure", (req, res) => {
  if(process.env.NODE_ENV === "development") {
    res.redirect("http://localhost:80801");
    return;
  }

  res.redirect("/");
});

app.get("/callback/success", checkAuth, (req, res) => {
  if(process.env.NODE_ENV === "development") {
    res.redirect("http://localhost:8081");
    return;
  }

  res.redirect("/");
});

// routes: data
app.get("/is-authenticated", (req, res) => {
  const status = req.user ? true : false;
  if(status) {
    console.log(`${req.user.username} is authenticated`);
  }
  else {
    console.log("not authenticated");
  }
  res.send({ isAuthenticated: status });
});

app.get("/user", checkAuth, (req, res) => {
  const status = !!req.user;

  if(status) {
    res.statusCode = 200;
    res.send(req.user);
  }
  else {
    res.statusCode = 401;
    res.end();
  }

});

const port = process.env.PORT || 3000;
http.createServer(app).listen(port).on("listening", () => console.log("start"));
