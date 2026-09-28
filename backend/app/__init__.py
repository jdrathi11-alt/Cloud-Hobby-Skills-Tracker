import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-only-change-me'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///hobby_tracker.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=int(os.getenv('MAX_UPLOAD_BYTES', 5 * 1024 * 1024)),
        UPLOAD_FOLDER=os.getenv('UPLOAD_FOLDER', os.path.join(app.instance_path, 'uploads')),
    SUPABASE_URL=os.getenv('SUPABASE_URL'),
    SUPABASE_SERVICE_ROLE_KEY=os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
    SUPABASE_BUCKET=os.getenv('SUPABASE_BUCKET', 'uploads'),
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.init_app(app)
    CORS(app, resources={r'/api/*': {'origins': os.getenv('FRONTEND_ORIGIN', '*')}})
    from .models.models import User, Skill, Goal, Milestone, PracticeSession, Post, Comment, Like, Follow, FileAsset
    from .routes.api import api
    app.register_blueprint(api, url_prefix='/api')
    @app.get('/health')
    def health():
        return {'status': 'ok', 'service': 'cloud-hobby-skills-tracker'}
    with app.app_context():
        db.create_all()
    return app
