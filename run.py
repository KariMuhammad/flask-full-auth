# run.py
from main import create_app
from extensions import db
from flask_migrate import Migrate, upgrade

app = create_app()
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()
    upgrade()