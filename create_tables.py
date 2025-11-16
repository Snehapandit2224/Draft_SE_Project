from app import create_app, db

app = create_app('development')

with app.app_context():
    # Create all tables from models
    db.create_all()
    print('Tables created (if not present).')
