# KrishiSakhi — The Easy Way (3 steps, no coding knowledge needed)

## Step 1 — Install Python (one time only)
Go to **https://www.python.org/downloads/** and download **Python 3.11**.

Run the installer.
- **Windows:** On the very first screen, **tick the box that says "Add
  python.exe to PATH"** at the bottom, then click Install. This is the only
  thing you need to get right.
- **Mac:** just run the installer normally.

## Step 2 — Unzip this project
Right-click the zip file → **Extract All** (Windows) or just double-click it
(Mac). You'll get a folder called `agribot_project_easy`.

## Step 3 — Double-click to run
Open that folder and double-click:

- **Windows:** `RUN_ME_WINDOWS.bat`
- **Mac:** `RUN_ME_MAC_LINUX.command`
  *(Mac only: if it says "cannot be opened because it is from an unidentified
  developer" — right-click the file instead → Open → click Open again in the
  popup. You only need to do this once.)*

A black window will open and do everything automatically:
1. Sets up an isolated Python environment
2. Installs everything needed (takes 5–10 minutes the *first* time only)
3. Trains the price-prediction models
4. Starts the app

When you see a line like `Running on http://127.0.0.1:5000`, open your web
browser and go to:

```
http://localhost:5000
```

That's your KrishiSakhi dashboard — pick a crop, enter months ahead, click
**Predict Price**.

## To stop it
Click into that black window and press `Ctrl+C`.

## To run it again later
Just double-click the same file again — it'll skip straight to starting the
app since everything is already installed and trained (much faster the
second time).

## If something goes wrong
| What you see | What to do |
|---|---|
| "python is not recognized" / window closes instantly | Python isn't installed properly — reinstall it and make sure you tick "Add to PATH" |
| Stuck for a long time on package installing | Normal the first time — TensorFlow is a big download, just wait |
| "Model not trained" in the browser | Delete the `models` folder's contents and run the script again |
| Browser says "can't reach this page" | Make sure the black window is still open and running |

---

**You do not need VS Code, Android Studio, or any coding knowledge for this
version** — it's just for seeing your project work as a website. If you later
want the Android `.apk` version, that's a separate, optional step using
Android Studio (ask me and I'll walk you through it fresh).
