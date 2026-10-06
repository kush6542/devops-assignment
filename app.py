# ACEest Fitness & Gym - Flask API
# Student project for DevOps assignment 1

import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
# default db name or read from env if set
DB_NAME = os.getenv("ACEEST_DB", "aceest_fitness.db")

# calorie multipliers and notes from baseline python code
PROGRAM_FACTORS = {
    "Fat Loss (FL)": {
        "factor": 22,
        "workout": "Mon: Squat 5x5, Tue: Assault Bike 20min, Wed: Bench, Thu: Deadlift, Fri: Cardio",
        "diet": "Egg whites, grilled chicken, brown rice, fish curry (~2000 kcal)"
    },
    "Muscle Gain (MG)": {
        "factor": 35,
        "workout": "Mon: Squat 5x5, Tue: Bench 5x5, Wed: Deadlift 4x6, Thu: Front Squat, Fri: Press",
        "diet": "Eggs, PB oats, chicken biryani, mutton curry (~3200 kcal)"
    },
    "Beginner (BG)": {
        "factor": 26,
        "workout": "Circuit: Air Squats, Ring Rows, Push-ups for form mastery",
        "diet": "Balanced meals (Idli, Dosa, Dal, Rice) with 120g protein"
    }
}

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # creat tables if not existing
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            weight REAL,
            program TEXT NOT NULL,
            calories INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            week TEXT NOT NULL,
            adherence INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# init db on startup
init_db()

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "healthy",
        "app": "ACEest Fitness Management",
        "version": "1.0"
    }), 200

@app.route("/programs", methods=["GET"])
def get_programs():
    return jsonify({"programs": PROGRAM_FACTORS}), 200

@app.route("/calculate-calories", methods=["POST"])
def calc_calories():
    # calculate daily calories for a given weight and goal
    body = request.get_json() or {}
    weight = body.get("weight")
    prog = body.get("program")

    if weight is None or not prog:
        return jsonify({"error": "weight and program are required fields"}), 400

    if prog not in PROGRAM_FACTORS:
        return jsonify({"error": "invalid program selected"}), 400

    try:
        w_val = float(weight)
        if w_val <= 0:
            return jsonify({"error": "weight must be positive"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "weight must be a number"}), 400

    daily_cal = int(w_val * PROGRAM_FACTORS[prog]["factor"])
    return jsonify({
        "program": prog,
        "weight": w_val,
        "daily_calories": daily_cal
    }), 200

@app.route("/clients", methods=["POST"])
def add_client():
    body = request.get_json() or {}
    name = body.get("name", "").strip()
    age = body.get("age")
    weight = body.get("weight")
    program = body.get("program")

    if not name or not program:
        return jsonify({"error": "name and program cannot be empty"}), 400

    if program not in PROGRAM_FACTORS:
        return jsonify({"error": "invalid program name"}), 400

    cal = None
    if weight is not None:
        try:
            cal = int(float(weight) * PROGRAM_FACTORS[program]["factor"])
        except (ValueError, TypeError):
            return jsonify({"error": "weight is invalid"}), 400

    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO clients (name, age, weight, program, calories)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                age=excluded.age,
                weight=excluded.weight,
                program=excluded.program,
                calories=excluded.calories
        ''', (name, age, weight, program, cal))
        conn.commit()
    finally:
        conn.close()

    return jsonify({
        "message": f"client {name} saved successfully",
        "client": {
            "name": name,
            "age": age,
            "weight": weight,
            "program": program,
            "calories": cal
        }
    }), 201

@app.route("/clients/<string:name>", methods=["GET"])
def get_client_by_name(name):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM clients WHERE name = ?", (name,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "client not found"}), 404

    return jsonify(dict(row)), 200

@app.route("/progress", methods=["POST"])
def log_adherence():
    # log weekly adherance percent
    data = request.get_json() or {}
    client_name = data.get("client_name", "").strip()
    week = data.get("week", "").strip()
    adherence = data.get("adherence")

    if not client_name or not week or adherence is None:
        return jsonify({"error": "missing client_name, week or adherence"}), 400

    try:
        adh_val = int(adherence)
        if adh_val < 0 or adh_val > 100:
            return jsonify({"error": "adherence must be between 0 and 100"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "adherence must be integer"}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO progress (client_name, week, adherence)
        VALUES (?, ?, ?)
    ''', (client_name, week, adh_val))
    conn.commit()
    conn.close()

    return jsonify({"message": "progress logged", "adherence": adh_val}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
