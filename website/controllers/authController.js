export function redirectSignInController(req, res) {
  res.redirect("/link-to-discord")
}

export function callbackController(req, res) {
  passport.authenticate("discord", { failureRedirect: "/auth/callback/failure" }),
    (req, res) => {
      res.redirect("/auth/callback/success");
    }
}

export function callbackFailureController(req, res) {
  res.redirect("/sign-in-failed");
}

export function callbackSuccessController(req, res) {
  res.redirect("/dashboard");
}
