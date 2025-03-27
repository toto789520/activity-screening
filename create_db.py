from app import app, db, get_local_ip
from app import User, AvailableTicket, Task, SubTask, TaskUserProgress, SubTaskUserProgress  # Importer les modèles User, AvailableTicket, Task, SubTask, TaskUserProgress, SubTaskUserProgress
import qrcode
import os


# Add this line to suppress the FSADeprecationWarning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    # Créer la base de données
    db.create_all()
    

    # Ajouter des utilisateurs et des tickets disponibles pour les tests
    if not User.query.first():
        user1 = User(first_name='John', last_name='Doe', email='john.doe@example.com', class_name='Classe A')
        user2 = User(first_name='Jane', last_name='Smith', email='jane.smith@example.com', class_name='Classe B')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
    if not AvailableTicket.query.first():
        ticket1 = AvailableTicket(
            title='Ticket 1', 
            image='static/ticket1.png', 
            description='Description du ticket 1'
        )
        ticket2 = AvailableTicket(
            title='Ticket 2', 
            image='static/ticket2.png', 
            description='Description du ticket 2'
        )
        db.session.add(ticket1)
        db.session.add(ticket2)
        db.session.commit()
<<<<<<< Updated upstream

    # Validate 'title' key when processing tasks
=======
    if not Task.query.first():
        task1 = Task(name='Tâche 1', task='Description de la tâche 1', progress=0, code='ABC123', image='static/task1.png')
        user1 = User.query.filter_by(first_name='John').first()
        subtask1 = SubTask(name='Sous-tâche 1', progress=50, task=task1)
        subtask1.users.append(user1)
        db.session.add(task1)
        db.session.commit()
        print("Task and subtask added for testing.")
    # Générer un QR code pour chaque tâche
>>>>>>> Stashed changes
    tasks = Task.query.all()
    for task in tasks:
        if not task.title:
            raise ValueError("Task is missing a 'title' key.")
        qr = qrcode.make(f"http://{get_local_ip()}:5000/task/{task.code}")
        qr.save(os.path.join('static', 'qr_codes', f'{task.code}.png'))
