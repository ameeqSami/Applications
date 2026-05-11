"""
logic.py — Data handling layer for the Academic Assessment Tracker.

Responsibilities:
  - Read / write tasks to tasks.json (persistence)
  - CRUD helpers used by the FastAPI backend
  - Urgency classification (used by both backend and frontend)
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from models import Task, TaskCreate

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TASKS_FILE = Path(__file__).parent / "tasks.json"

URGENCY_CRITICAL_HOURS = 24   # red  — deadline within 24 hours
URGENCY_WARNING_HOURS  = 72   # amber — deadline within 72 hours


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def _load_raw() -> list[dict]:
    """Return raw list of task dicts from disk, or [] if file absent/corrupt."""
    if not TASKS_FILE.exists():
        return []
    try:
        with TASKS_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_raw(tasks: list[dict]) -> None:
    """Persist the list of task dicts to disk."""
    with TASKS_FILE.open("w", encoding="utf-8") as fh:
        json.dump(tasks, fh, indent=2, default=str)


def _next_id(tasks: list[dict]) -> int:
    """Generate the next integer ID."""
    return max((t.get("id", 0) for t in tasks), default=0) + 1


# ---------------------------------------------------------------------------
# Public CRUD API
# ---------------------------------------------------------------------------

def get_all_tasks() -> List[Task]:
    """Return all tasks sorted by deadline (soonest first)."""
    raw = _load_raw()
    tasks = [Task(**t) for t in raw]
    tasks.sort(key=lambda t: t.deadline)
    return tasks


def get_task_by_id(task_id: int) -> Optional[Task]:
    """Return a single task by its ID, or None if not found."""
    raw = _load_raw()
    for t in raw:
        if t.get("id") == task_id:
            return Task(**t)
    return None


def create_task(payload: TaskCreate) -> Task:
    """Persist a new task and return the saved Task (with assigned id)."""
    raw = _load_raw()
    new_id = _next_id(raw)
    task = Task(id=new_id, **payload.dict())
    raw.append(task.dict())
    _save_raw(raw)
    return task


def update_task(task_id: int, payload: TaskCreate) -> Optional[Task]:
    """Update an existing task; returns the updated Task or None if not found."""
    raw = _load_raw()
    for i, t in enumerate(raw):
        if t.get("id") == task_id:
            updated = Task(id=task_id, **payload.dict())
            raw[i] = updated.dict()
            _save_raw(raw)
            return updated
    return None


def delete_task(task_id: int) -> bool:
    """Delete a task by ID; returns True if found and deleted."""
    raw = _load_raw()
    new_raw = [t for t in raw if t.get("id") != task_id]
    if len(new_raw) == len(raw):
        return False
    _save_raw(new_raw)
    return True


# ---------------------------------------------------------------------------
# Urgency classification
# ---------------------------------------------------------------------------

def hours_until_deadline(deadline: datetime) -> float:
    """Return the number of hours between now and the deadline (can be negative)."""
    now = datetime.now()
    # Strip timezone info from deadline if present, for naive comparison
    dl = deadline.replace(tzinfo=None) if deadline.tzinfo else deadline
    return (dl - now).total_seconds() / 3600


def classify_urgency(deadline: datetime) -> str:
    """
    Returns:
        'overdue'  — deadline has already passed
        'critical' — within URGENCY_CRITICAL_HOURS hours
        'warning'  — within URGENCY_WARNING_HOURS hours
        'normal'   — more than URGENCY_WARNING_HOURS hours away
    """
    hours = hours_until_deadline(deadline)
    if hours < 0:
        return "overdue"
    if hours <= URGENCY_CRITICAL_HOURS:
        return "critical"
    if hours <= URGENCY_WARNING_HOURS:
        return "warning"
    return "normal"


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

def get_summary_stats(tasks: List[Task]) -> dict:
    """Return a dict of aggregate stats for the dashboard."""
    now = datetime.now()
    total = len(tasks)
    overdue = sum(1 for t in tasks if hours_until_deadline(t.deadline) < 0)
    critical = sum(
        1 for t in tasks
        if 0 <= hours_until_deadline(t.deadline) <= URGENCY_CRITICAL_HOURS
    )
    upcoming = sum(
        1 for t in tasks
        if URGENCY_CRITICAL_HOURS < hours_until_deadline(t.deadline) <= URGENCY_WARNING_HOURS
    )
    total_weight = sum(t.weightage for t in tasks)
    return {
        "total": total,
        "overdue": overdue,
        "critical": critical,
        "upcoming": upcoming,
        "normal": total - overdue - critical - upcoming,
        "total_weightage": round(total_weight, 1),
    }
