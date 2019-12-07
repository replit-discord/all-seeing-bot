import { Router } from "express";

import {
  homeController,
  profileController
} from "../controllers/dashboardController"

const router = Router()

router.get("/", (req, res) => res.redirect("/dashboard/home"));
router.get("/home", homeController);
router.get("/profile", profileController);

export default router;
