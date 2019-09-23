import express from "express";

const app = express();

app.get("/", (req, res) => {
  res.send("hello");
});

const port = process.env.PORT || 8080;
app.listen(port, "0.0.0.0", () => console.log("start"));
