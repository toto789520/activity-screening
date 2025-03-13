from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string
import qrcode
import netifaces

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

def generate_code():
    data = ("http://"+get_local_ip()+":5000/enter_code")
    # Generate QR code
    qr = qrcode.make(data)
    # Save the QR code as an image file
    return qr

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    progress = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(6), unique=True, nullable=False, default=generate_code)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.before_request
def generate_qr_code():
    if not hasattr(app, 'qr_code_generated'):
        with app.app_context():
            url = url_for('enter_code', _external=True)
            img = qrcode.make(url)
            img.save('static/qr_code.png')
            app.qr_code_generated = True

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        task = request.form['task']
        progress = request.form['progress']
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        new_task = Task(name=name, task=task, progress=progress, code=code)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.name = request.form['name']
        task.task = request.form['task']
        task.progress = request.form['progress']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/live')
def live():
    tasks = Task.query.all()
    return render_template('live.html', tasks=tasks)

@app.route('/tasks')
def get_tasks():
    tasks = Task.query.all()
    tasks_list = [{'name': task.name, 'task': task.task, 'progress': task.progress, 'code': task.code, 'created_at': task.created_at} for task in tasks]
    return jsonify(tasks_list)

@app.route('/update_progress/<string:code>', methods=['POST'])
def update_progress(code):
    task = Task.query.filter_by(code=code).first_or_404()
    task.progress = request.form['progress']
    db.session.commit()
    return redirect(url_for('confirmation'))

@app.route('/enter_code', methods=['GET', 'POST'])
def enter_code():
    if request.method == 'POST':
        code = request.form['code']
        return redirect(url_for('update_progress_page', code=code))
    return render_template('enter_code.html')

@app.route('/update_progress/<string:code>', methods=['GET', 'POST'])
def update_progress_page(code):
    task = Task.query.filter_by(code=code).first_or_404()
    if request.method == 'POST':
        task.progress = request.form['progress']
        db.session.commit()
        return redirect(url_for('confirmation'))
    return render_template('update_progress.html', task=task)

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

if __name__ == '__main__':
    print(get_local_ip())
    print("server running")
    app.run(host=get_local_ip(), port=5000, debug=True)
