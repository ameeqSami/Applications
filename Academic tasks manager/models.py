"""
models.py — Pydantic data models for the Academic Assessment Tracker.
Shared between the FastAPI backend and the Streamlit frontend.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class Task(BaseModel):
    """Represents a single academic task (quiz, assignment, exam, etc.)."""

    id: Optional[int] = Field(default=None, description="Auto-assigned unique identifier")
    title: str = Field(..., min_length=1, max_length=120, description="Name of the task")
    subject: str = Field(..., min_length=1, max_length=80, description="Subject / course name")
    deadline: datetime = Field(..., description="Due date and time (ISO 8601)")
    weightage: float = Field(
        ..., ge=0.0, le=100.0, description="Contribution to final grade (0–100 %)"
    )
    task_type: str = Field(
        default="Assignment",
        description="Category: Assignment, Quiz, Exam, Project, Lab",
    )
    notes: Optional[str] = Field(default=None, max_length=500, description="Optional remarks")

    @validator("task_type")
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        allowed = {"Assignment", "Quiz", "Exam", "Project", "Lab"}
        if v not in allowed:
            raise ValueError(f"task_type must be one of {allowed}")
        return v

    @validator("deadline", pre=True)
    @classmethod
    def parse_deadline(cls, v):
        if isinstance(v, str):
            # Accept both with and without timezone info
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse deadline: {v!r}")
        return v

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}


class TaskCreate(BaseModel):
    """Payload used when creating a new task (no id required)."""

    title: str = Field(..., min_length=1, max_length=120)
    subject: str = Field(..., min_length=1, max_length=80)
    deadline: datetime
    weightage: float = Field(..., ge=0.0, le=100.0)
    task_type: str = Field(default="Assignment")
    notes: Optional[str] = Field(default=None, max_length=500)

    @validator("task_type")
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        allowed = {"Assignment", "Quiz", "Exam", "Project", "Lab"}
        if v not in allowed:
            raise ValueError(f"task_type must be one of {allowed}")
        return v

    @validator("deadline", pre=True)
    @classmethod
    def parse_deadline(cls, v):
        if isinstance(v, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse deadline: {v!r}")
        return v
