import http from "http";
import { join } from "path";

import dotenv from "dotenv";
import express from "express";
import hbs from "hbs";
import session from "express-session";
import passport from "passport";
import passportDiscord from "passport-discord";

import rootRoutes from './routes/rootRoutes';
import dashboardRoutes from "./routes/dashboardRoutes";
import authRoutes from "./routes/authRouter";
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
hbs.localsAsTemplateData(app);
app.use("/", express.json());

// session
app.use(session({
  secret: "fortesting2",
  maxAge: 1000,
  resave: false,
  saveUninitialized: false
}));

// passport
const callbackURL = process.env.NODE_ENV === "development" ? "http://localhost:3000/auth/callback" : "https://allseeingbot.com/auth/callback";
app.use(passport.initialize());
app.use(passport.session());
passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj, done) => done(null, obj));
passport.use(new passportDiscord.Strategy({
  clientID: process.env.CLIENT_ID,
  clientSecret: process.env.CLIENT_SECRET,
  callbackURL: callbackURL,
  scope: ["identify", "guilds"]
}, (accessToken, refreshToken, profile, cb) => {
  // console.log(accessToken, refreshToken, profile, cb);
  cb(null, profile);
}));

// app
app.use(express.static("public"));
app.use("/", rootRoutes);
app.use("/dashboard", checkAuth, dashboardRoutes);
app.use("/auth", authRoutes);

// listen
const port = process.env.PORT || 3000;
http.createServer(app)
  .listen(port, () => console.log("start"));
