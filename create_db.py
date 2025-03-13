from app import app, db

# Add this line to suppress the FSADeprecationWarning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    db.create_all()
