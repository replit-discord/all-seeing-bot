export function checkAuth(req, res, next) {
  // console.log("$$$$");
  // console.log(req.session);
  // console.log("$$$$");
  // console.log(req.account);
  // console.log("$$$$");
  // console.log(req.isAuthenticated());

  if (req.isAuthenticated()) {
    console.log(`'${req.user}' completed auth flow`);
    next();
  }

  res.statusCode = 401;
  res.redirect("/not-signed-in");
}
