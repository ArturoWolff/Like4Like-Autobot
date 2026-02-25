# Like4Like Autobot

> A headless Chrome automation bot that grinds [Like4Like](https://www.like4like.org) credits on autopilot — liking Facebook posts and Instagram posts/profiles so your own content gets boosted in return.

---

## How Like4Like Works (and why this bot exists)

Like4Like is an exchange platform: you earn **credits** by engaging with other users' content (liking posts, following profiles), and those credits are spent to push your own content to other users' queues. The grind is entirely mechanical — click a button, wait for a popup, click Like, close the popup, confirm the action. Human eyes are not required.

This bot automates that mechanical loop end-to-end using **Selenium** driving a **real** Chrome instance (via `undetected-chromedriver`, which patches the CDP fingerprint to pass bot-detection). Because it uses a **persistent Chrome profile**, your session cookies survive between runs, so you log in once and the bot rides that session indefinitely.

---

## Architecture

```
Like4Like Autobot/
├── main.py                  # Entry point & CLI menu
├── run_bot.sh               # Shell launcher (activates venv, runs main.py)
├── requirements.txt         # Python dependencies
├── chrome_profile/          # Persistent Chrome user-data-dir (gitignore this)
└── bot_logic/
    ├── __init__.py
    ├── utils.py             # Shared helpers (login nav, points reader)
    ├── facebook.py          # Facebook Likes engine
    ├── instagram.py         # Instagram Likes + Follows engines
    └── master.py            # Orchestrator that cycles all three modules
```

### `main.py` — CLI Menu & Browser Bootstrap

The top-level entry point presents an interactive menu. Before any loop runs, it calls `setup_browser()`, which instantiates an `undetected_chromedriver.Chrome` object pointed at the persistent `chrome_profile/` directory. This means:

- The browser opens with your previously saved cookies, extensions, and preferences.
- Chrome version is pinned to `version_main=145` to keep the ChromeDriver patch aligned with your installed browser.
- The `driver` object is passed **by reference** into whichever module runs next — there is only ever one browser instance open at a time.

### `utils.py` — Shared Primitives

Two functions used by every module:

| Function | What it does |
|---|---|
| `login_like4like(driver)` | Navigates to `like4like.org/login/`, then waits 30 seconds (countdown printed to console) for you to log in manually if needed. On subsequent runs the session is already authenticated, so this is effectively a no-op. |
| `get_current_points(driver)` | Reads the `#earned-credits` element's text and returns it as an `int`. Returns `None` on failure. Used to verify that an interaction actually awarded points. |

### `facebook.py` — Facebook Likes Engine

**Entry point:** `run_facebook_batch(driver, batch_size=None)`

Flow per iteration:
1. Navigate to `like4like.org/user/earn-facebook.php`.
2. Ensure the **"Only Posts"** radio button (`#onlyPosts`, value `2`) is selected (refreshes page if it wasn't).
3. Find and click the green `.earn_pages_button` link.
4. Switch focus to the newly opened popup window.
5. Wait 6 seconds for Facebook's JS to render inside the popup.
6. Search for overlay `role="dialog"` containers (Facebook's post modal), then within that scope look for a `div[role="button"]` whose `aria-label` is `"Like"` or `"Me gusta"` (case-insensitive, handles Spanish locale).
7. `scrollIntoView` the button and click it via `execute_script` (avoids interception by overlapping elements).
8. Close the popup, switch back to the main window.
9. Click the `confirm1.png` confirmation button on Like4Like.
10. Poll `get_current_points()` up to 8 times (1-second intervals) waiting for the point total to increment.
11. If points didn't change → **failsafe reset**: navigate to homepage then back to the earn page and retry.
12. If points changed → `successful_actions += 1`, sleep 3 seconds, continue.
13. Loop exits when `batch_size` is reached or no more earn buttons are found.

**Returns** `True` on clean exit, `False` on fatal `WebDriverException` (browser closed/disconnected).

### `instagram.py` — Instagram Engines

Two separate batch runners share the same structural pattern:

#### `run_instagram_like_batch(driver, batch_size=None)` — Instagram Likes

Targets `like4like.org/user/earn-instagram-like.php`. After opening the popup:
- Checks for an **Unlike** SVG (`aria-label="Unlike"`) first — if already liked, treats as `"already_liked"` and still confirms with Like4Like (credits are awarded regardless).
- If not liked, finds the **Like** SVG via a fallback chain of 4 CSS/XPath selectors (handles Instagram's frequent class-name obfuscation).
- Clicks via `closest('div[role="button"]').click()` with a fallback to direct `execute_script` click, then `.click()`.
- Confirmation and points-poll logic is identical to the Facebook module.

#### `run_instagram_follow_batch(driver, batch_size=5)` — Instagram Follows

Targets `like4like.org/user/earn-instagram-follow.php`. After opening the popup:
- Waits 8 seconds (Instagram profile pages are heavier than post modals).
- Finds `div[text()='Follow']` and clicks it.
- Verifies state changed to `"Following"`.
- Handles edge cases: already following, private accounts (`"Requested"` state).
- Only confirms with Like4Like if the follow actually succeeded.

> **Why default `batch_size=5` for follows?** Instagram's follow rate-limits are aggressive. The master loop enforces an additional 1-hour cooldown on top of the batch cap.

### `master.py` — The Orchestrator

`start_master_loop(setup_browser_func)` is the "set and forget" mode. It opens **one browser instance** for the entire session and cycles through:

```
loop forever:
    → run_facebook_batch(driver)        # unlimited, runs until queue empty
    → sleep 5s
    → run_instagram_like_batch(driver)  # unlimited, runs until queue empty
    → sleep 5s
    → if time since last follow >= 3600s:
          run_instagram_follow_batch(driver, batch_size=5)
          reset cooldown timer
      else:
          print remaining minutes
    → sleep 5s
```

If any module returns `False` (fatal browser error), the master loop breaks and the browser is cleanly quit. `Ctrl+C` is caught gracefully and also triggers cleanup.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.8+ | Tested on 3.10/3.11 |
| Google Chrome | Must match or exceed `version_main=145` in `main.py` |
| A Like4Like account | Free tier works |
| Facebook & Instagram accounts | Linked to your Like4Like campaigns |

---

## Setup

### 1. Clone / download the project

```bash
cd /path/to/your/projects
# (project is already here if you're reading this)
```

### 2. Create and activate the virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` pulls in:
- `undetected-chromedriver` — Chrome automation with bot-detection bypass
- `selenium` — WebDriver interface
- `setuptools` — build dependency for the above

### 4. First Run — Login Setup

```bash
./run_bot.sh
# or: source venv/bin/activate && python main.py
```

Select **option 1 — Setting Up**. The browser will open. Log in to:
1. [like4like.org](https://www.like4like.org)
2. [facebook.com](https://www.facebook.com)
3. [instagram.com](https://www.instagram.com)

Close the browser window when done. Your session is now saved in `chrome_profile/`. You will **not** need to log in again unless cookies expire.

---

## Usage

```
========================================
       LIKE4LIKE AUTOBOT MENU
========================================
1. Setting Up (Open browser for manual login)
2. Facebook Likes Loop
3. Instagram Follow Loop
4. Instagram Likes Loop
5. Master Loop (Cycles through all)
0. Exit
========================================
```

| Option | What it runs | Ends when |
|---|---|---|
| `1` | Opens a live browser for manual setup | You close the browser |
| `2` | `run_facebook_batch(driver)` | Queue empty or `Ctrl+C` |
| `3` | `run_instagram_follow_batch(driver)` | 5 follows done or queue empty |
| `4` | `run_instagram_like_batch(driver)` | Queue empty or `Ctrl+C` |
| `5` | `start_master_loop(setup_browser)` | Fatal error or `Ctrl+C` |

**For unattended overnight runs, use option 5.** It handles the follow cooldown automatically and keeps cycling Facebook and Instagram likes in between.

---

## The Login Flow — Why the 30-Second Window

Every module calls `login_like4like(driver)` at startup, which navigates to `like4like.org/login/` and waits 30 seconds. This is a **soft gate**:

- If the session cookie is valid (normal case), Like4Like auto-redirects you to the dashboard within a second or two, and the bot proceeds when the 30-second timer expires regardless.
- If the session expired, you have 30 seconds to manually type credentials. The bot doesn't automate this login step intentionally, to avoid storing credentials in plaintext.

---

## Chrome Version Pinning

In `main.py`:

```python
driver = uc.Chrome(options=options, version_main=145)
```

`undetected-chromedriver` downloads a matching ChromeDriver binary for the specified major version. If you upgrade Chrome beyond version 145, update this number accordingly. To find your Chrome version:

```bash
google-chrome --version
# or
chromium --version
```

---

## Failsafe & Error Recovery

The bot is designed to be self-healing within a session:

| Condition | Response |
|---|---|
| Points didn't increment after interaction | Navigate to homepage → back to earn page, retry |
| Confirmation button not found | Log warning, continue to next item |
| Popup didn't open | Navigate to homepage → back to earn page, retry |
| Post already liked on Instagram | Still confirm with Like4Like (you still earn credits) |
| Instagram account is private | Skip, continue |
| `WebDriverException` (browser closed) | Return `False`, bubble up to caller for graceful exit |
| `KeyboardInterrupt` | Caught at every level, browser is cleanly `.quit()`-ed |

---

## Known Limitations

- **Like4Like queue dependency:** When Like4Like runs out of tasks to serve (no more posts/profiles in the queue), the loop pauses itself and waits for the next master loop cycle. This is normal — you're at the mercy of how many other users have submitted tasks.
- **Instagram rate limits:** Instagram actively throttles likes and follows. The 1-hour follow cooldown in the master loop is intentional mitigation. Aggressive runs may still trigger temporary action blocks on Instagram's side.
- **Chrome version drift:** If Chrome auto-updates past the pinned `version_main`, the driver initialization will fail. Update the value in `main.py` when this happens.
- **Locale-aware Like button:** The Facebook like button search handles English (`"like"`) and Spanish (`"me gusta"`) `aria-label` values. If your Facebook is in another language, add the localized label to the XPath in `facebook.py`.
- **Single browser instance:** The bot does not parallelize. One browser, one action at a time. This is intentional — multiple instances would share the same Chrome profile and corrupt it.

---

## File Reference

| File | Role |
|---|---|
| [`main.py`](./main.py) | CLI entry point, browser setup, menu routing |
| [`run_bot.sh`](./run_bot.sh) | Shell launcher, venv activation |
| [`requirements.txt`](./requirements.txt) | Python package dependencies |
| [`bot_logic/utils.py`](./bot_logic/utils.py) | `login_like4like`, `get_current_points` |
| [`bot_logic/facebook.py`](./bot_logic/facebook.py) | Facebook Likes batch runner |
| [`bot_logic/instagram.py`](./bot_logic/instagram.py) | Instagram Likes + Follows batch runners |
| [`bot_logic/master.py`](./bot_logic/master.py) | Master orchestration loop |
| `chrome_profile/` | Chrome persistent session data (do not delete) |

---

## Quick Start (TL;DR)

```bash
# First time only:
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Every time:
./run_bot.sh
# → Select 1, log in to Like4Like + Facebook + Instagram, close browser
# → Select 5 for the full master loop
```
