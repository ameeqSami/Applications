from flask import Flask, render_template
import requests

app = Flask(__name__)

def fetch_github_repos():
    try:
        response = requests.get('https://api.github.com/users/ameeqSami/repos?sort=updated&per_page=6', timeout=5)
        response.raise_for_status()
        repos = response.json()
        
        # Format the repos to match the expected structure in the template
        projects = []
        for repo in repos:
            # Skip forks or choose what to include
            if not repo.get('fork'):
                projects.append({
                    'title': repo.get('name'),
                    'description': repo.get('description') or 'No description provided.',
                    'tech_stack': repo.get('language') or 'Mixed',
                    'url': repo.get('html_url')
                })
        return projects[:6] # Return top 6
    except Exception as e:
        print(f"Error fetching GitHub repos: {e}")
        # Fallback to empty list
        return []

POSTS = [
    {
        'title': 'My First Blog Post',
        'content': 'This is the content of my first blog post. Welcome to my portfolio!',
        'date': '2026-05-02'
    }
]

def fetch_github_activity():
    try:
        # Using 'octocat' as a sample active GitHub user, you can change this to your username!
        response = requests.get('https://api.github.com/users/ameeqSami/events', timeout=5)
        response.raise_for_status()
        events = response.json()
        return events[:3] if events else []
    except Exception as e:
        print(f"Error fetching GitHub activity: {e}")
        return []

@app.route('/')
def index():
    projects = fetch_github_repos()
    github_events = fetch_github_activity()
    return render_template('index.html', projects=projects, posts=POSTS, github_events=github_events)

if __name__ == '__main__':
    app.run(debug=True)
