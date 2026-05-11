# 🎓 Academic Assessment Tracker

A modern web-based task management system for tracking academic assignments, quizzes, exams, and projects with deadline prioritization and urgency classification.

## ✨ Features

- **Task Management**: Create, read, update, and delete academic tasks
- **Urgency Tracking**: Automatic classification of tasks as Overdue, Critical, Warning, or Normal
- **Deadline Monitoring**: Track how many hours/days until each deadline
- **Statistics Dashboard**: Real-time stats showing overdue, critical, and warning tasks
- **Subject & Type Filtering**: Filter tasks by subject and task type
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Beautiful UI**: Dark theme with gradient styling and smooth animations

## 📋 Task Types

- Assignment
- Quiz
- Exam
- Project
- Lab

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- pip

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Server

```bash
python run.py
```

Or manually start with Flask:
```bash
python -m flask --app api run --host 127.0.0.1 --port 8000
```

### Step 3: Open in Browser

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

## 🐛 Issues Fixed

### Backend Configuration
✅ **Fixed mismatch between Flask (api.py) and uvicorn in run.py**
- Corrected run.py to properly start Flask development server

✅ **Added missing Flask dependency**
- requirements.txt now includes Flask==2.3.2 and Flask-CORS==4.0.0

✅ **Removed unnecessary FastAPI dependency**
- Streamlined requirements.txt for Flask-only setup

### Frontend
✅ **Created modern HTML/CSS frontend**
- Beautiful, responsive design replacing the Streamlit interface
- Real-time task rendering with filtering capabilities
- Statistics dashboard with urgency metrics

## 📊 API Endpoints

### Frontend
- `GET /` — Serves the HTML interface

### Task Management
- `GET /tasks` — Get all tasks (sorted by deadline)
- `POST /tasks` — Create a new task
- `GET /tasks/<id>` — Get a specific task
- `PUT /tasks/<id>` — Update a task
- `DELETE /tasks/<id>` — Delete a task

### Statistics
- `GET /stats` — Get summary statistics
- `GET /health` — API health check

## 🎨 UI Features

### Dashboard
- **Header**: Application title and quick stats
- **Statistics Bar**: Shows total, overdue, critical, and warning task counts
- **Task Form**: Add new tasks with deadline, subject, type, and weightage

### Task List
- **Color-Coded Urgency**: 
  - 🔴 Red (Overdue)
  - 🟠 Orange (Critical - within 24 hours)
  - 🟡 Yellow (Warning - within 72 hours)
  - 🟢 Green (Normal)
- **Task Details**: Title, subject, type, weightage, deadline, and notes
- **Quick Actions**: Edit and delete buttons for each task

### Filters
- Filter by subject
- Filter by task type
- Hide overdue tasks option

## 💾 Data Storage

Tasks are persisted in `tasks.json` with the following structure:

```json
{
  "id": 1,
  "title": "Midterm Assignment",
  "subject": "Data Structures",
  "deadline": "2026-05-12T20:23:00",
  "weightage": 20.0,
  "task_type": "Assignment",
  "notes": "Optional notes"
}
```

## ⚙️ Technical Stack

- **Backend**: Flask 2.3.2 with Python 3.8+
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data Persistence**: JSON file storage
- **Validation**: Pydantic models
- **API**: RESTful endpoints with JSON

## 📱 Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## 🔒 CORS Configuration

CORS is enabled for local development. Modify in `api.py` if deploying to production.

## 📝 Example Usage

### Create a Task
```javascript
POST /tasks
Content-Type: application/json

{
  "title": "Database Project",
  "subject": "Database Systems",
  "task_type": "Project",
  "deadline": "2026-05-15T23:59:00",
  "weightage": 30,
  "notes": "Implementation of B-tree structure"
}
```

### Get All Tasks
```bash
GET /tasks
```

## 🔄 Auto-Refresh

The task list automatically refreshes every 30 seconds to show updated urgency status.

## 📞 Support

If you encounter any issues:
1. Ensure the server is running on port 8000
2. Check that all dependencies are installed
3. Verify tasks.json exists and is readable
4. Check browser console for error messages

## 📄 License

This project is open source and available for academic use.

---

**Happy learning! 🎓**
