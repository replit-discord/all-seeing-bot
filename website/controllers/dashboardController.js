export function homeController(req, res) {
  res.render("pages/dashboardHome", {
    id: req.user.id,
    username: req.user.username,
    avatar: req.user.avatar,
    discriminator: req.user.discriminator,
    mfa_enabled: req.user.mfa_enabled,
    guilds: req.user.guilds
  });
}

export function profileController(req, res) {
  res.render("pages/dashboardProfile", {
    username: req.user.username
  })
}
