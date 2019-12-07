import http from "http";
import { join } from "path";

import dotenv from "dotenv";
import express from "express";
import hbs from "hbs";
import session from "express-session";
import passport from "passport"
import passportDiscord from "passport-discord"

import dashboardRoutes from "./routes/dashboardRoutes"
import { checkAuth } from "./middleware";

// dotenv
dotenv.config();

// express
const app = express();
app.enable("case sensitive routing");
app.set("json spaces", 2);
app.disable("strict routing");
app.set("view engine", "hbs");
app.disable("x-powered-by");

// handlebars
app.engine("hbs", hbs.__express);
hbs.registerPartials(join(__dirname, "views", "partials"));
hbs.registerPartials(join(__dirname, "views", "components"));
// hbs.localsAsTemplateData(app);
app.use("/", express.json());

// session
app.use(session({
  secret: "fortesting2",
  maxAge: 1000,
  resave: false,
  saveUninitialized: false
}));

// passport
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
  // console.log(accessToken, refreshToken, profile, cb);
  cb(null, profile);
}));

// app
app.use("/", express.static("public"));

app.get("/", (req, res) => res.redirect("/dashboard"));
app.use("/dashboard", dashboardRoutes);

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

// listen
const port = process.env.PORT || 3000;
http.createServer(app)
  .listen(port, () => console.log("start"));
