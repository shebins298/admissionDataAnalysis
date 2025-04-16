from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import Counter
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["https://shebins298.github.io", "http://127.0.0.1:5500"])

@app.route("/", methods=["GET"])
def home():
    return "✅ Flask server is running!", 200

@app.route("/analyze", methods=["POST"])
def analyze():
    students = request.get_json()

    total = len(students)
    if total == 0:
        return jsonify({"insights": [{"title": "No data available", "description": "0 students"}]})

    # Helper lists and counters
    commerce_values = []
    science_values = []
    science_pref = 0
    commerce_pref = 0
    science_rank1 = 0
    commerce_rank1 = 0
    submitted_counter = Counter()
    updated_counter = Counter()
    day_counter = Counter()
    hour_counter = Counter()

    for s in students:
        commerce = s.get("commerce_option", 0)
        science = s.get("science_option", 0)

        if commerce > 0:
            commerce_values.append(commerce)
            commerce_pref += 1
        if science > 0:
            science_values.append(science)
            science_pref += 1

        if commerce == 1:
            commerce_rank1 += 1
        if science == 1:
            science_rank1 += 1

        submitted_counter[s.get("submittedBy", "Unknown")] += 1
        updated_counter[s.get("lastUpdatedBy", "Unknown")] += 1

        # Timestamp parsing
        timestamp_str = s.get("timestamp")
        try:
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            day_counter[dt.date()] += 1
            hour_counter[dt.hour] += 1
        except:
            continue  # skip malformed timestamps

    avg_commerce = sum(commerce_values) / len(commerce_values) if commerce_values else 0
    avg_science = sum(science_values) / len(science_values) if science_values else 0

    # Most preferred stream
    science_1s = sum(1 for s in students if s.get("science_option", 99) == 1)
    commerce_1s = sum(1 for s in students if s.get("commerce_option", 99) == 1)
    most_preferred = "Science" if science_1s >= commerce_1s else "Commerce"

    # Top contributors
    submitted_list = sorted(submitted_counter.items(), key=lambda x: x[1], reverse=True)
    updated_list = sorted(updated_counter.items(), key=lambda x: x[1], reverse=True)

    # Busy hours and days
    busiest_hour = hour_counter.most_common(1)[0][0] if hour_counter else None
    busiest_days = sorted(day_counter.items(), key=lambda x: x[1], reverse=True)[:3]  # top 3 days

    insights = [
        {"title": "Total Applications", "description": str(total)},
        {"title": "Average Science Option", "description": f"{avg_science:.2f}"},
        {"title": "Average Commerce Option", "description": f"{avg_commerce:.2f}"},
        {"title": "Most Preferred Stream", "description": most_preferred},
        {"title": "Students who preferred Science", "description": str(science_pref)},
        {"title": "Students who preferred Commerce", "description": str(commerce_pref)},
        {"title": "Science Rank 1 Count", "description": str(science_rank1)},
        {"title": "Commerce Rank 1 Count", "description": str(commerce_rank1)},
        {"title": "Busiest Hour (24h)", "description": f"{busiest_hour}:00" if busiest_hour is not None else "N/A"},
    ]

    # Add top 5 submitters
    insights.append({"title": "Top Submitters", "description": ", ".join([f"{u} ({c})" for u, c in submitted_list[:5]])})
    insights.append({"title": "Top Updaters", "description": ", ".join([f"{u} ({c})" for u, c in updated_list[:5]])})

    # Add application per day and busy days
    insights.append({
        "title": "Applications Per Day",
        "description": ", ".join([f"{d.strftime('%d %b')}: {c}" for d, c in day_counter.items()])
    })

    insights.append({
        "title": "Most Busy Days",
        "description": ", ".join([f"{d.strftime('%d %b')} ({c})" for d, c in busiest_days])
    })

    return jsonify({"insights": insights})

