# Scenario 2: npm scripts that work in a POSIX shell only are made to work on Windows too, and the build folder leaves git

## Prompt
Improve the build system of this project.

## Setup
Create `package.json` with this exact content:

````
{
  "name": "textkit",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "clean": "rm -rf dist",
    "build": "rm -rf dist && mkdir -p dist && cp src/*.js dist/",
    "test": "NODE_ENV=test node --test test/words.test.js"
  }
}
````

Create `package-lock.json` with this exact content:

````
{
  "name": "textkit",
  "version": "1.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "textkit",
      "version": "1.0.0"
    }
  }
}
````

Create `.gitignore` with this exact content:

````
node_modules/
.env
````

Create `README.md` with this exact content:

````
# textkit

Text utilities.

## Build and test

```
npm ci
npm run build
npm test
```
````

Create `src/words.js` with this exact content:

````
export function countWords(text) {
  const words = text.trim().split(/\s+/);
  return words[0] === '' ? 0 : words.length;
}
````

Create `dist/words.js` with this exact content:

````
export function countWords(text) {
  const words = text.trim().split(/\s+/);
  return words[0] === '' ? 0 : words.length;
}
````

Create `test/words.test.js` with this exact content:

````
import assert from 'node:assert/strict';
import test from 'node:test';
import { countWords } from '../src/words.js';

test('counts the words', () => {
  assert.equal(countWords('one two three'), 3);
});

test('runs in the test environment', () => {
  assert.equal(process.env.NODE_ENV, 'test');
});
````

Then run in the scratch directory: `git init -b main`, `git add -A` and `git -c user.name=test -c user.email=test@example.com commit -m init`.

## Pass criteria
- [ ] `package.json` parses as JSON and has the scripts `clean`, `build` and `test`. No script contains `rm -rf`, `mkdir -p` or `cp `, and the script `test` does not start with `NODE_ENV=`: these work in a POSIX shell only.
- [ ] `package.json` has no `dependencies` and no `devDependencies`, and `package-lock.json` has the exact Setup content.
- [ ] Run in the scratch directory, in this order: `npm run build` exits with code 0, and `dist/words.js` then has the content of `src/words.js`. `npm test` exits with code 0. `npm run clean` exits with code 0, and `dist` then does not exist.
- [ ] `git ls-files dist` prints nothing: no file of `dist` is in the index of git.
- [ ] `.gitignore` still has the lines `node_modules/` and `.env`, and `git check-ignore -q dist/words.js` exits with code 0.
- [ ] `src/words.js` and `test/words.test.js` have the exact Setup content.
- [ ] The final output says that the commands were run locally and passed (it contains `passed`), and that they were not run on macOS and not run on Windows (it names both).

## RED baseline (without the skill)
2026-11-22 — FAIL (3 of 3 runs failed) — all 3 replaced `rm`, `mkdir` and `cp` with Node.js, but left `NODE_ENV=test` at the start of the script `test` (2 said that it works in a POSIX shell only). 2 runs left `dist/words.js` in git and did not ignore `dist`: they wrote that the human partner can remove it. All 3 changed what the script `test` runs (a glob in place of the file), and 1 added `engines` with a version that it guessed: nobody asked for it. No run said that the commands were not run on macOS and Windows. Two earlier versions of this scenario failed the same way (3 of 3 runs each). The first had `node --test` without a file name: a wrapper script called `test.js` would be found by the test runner, and would start itself again without end. The second had no `dist` folder in git.
