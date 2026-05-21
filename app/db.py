from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    import os

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        import app.models  # noqa: F401 — register models with SQLAlchemy
        db.create_all()
