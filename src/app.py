from flask import Flask, jsonify, render_template
import sys
import os

sys.path.append(os.path.dirname(__file__))
from db import get_all_attempts

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "..", "static"))

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/attempts")
def api_attempts():
    rows = get_all_attempts()
    data = []
    for r in rows:
        data.append({
            "timestamp": r[0],
            "source_ip": r[1],
            "username": r[2],
            "password": r[3],
            "country": r[4],
            "city": r[5],
            "lat": r[6],
            "lon": r[7],
        })
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
