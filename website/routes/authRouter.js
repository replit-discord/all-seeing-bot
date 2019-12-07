import { Router } from "express";

import {
  redirectSignInController,
  callbackController,
  callbackFailureController,
  callbackSuccessController
} from "../controllers/authController";

const router = Router();

router.get("/redirect/sign-in", redirectSignInController);
router.get("/callback", callbackController);
router.get("/callback/failure", callbackFailureController);
router.get("/callback/success", callbackSuccessController);

export default router;
