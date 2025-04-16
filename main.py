from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://shebins298.github.io"])  # Limit CORS to your GitHub Pages site


@app.route("/analyze", methods=["POST"])
def analyze():
    students = request.get_json()

    # 🔍 Example Analysis: total submissions, average options
    total_students = len(students)
    avg_commerce = sum(s.get("commerce_option", 0) for s in students) / total_students
    avg_science = sum(s.get("science_option", 0) for s in students) / total_students

    result = {
        "insights": [
            {"title": "Total Applications", "description": str(total_students)},
            {"title": "Average Commerce Option", "description": f"{avg_commerce:.2f}"},
            {"title": "Average Science Option", "description": f"{avg_science:.2f}"}
        ]
    }

    return jsonify(result)
