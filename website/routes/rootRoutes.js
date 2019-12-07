import { Router } from "express";

import {
  rootPageController,
  notSignedInController,
  signInFailedController
} from "../controllers/rootController";

const router = Router();

router.get("/", rootPageController);
router.get("/not-signed-in", notSignedInController);
router.get("/sign-in-failed", signInFailedController);

export default router;
