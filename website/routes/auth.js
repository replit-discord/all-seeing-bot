import { Router } from "express";

const router = Router();

router.get("/is-authenticated", (req, res) => {
  const status = req.user ? true : false;
  if(status) {
    console.log(`${req.user.username} is authenticated`);
  }
  else {
    console.log("not authenticated");
  }
  res.send({ isAuthenticated: status });
});

export default router;
