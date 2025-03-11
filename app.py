from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    progress = db.Column(db.Integer, nullable=False)

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
        new_task = Task(name=name, task=task, progress=progress)
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
    tasks_list = [{'name': task.name, 'task': task.task, 'progress': task.progress} for task in tasks]
    return jsonify(tasks_list)

if __name__ == '__main__':
    app.run(debug=True)
