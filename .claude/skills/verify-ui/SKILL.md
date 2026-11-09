---
name: verify-ui
description: Verify a change in the running Airel web app, signed in without Google. Use after changing anything a page shows (web/ components, routes, styles, or GraphQL data the UI reads), when asked to check, screenshot or demo a page, or before saying UI work is done.
---

# Verify a change in the running web app

The proof is the page itself: the changed page loads, shows the change, and has no new console errors or failed requests. Tests and `vp check` don't count as UI proof.

## 1. Servers up

- **api** on 8000 and **web** on 5173 (`Procfile.dev`). With the Browser pane: `preview_start` with `api`, then `web` (`.claude/launch.json`). Without it: `api/.venv/bin/honcho -f Procfile.dev start api web` in the background.
- Done when `curl -s localhost:8000/healthcheck/` prints `OK` and `curl -so /dev/null -w '%{http_code}' localhost:5173/` prints `200`.

## 2. Sign-in users

`api/.venv/bin/python api/manage.py seed_dev` (idempotent). It ensures two users with no password, **dm** (staff, superuser) and **player** (plain user), and on an empty database also a small world: races, places, characters, items, an artifact and three game logs. A database with real logs (a local copy of production) gets only the users.

## 3. Look at the page

Pick the user the change is about: **dm** for editing and staff-only UI, **player** for what players see, `anon` for signed-out pages.

**Browser pane (desktop app).** Get tokens with `api/.venv/bin/python api/manage.py dev_login dm --json`. On a page of `http://localhost:5173`, set both as cookies, then navigate:

```js
document.cookie = 'access_token=<access_token>; path=/; SameSite=Strict';
document.cookie = 'refresh_token=<refresh_token>; path=/; SameSite=Strict';
location.href = '/database/characters';
```

The web app renews the 5-minute access token from the refresh token (7 days), so this lasts the session. Signed in, the sidebar footer shows the username and clearance.

**Headless (cloud sessions, no pane).** From `web/`:

```sh
node scripts/browse.ts /database/characters --as dm --out /tmp/characters.png
```

It signs in, loads the page, saves a screenshot and prints status, title, console errors, failed requests and visible text. Options: `--as dm|player|anon`, `--width 390` for phone width, `--full-page`, `--max-text`. Read the screenshot to look at it.

Chromium: it uses Playwright's own browser when installed, else `$BROWSE_CHROMIUM_PATH`, else a Chromium preinstalled under `$PLAYWRIGHT_BROWSERS_PATH` (default `/opt/pw-browsers`; cloud sessions use this, since the proxy blocks Playwright's download host). `node scripts/browse.ts --check-browser` prints which one launches. Locally, if none is found: `vp exec playwright install chromium --only-shell`.

## 4. Report

Done when you've looked at every page the change touches (and phone width when layout changed), each shows the change, and console errors and failed requests are none, or the same as before the change. Report what you checked, as whom, and anything you couldn't check. Attach the key screenshot when the change is visual.

`seed_dev` and `dev_login` refuse to run unless Django's `DEBUG` is on. `api/website/settings.py` turns it off when `COOLIFY_URL` is set, as Coolify sets it in production.
