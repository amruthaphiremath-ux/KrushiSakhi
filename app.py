"""
ALGORITHM 6 — BACKEND PREDICTION API (RESULT DELIVERY)
------------------------------------------------------------
START
1. Receive prediction request (crop, months-ahead) from frontend
2. Trigger Algorithms 1-5 in sequence
3. Collect the final predicted price list
4. Package results into structured JSON
5. Send response back to the frontend
END

This file also adds the site's page routing: a public landing page,
login/register, and a protected dashboard that hosts the prediction tool.
"""

import os
import glob
import json
import functools
from flask import (
    Flask, render_template, request, jsonify, send_from_directory,
    session, redirect, url_for, flash,
)
from werkzeug.security import generate_password_hash, check_password_hash

from utils.predictor import predict_future_prices

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "krishisakhi-dev-secret-change-me")

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
USERS_FILE = os.path.join(BASE_DIR, "users.json")


# ---------------------------------------------------------------------
# Very small file-based user store.
# NOTE: this is intentionally simple for a college project demo. On
# free hosting tiers (e.g. Render's free plan) the filesystem is
# ephemeral, so accounts may reset on redeploy - swap USERS_FILE for a
# real database (SQLite/Postgres) before relying on this in production.
# ---------------------------------------------------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("username"):
            flash("Please log in to continue.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def available_crops():
    crops = sorted(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(DATA_DIR, "*.csv"))
    )
    if not crops:
        # Loud, unmissable log line - if the crop dropdown is ever empty
        # in production, this is the first place to check.
        app.logger.warning(
            "No crop CSV files found in %s - the crop dropdown will be "
            "empty. Confirm the data/ folder was included in the deploy.",
            DATA_DIR,
        )
    return crops


# ---------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please fill in both fields.")
            return redirect(url_for("register"))

        users = load_users()
        if username in users:
            flash("That username is already taken.")
            return redirect(url_for("register"))

        users[username] = {"password_hash": generate_password_hash(password)}
        save_users(users)

        session["username"] = username
        flash(f"Welcome to KrishiSakhi, {username}!")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        users = load_users()
        user = users.get(username)

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Incorrect username or password.")
            return redirect(url_for("login"))

        session["username"] = username
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You've been logged out.")
    return redirect(url_for("home"))


# ---------------------------------------------------------------------
# Protected dashboard (the actual prediction tool)
# ---------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", crops=available_crops())


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    payload = request.get_json(force=True) or {}
    crop = str(payload.get("crop", "")).strip()
    months_ahead = payload.get("months_ahead")

    if not crop:
        return jsonify({"success": False, "message": "Please select a crop."}), 400
    try:
        months_ahead = int(months_ahead)
        if months_ahead <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Months ahead must be a positive number."}), 400

    try:
        results = predict_future_prices(crop, months_ahead)
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "message": f"Model not trained for '{crop}'. Run: python train_model.py {crop}",
        }), 404
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    return jsonify({"success": True, "crop": crop, "predictions": results})


# ---------------------------------------------------------------------
# PWA service worker (served from root so its scope covers the whole app)
# ---------------------------------------------------------------------
@app.route("/sw.js")
def service_worker():
    response = send_from_directory(STATIC_DIR, "sw.js")
    response.headers["Service-Worker-Allowed"] = "/"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
