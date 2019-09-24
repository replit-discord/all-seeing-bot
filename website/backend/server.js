import http from "http";
import express from "express";
import session from "express-session";
import passport from "passport"
import passportDiscord from "passport-discord"
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(session({ secret: "fortesting", maxAge: 1000, resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj, done) => done(null, obj));
passport.use(new passportDiscord.Strategy({
  clientID: process.env.CLIENT_ID,
  clientSecret: process.env.CLIENT_SECRET,
  callbackURL: "http://localhost:3000/callback",
  scope: ["identify", "guild", "guilds.join"]
}, (accessToken, refreshToken, profile, cb) => {
  console.log(accessToken, refreshToken, profile, cb);
  process.nextTick(() => cb(null, profile));
}));

let checkAuth = (req, res, next) => {
  console.log("broth", req.user);
  console.log("brother", req.isAuthenticated());
  if (req.isAuthenticated()) return next();
  res.send("not logged in");
};

app.get("/", (req, res) => {
  res.send("hello");
});

app.get("/callback",
  passport.authenticate("discord", { failureRedirect: "/callback/failure" }),
  (req, res) => {
    console.log("SUCCESS --")
    let user = req.user;
    let account = req.account;

    console.log(user, account);
    res.redirect("/callback/success");
  }
);

app.get("/callback/failure", (req, res) => {
  res.json("failure")
});

app.get("/callback/success", checkAuth, (req, res) => {
  res.send(req.user);
});


const port = process.env.PORT || 3000;
http.createServer(app).listen(port).on("listening", () => console.log("start"));
