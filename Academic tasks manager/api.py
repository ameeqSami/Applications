
"""
api.py — Flask backend for the Academic Assessment Tracker.

Endpoints:
  GET    /               — serve HTML frontend
  GET    /tasks          — list all tasks (sorted by deadline)
  POST   /tasks          — create a new task
  GET    /tasks/<int:task_id> — retrieve a single task
  PUT    /tasks/<int:task_id> — update a task
  DELETE /tasks/<int:task_id> — remove a task
  GET    /stats          — summary statistics
  GET    /health         — liveness check
"""
from __future__ import annotations

import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

import logic
from models import TaskCreate
from pydantic import ValidationError

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for frontend on same machine

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def serve_index():
    """Serve the HTML frontend."""
    return send_file('index.html', mimetype='text/html')


@app.route("/cgpa", methods=["GET"])
def serve_cgpa():
    """Serve the CGPA calculator page."""
    return send_file('cgpa.html', mimetype='text/html')


@app.route("/add-task", methods=["GET"])
def serve_add_task():
    """Serve the Add Task page."""
    return send_file('add-task.html', mimetype='text/html')


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "Academic Assessment Tracker"})


@app.route("/tasks", methods=["GET"])
def list_tasks():
    """Return all tasks sorted by deadline (soonest first)."""
    tasks = logic.get_all_tasks()
    return jsonify([t.dict() for t in tasks])


@app.route("/tasks", methods=["POST"])
def create_task():
    """Add a new academic task."""
    try:
        payload = request.get_json()
        task_create = TaskCreate(**payload)
        task = logic.create_task(task_create)
        return jsonify(task.dict()), 201
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 422
    except Exception as e:
        return jsonify({"detail": str(e)}), 400


@app.route("/tasks/<int:task_id>", methods=["GET"])
def read_task(task_id: int):
    task = logic.get_task_by_id(task_id)
    if task is None:
        return jsonify({"detail": f"Task {task_id} not found"}), 404
    return jsonify(task.dict())


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id: int):
    try:
        payload = request.get_json()
        task_create = TaskCreate(**payload)
        task = logic.update_task(task_id, task_create)
        if task is None:
            return jsonify({"detail": f"Task {task_id} not found"}), 404
        return jsonify(task.dict())
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 422
    except Exception as e:
        return jsonify({"detail": str(e)}), 400


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id: int):
    if not logic.delete_task(task_id):
        return jsonify({"detail": f"Task {task_id} not found"}), 404
    return "", 204


@app.route("/stats", methods=["GET"])
def get_stats():
    """Return aggregate statistics (counts by urgency level, total weightage)."""
    tasks = logic.get_all_tasks()
    stats = logic.get_summary_stats(tasks)
    return jsonify(stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
