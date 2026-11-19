import json
import os

import pymongo
from flask import Flask, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Only one setting is needed: MONGO_URL (either as its own Render env var,
# or inside an APP_CONFIG JSON object, like your shop site).
try:
    APP_CONFIG = json.loads(os.environ.get("APP_CONFIG", "{}"))
    if not isinstance(APP_CONFIG, dict):
        APP_CONFIG = {}
except (json.JSONDecodeError, TypeError):
    APP_CONFIG = {}


def config_value(name, default=""):
    value = APP_CONFIG.get(name)
    if value is None or value == "":
        value = os.environ.get(name, default)
    return value


MONGO_URL = config_value("MONGO_URL")
MONGO_DB_NAME = config_value("MONGO_DB_NAME", "exhibition")

SITE = {
    "eyebrow": "SCHOOL SCIENCE EXHIBITION",
    "title": "Exhibition Projects",
    "subtitle": "Ideas that move, sense, and amaze.",
}

# Default content. It is copied into MongoDB the first time the site starts.
# After that, edit the documents in MongoDB (collection "projects") and the
# website updates by itself. "image" is any image URL (e.g. from Google).
DEFAULT_PROJECTS = [
    {
        "slug": "magical-number", "order": 1, "interactive": "magic",
        "name": "Magical Number", "tag": "Interactive Experience",
        "summary": "Think of any number. Six cards. One reveal.",
        "image": "", "glyph": "7", "accent": ["#7c5cff", "#00d4ff"],
        "details": [
            {"heading": "The idea", "text": "Pick a secret number from 1 to 63 and answer six simple questions. The program names your number instantly."},
            {"heading": "The secret", "text": "Every number can be written in binary using the values 1, 2, 4, 8, 16 and 32. Each card holds exactly the numbers that use one of those values. Adding the first number of every card you said yes to gives your number."},
        ],
    },
    {
        "slug": "piezoelectric-sensor", "order": 2, "interactive": "",
        "name": "Piezoelectric Sensor", "tag": "Sensors & Energy",
        "summary": "Pressure becomes electricity.",
        "image": "", "glyph": "\u223f", "accent": ["#f3d47a", "#ff5fa2"],
        "details": [
            {"heading": "How it works", "text": "Piezoelectric crystals produce a small voltage when they are squeezed, bent or struck. The harder the force, the larger the signal."},
            {"heading": "Where it is used", "text": "Lighters, microphones, knock sensors, ultrasound scanners and footstep energy harvesting."},
            {"heading": "Our model", "text": "Details of our model will be added here."},
        ],
    },
    {
        "slug": "cookie-lady", "order": 3, "interactive": "",
        "name": "Cookie Lady", "tag": "Featured Project",
        "summary": "A project with a lot of character.",
        "image": "", "glyph": "\u25cd", "accent": ["#ff9a5f", "#ff5fa2"],
        "details": [
            {"heading": "About this project", "text": "Details coming soon."},
        ],
    },
    {
        "slug": "maglev-train", "order": 4, "interactive": "",
        "name": "Maglev Train Model", "tag": "Transport & Physics",
        "summary": "A train that floats on magnetic force.",
        "image": "", "glyph": "\u27ff", "accent": ["#00d4ff", "#5f7bff"],
        "details": [
            {"heading": "How it works", "text": "Powerful magnets lift the train a few millimetres above the track, so there is no wheel friction. Electromagnets along the track then push and pull it forward."},
            {"heading": "Why it matters", "text": "No friction means higher speed, less noise and less wear than a conventional train."},
            {"heading": "Our model", "text": "Details of our model will be added here."},
        ],
    },
    {
        "slug": "radar-system", "order": 5, "interactive": "",
        "name": "Radar System", "tag": "Electronics",
        "summary": "Seeing the invisible with waves.",
        "image": "", "glyph": "\u25ce", "accent": ["#43e6a0", "#00b4d8"],
        "details": [
            {"heading": "How it works", "text": "A radar sends out a pulse of radio or ultrasonic waves. When the pulse hits an object it bounces back, and the time taken tells us how far away the object is."},
            {"heading": "Where it is used", "text": "Aircraft tracking, weather forecasting, ships, speed guns and parking sensors."},
            {"heading": "Our model", "text": "Details of our model will be added here."},
        ],
    },
]

app = Flask(__name__, static_folder=None)

_collection = None
if MONGO_URL:
    try:
        _client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        _collection = _client[MONGO_DB_NAME]["projects"]
    except Exception:
        app.logger.exception("Could not create the MongoDB client")


def load_projects():
    """Return projects from MongoDB (seeding it once); fall back to defaults."""
    if _collection is None:
        return DEFAULT_PROJECTS
    try:
        if _collection.count_documents({}) == 0:
            _collection.insert_many([dict(p) for p in DEFAULT_PROJECTS])
        records = list(_collection.find({}, {"_id": 0}).sort("order", 1))
        return records or DEFAULT_PROJECTS
    except Exception:
        app.logger.exception("MongoDB unavailable; using built-in project details")
        return DEFAULT_PROJECTS


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/style.css")
def style():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/script.js")
def script():
    return send_from_directory(BASE_DIR, "script.js")


@app.route("/api/projects")
def api_projects():
    response = jsonify({"site": SITE, "projects": load_projects()})
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
