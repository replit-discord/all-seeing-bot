export function rootPageController(req, res) {
  res.redirect("/dashboard");
}

export function notSignedInController(req, res) {
  res.render("pages/rootNotSignedIn");
}

export function signInFailedController(req, res) {
  res.render("pages/rootSignInFailed");
}
