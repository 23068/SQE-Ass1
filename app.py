from flask import Flask, request, jsonify
from models import db, User, Project, Task, Comment
from utils import *
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------- User Routes ----------
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not validate_email(data.get('email', '')):
        return jsonify({'error': 'Invalid email'}), 400
    if not validate_username(data.get('username', '')):
        return jsonify({'error': 'Invalid username'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data.get('password', ''))
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'email': u.email} for u in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if 'username' in data:
        if not validate_username(data['username']):
            return jsonify({'error': 'Invalid username'}), 400
        user.username = data['username']
    if 'email' in data:
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email'}), 400
        user.email = data['email']
    db.session.commit()
    return jsonify({'message': 'User updated'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

# ---------- Project Routes ----------
@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'Name required'}), 400
    if not data.get('owner_id'):
        return jsonify({'error': 'Owner ID required'}), 400
    owner = User.query.get(data['owner_id'])
    if not owner:
        return jsonify({'error': 'Owner not found'}), 404
    project = Project(
        name=data['name'],
        description=data.get('description', ''),
        owner_id=data['owner_id'],
        deadline=parse_date(data.get('deadline', ''))
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({'id': project.id, 'name': project.name}), 201

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'owner_id': p.owner_id} for p in projects])

@app.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'owner_id': project.owner_id,
        'deadline': format_date(project.deadline),
        'is_completed': project.is_completed
    })

@app.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'deadline' in data:
        project.deadline = parse_date(data['deadline'])
    if 'is_completed' in data:
        project.is_completed = data['is_completed']
    db.session.commit()
    return jsonify({'message': 'Project updated'})

@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted'})

# ---------- Task Routes ----------
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    errors = validate_task_data(data)
    if errors:
        return jsonify({'errors': errors}), 400
    if not data.get('project_id'):
        return jsonify({'error': 'Project ID required'}), 400
    project = Project.query.get(data['project_id'])
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        project_id=data['project_id'],
        assignee_id=data.get('assignee_id'),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        due_date=parse_date(data.get('due_date', ''))
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'id': task.id, 'title': task.title}), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'status': t.status,
        'priority': t.priority,
        'project_id': t.project_id
    } for t in tasks])

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'project_id': task.project_id,
        'assignee_id': task.assignee_id,
        'due_date': format_date(task.due_date),
        'created_at': format_date(task.created_at)
    })

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        if data['status'] not in ['pending', 'in_progress', 'completed']:
            return jsonify({'error': 'Invalid status'}), 400
        task.status = data['status']
        if data['status'] == 'completed':
            task.completed_at = datetime.utcnow()
    if 'priority' in data:
        if data['priority'] not in ['high', 'medium', 'low']:
            return jsonify({'error': 'Invalid priority'}), 400
        task.priority = data['priority']
    if 'assignee_id' in data:
        task.assignee_id = data['assignee_id']
    if 'due_date' in data:
        task.due_date = parse_date(data['due_date'])
    db.session.commit()
    return jsonify({'message': 'Task updated'})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})

# ---------- Comment Routes ----------
@app.route('/tasks/<int:task_id>/comments', methods=['POST'])
def create_comment(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    if not data.get('content'):
        return jsonify({'error': 'Content required'}), 400
    if not data.get('author_id'):
        return jsonify({'error': 'Author ID required'}), 400
    author = User.query.get(data['author_id'])
    if not author:
        return jsonify({'error': 'Author not found'}), 404
    comment = Comment(
        content=data['content'],
        task_id=task_id,
        author_id=data['author_id']
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({'id': comment.id, 'content': comment.content}), 201

@app.route('/tasks/<int:task_id>/comments', methods=['GET'])
def get_comments(task_id):
    task = Task.query.get_or_404(task_id)
    comments = Comment.query.filter_by(task_id=task_id).all()
    return jsonify([{
        'id': c.id,
        'content': c.content,
        'author_id': c.author_id,
        'created_at': format_date(c.created_at)
    } for c in comments])

# ---------- Analytics Routes ----------
@app.route('/analytics/tasks/summary', methods=['GET'])
def task_summary():
    tasks = Task.query.all()
    task_dicts = [{'status': t.status, 'priority': t.priority} for t in tasks]
    return jsonify(get_task_summary(task_dicts))

@app.route('/analytics/projects/<int:project_id>/completion', methods=['GET'])
def project_completion(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).all()
    task_dicts = [{'status': t.status} for t in tasks]
    return jsonify({'completion_percentage': calculate_completion_percentage(task_dicts)})

@app.route('/analytics/users/<int:user_id>/tasks', methods=['GET'])
def user_tasks(user_id):
    user = User.query.get_or_404(user_id)
    tasks = Task.query.filter_by(assignee_id=user_id).all()
    return jsonify([{'id': t.id, 'title': t.title, 'status': t.status} for t in tasks])

if __name__ == '__main__':
    app.run(debug=True)
