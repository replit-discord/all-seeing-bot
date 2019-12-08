import passport from "passport";

import { logAuthenticatedUser as log } from "../util/log";

export function redirectSignInController(req, res) {
  return passport.authenticate("discord")(req, res)
}

export let callbackController =  [
  passport.authenticate("discord", { failureRedirect: "/sign-in-failed" }),
  (req, res, next) => log(req.user.id, req.user.username) || next(),
  (req, res) => res.redirect("/dashboard")
];
