# npm

Rules of the skill `build-system` for a project built with npm.

## Portable
A Node.js script of the project does the job of the commands of a POSIX shell (`"build": "node scripts/build.js"`). The script of `package.json` keeps its name and its job.

## No global variable
- A script does not need a variable of the environment that the shell sets (`NODE_ENV=test node ...`). The Node.js script sets the variable itself, or gives it to the process that it starts.
- A script does not need a tool installed with `npm install -g`. It calls Node.js and the tools of `devDependencies` only.
