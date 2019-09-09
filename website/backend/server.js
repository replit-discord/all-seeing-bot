import express from "express";

const app = express();
app.use(express.static("public", { extensions: true }));

app.listen(3000, "0.0.0.0", 511, () => console.log("Working"));
