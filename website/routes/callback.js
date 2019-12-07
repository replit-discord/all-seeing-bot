import { Router } from "express";

const router = new Router();

router.get("/callback",
  passport.authenticate("discord", { failureRedirect: "/callback/failure" }),
  (req, res) => {
    res.redirect("/callback/success");
  }
);

router.get("/callback/failure", (req, res) => {
  if(process.env.NODE_ENV === "development") {
    res.redirect("http://localhost:80801");
    return;
  }

  res.redirect("/");
});

router.get("/callback/success", checkAuth, (req, res) => {
  if(process.env.NODE_ENV === "development") {
    res.redirect("http://localhost:8081");
    return;
  }

  res.redirect("/");
});

export default router;
