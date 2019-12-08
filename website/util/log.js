import chalk from "chalk";

export function logAuthenticatedUser(id, username) {
  log({
    title: "new user authenticated",
    content: `${username} ${id}`,
    fallback: "a new user authenticated"
  });
}

function log({
  priority,
  title = "title",
  content,
  fallback = "default fallback"
}) {
  process.env.NODE_ENV === "production" ? false : true
  ? console.log(
    priority === "warning" ? chalk.red(title) : chalk.blue(title) +
    ': ' +
    chalk.white(!!content ? content : fallback)
  )
  : console.log("not printing in production");
}

