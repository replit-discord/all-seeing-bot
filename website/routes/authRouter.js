import { Router } from "express";

import {
  redirectSignInController,
  callbackController
} from "../controllers/authController";

const router = Router();

router.get("/redirect/sign-in", redirectSignInController);
router.get("/callback", callbackController);

export default router;
