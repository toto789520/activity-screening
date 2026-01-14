from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string
import qrcode
import netifaces
import os
import sqlite3
import shlex
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
# Add this line to suppress the FSADeprecationWarning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def get_local_ip():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for address in addresses[netifaces.AF_INET]:
                local_ip = address['addr']
                print(f"L'adresse IP locale sur l'interface {interface} est : {local_ip}")
                return local_ip

def generate_code(code):
    qrcodetack = qrcode.make(f"http://{get_local_ip()}:5000/task/{code}")
    qrcodetack.save(f"static/qr_codes/{code}.png")

def recreate_qr_codes():
    tasks = Task.query.all()
    for task in tasks:
        generate_code(task.code)

task_users = db.Table('task_users',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

subtask_users = db.Table('subtask_users',
    db.Column('subtask_id', db.Integer, db.ForeignKey('sub_task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class SubTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    progress = db.Column(db.Integer, nullable=False, default=0)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    users = db.relationship('User', secondary=subtask_users, lazy='subquery',
        backref=db.backref('subtasks', lazy=True))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    progress = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(6), unique=True, nullable=False, default=generate_code)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    users = db.relationship('User', secondary=task_users, lazy='subquery',
        backref=db.backref('tasks', lazy=True))
    subtasks = db.relationship('SubTask', backref='task', lazy=True)
    image = db.Column(db.String(150))

    def calculate_global_progress(self):
        if not self.users:
            return 0
        total_progress = sum(user.get_task_progress(self.id) for user in self.users)
        return total_progress // len(self.users)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    progress = db.Column(db.Integer, nullable=False, default=0)

    def get_task_progress(self, task_id):
        task_progress = TaskUserProgress.query.filter_by(user_id=self.id, task_id=task_id).first()
        return task_progress.progress if task_progress else 0

class TaskUserProgress(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
    progress = db.Column(db.Integer, nullable=False, default=0)

class SubTaskUserProgress(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    subtask_id = db.Column(db.Integer, db.ForeignKey('sub_task.id'), primary_key=True)
    progress = db.Column(db.Integer, nullable=False, default=0)

class AvailableTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        class_name = request.form['class_name']
        new_user = User(first_name=first_name, last_name=last_name, email=email, class_name=class_name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('users'))
    return render_template('add_user.html')

@app.route('/add_ticket', methods=['GET', 'POST'])
def add_ticket():
    if request.method == 'POST':
        title = request.form['title']
        image = request.form['image']
        description = request.form['description']
        new_ticket = AvailableTicket(title=title, image=image, description=description)
        db.session.add(new_ticket)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_ticket.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    users = User.query.all()
    tickets = AvailableTicket.query.all()
    if request.method == 'POST':
        name = request.form['name']
        task = request.form['task']
        user_ids = request.form.getlist('users')
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        image = request.form.get('image', '')  # Utiliser une chaîne vide par défaut si 'image' n'est pas présent
        new_task = Task(name=name, task=task, progress=0, code=code, image=image)
        for user_id in user_ids:
            user = User.query.get(user_id)
            new_task.users.append(user)
            subtask_data = request.form.get(f'subtasks_{user_id}')
            if subtask_data and ',' in subtask_data:
                try:
                    subtask_name, subtask_progress = subtask_data.split(',', 1)
                    subtask = SubTask(name=subtask_name.strip(), progress=int(subtask_progress.strip()), task=new_task)
                    new_task.subtasks.append(subtask)
                    print(f"Subtask added: {subtask_name} with progress {subtask_progress}")
                except ValueError:
                    print(f"Invalid subtask data for user {user_id}: {subtask_data}")
        db.session.add(new_task)
        db.session.commit()
        generate_code(code)
        # Annoncer automatiquement le ticket
        safe_name = shlex.quote(name)
        os.system(f'say "Nouveau ticket disponible: {safe_name}"')
        return redirect(url_for('index'))
    return render_template('add.html', users=users, tickets=tickets)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    users = User.query.all()
    if request.method == 'POST':
        task.name = request.form['name']
        task.task = request.form['task']
        user_ids = request.form.getlist('users')
        task.users = []
        task.subtasks = []  # Clear existing subtasks to avoid duplicates
        for user_id in user_ids:
            user = User.query.get(user_id)
            task.users.append(user)
            subtask_data = request.form.get(f'subtasks_{user_id}')
            if subtask_data and ',' in subtask_data:
                try:
                    subtask_name, subtask_progress = subtask_data.split(',', 1)
                    subtask = SubTask(name=subtask_name.strip(), progress=int(subtask_progress.strip()), task=task)
                    task.subtasks.append(subtask)
                    print(f"Subtask updated: {subtask_name} with progress {subtask_progress}")
                except ValueError:
                    print(f"Invalid subtask data for user {user_id}: {subtask_data}")
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', task=task, users=users)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    print("delete")
    print(id)
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('available_tickets'))
    return render_template('delete.html', task=task)

@app.route('/live')
def live():
    tasks = Task.query.all()
    tasks_with_user_progress = []
    for task in tasks:
        task_info = {
            'name': task.name,
            'task': task.task,
            'progress': task.progress,
            'global_progress': task.calculate_global_progress(),
            'users': [
                {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'progress': user.get_task_progress(task.id),
                    'subtasks': [
                        {'name': subtask.name, 'progress': subtask.progress}
                        for subtask in task.subtasks if user in subtask.users
                    ]
                }
                for user in task.users
            ],
            'image': task.image
        }
        tasks_with_user_progress.append(task_info)
    return render_template('live.html', tasks=tasks_with_user_progress)

@app.route('/tasks')
def get_tasks():
    tasks = Task.query.all()
    tasks_list = [{'name': task.name, 'task': task.task, 'progress': task.progress, 'global_progress': task.calculate_global_progress(), 'created_at': task.created_at, 'code': task.code, 'users': [{'first_name': user.first_name, 'last_name': user.last_name, 'class_name': user.class_name, 'progress': user.get_task_progress(task.id), 'subtasks': [{'name': subtask.name, 'progress': subtask.progress} for subtask in user.subtasks if subtask.task_id == task.id]} for user in task.users], 'image': task.image} for task in tasks]
    return jsonify(tasks_list)

@app.route('/update_progress/<string:code>', methods=['POST'])
def update_progress(code):
    task = Task.query.filter_by(code=code).first_or_404()
    user_id = request.form['user_id']
    progress = request.form['progress']
    # Mettre à jour la progression de l'utilisateur pour cette tâche
    task_user_progress = TaskUserProgress.query.filter_by(user_id=user_id, task_id=task.id).first()
    if task_user_progress:
        task_user_progress.progress = progress
    else:
        new_progress = TaskUserProgress(user_id=user_id, task_id=task.id, progress=progress)
        db.session.add(new_progress)
    db.session.commit()
    return redirect(url_for('confirmation'))

@app.route('/enter_code', methods=['GET', 'POST'])
def enter_code():
    if request.method == 'POST':
        code = request.form['code']
        return redirect(url_for('update_progress_page', code=code))
    return render_template('enter_code.html')

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

@app.route('/users')
def users():
    users = User.query.order_by(User.class_name).all()
    return render_template('users.html', users=users)

@app.route('/available_tickets')
def available_tickets():
    tickets = AvailableTicket.query.all()
    return render_template('available_tickets.html', tickets=tickets)

@app.route('/announce_ticket/<int:id>')
def announce_ticket(id):
    ticket = AvailableTicket.query.get_or_404(id)
    # Code pour annoncer le ticket via les haut-parleurs
    os.system(f'say "Nouveau ticket disponible: {ticket.title}"')
    return redirect(url_for('available_tickets'))

@app.route('/delete_ticket/<int:id>', methods=['POST'])
def delete_ticket(id):
    ticket = AvailableTicket.query.get_or_404(id)
    db.session.delete(ticket)
    db.session.commit()
    return redirect(url_for('available_tickets'))

@app.route('/edit_ticket/<int:id>', methods=['GET', 'POST'])
def edit_ticket(id):
    ticket = AvailableTicket.query.get_or_404(id)
    if request.method == 'POST':
        # Ensure the form contains the required fields
        ticket.title = request.form.get('title', ticket.title)
        ticket.image = request.form.get('image', ticket.image)
        ticket.description = request.form.get('description', ticket.description)
        db.session.commit()
        return redirect(url_for('available_tickets'))
    # Render the edit_ticket.html template for GET requests
    return render_template('edit_ticket.html', ticket=ticket)

@app.route('/task/<string:code>')
def task_page(code):
    task = Task.query.filter_by(code=code).first_or_404()
    users = User.query.all()
    return render_template('task_page.html', task=task, users=users)

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.class_name = request.form['class_name']
        db.session.commit()
        return redirect(url_for('users'))
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users'))

if __name__ == '__main__':
    with app.app_context():
        recreate_qr_codes()
    print(get_local_ip())
    print("server running")
    app.run(host=get_local_ip(), port=5000, debug=True)
