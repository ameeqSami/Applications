import os
import json
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_cyber_key_2026'
DB_FILE = 'database.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return {'users': [], 'tasks': []}
    with open(DB_FILE, 'r') as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                # migrate old list structure
                return {'users': [], 'tasks': data}
            if 'users' not in data:
                data['users'] = []
            if 'tasks' not in data:
                data['tasks'] = []
            return data
        except:
            return {'users': [], 'tasks': []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def update_task_statuses(tasks):
    now = datetime.now()
    changed = False
    for task in tasks:
        if task.get('status') == 'Completed':
            continue
            
        try:
            deadline = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
        except ValueError:
            continue
            
        if deadline.tzinfo is None:
            deadline = deadline.astimezone()
            now_tz = datetime.now(deadline.tzinfo)
        else:
            now_tz = datetime.now(deadline.tzinfo)
            
        time_diff = deadline - now_tz
        
        # Overdue check
        if time_diff.total_seconds() < 0:
            if task.get('status') != 'Overdue':
                task['status'] = 'Overdue'
                changed = True
        # 24h reminder flag
        elif time_diff.total_seconds() <= 24 * 3600:
            if task.get('urgency_flag') != True:
                task['urgency_flag'] = True
                changed = True
        else:
            if task.get('urgency_flag') == True:
                task['urgency_flag'] = False
                changed = True
                
    return changed

def get_sorted_tasks(user_id):
    db = load_db()
    tasks = db['tasks']
    if update_task_statuses(tasks):
        save_db(db)
        
    user_tasks = [t for t in tasks if t.get('user_id') == user_id]
        
    def get_deadline(t):
        try:
            return datetime.fromisoformat(t['deadline'].replace('Z', '+00:00')).timestamp()
        except:
            return float('inf')
            
    user_tasks.sort(key=get_deadline)
    return user_tasks

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = load_db()
        user = next((u for u in db['users'] if u['username'].lower() == username.lower()), None)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = load_db()
        if any(u['username'].lower() == username.lower() for u in db['users']):
            return render_template('register.html', error="Username already exists")
            
        new_id = max([u['id'] for u in db['users']], default=0) + 1
        new_user = {
            'id': new_id,
            'username': username,
            'password': generate_password_hash(password)
        }
        db['users'].append(new_user)
        save_db(db)
        session['user_id'] = new_user['id']
        session['username'] = new_user['username']
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/cgpa')
@login_required
def cgpa():
    return render_template('cgpa.html')

@app.route('/reminder')
@login_required
def reminder():
    return render_template('reminder.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks_api():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(get_sorted_tasks(session['user_id']))

@app.route('/api/tasks', methods=['POST'])
def add_task_api():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    db = load_db()
    tasks = db['tasks']
    new_id = max([t['id'] for t in tasks], default=0) + 1
    
    if 'task_string' in data:
        task_string = data['task_string']
        parts = [p.strip() for p in task_string.split(',')]
        title = parts[0] if len(parts) > 0 else 'New Task'
        deadline = parts[1] if len(parts) > 1 else (datetime.now() + timedelta(days=1)).isoformat()
        priority = parts[2] if len(parts) > 2 else 'Normal'
        
        try:
            if len(deadline) == 10:
                deadline = datetime.strptime(deadline, "%Y-%m-%d").isoformat()
        except:
            pass

        new_task = {
            'id': new_id,
            'user_id': session['user_id'],
            'title': title,
            'deadline': deadline,
            'category': 'Study',
            'status': 'Active',
            'priority': priority,
            'urgency_flag': False
        }
    else:
        new_task = {
            'id': new_id,
            'user_id': session['user_id'],
            'title': data.get('title', ''),
            'deadline': data.get('deadline', ''),
            'category': data.get('category', 'Study'),
            'status': data.get('status', 'Active'),
            'priority': data.get('priority', 'Normal'),
            'urgency_flag': False
        }
        
    tasks.append(new_task)
    update_task_statuses(tasks)
    save_db(db)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task_api(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    db = load_db()
    tasks = db['tasks']
    for task in tasks:
        if task['id'] == task_id and task.get('user_id') == session['user_id']:
            for k, v in data.items():
                if k in task:
                    task[k] = v
            update_task_statuses(tasks)
            save_db(db)
            return jsonify(task)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task_api(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    db = load_db()
    tasks = db['tasks']
    original_len = len(tasks)
    db['tasks'] = [t for t in tasks if not (t['id'] == task_id and t.get('user_id') == session['user_id'])]
    if len(db['tasks']) < original_len:
        save_db(db)
        return '', 204
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        db = {'users': [], 'tasks': []}
        save_db(db)
    app.run(debug=True, port=8000)
