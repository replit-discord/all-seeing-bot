export function checkAuth(req, res, next) {
  // console.log("$$$$");
  // console.log(req.session);
  // console.log("$$$$");
  // console.log(req.account);
  // console.log("$$$$");
  // console.log(req.isAuthenticated());

  if (req.isAuthenticated()) {
    console.log(`'${req.user}' completed auth flow`);
    return next();
  }

  res.statusCode = 401;
  res.end("not logged in");
}
