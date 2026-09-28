from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(500))
    bio = db.Column(db.Text, default='')
    interests = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    skills = db.relationship('Skill', backref='user', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', cascade='all, delete-orphan')
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_name = db.Column(db.String(120), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    current_level = db.Column(db.String(30), default='BEGINNER')
    target_level = db.Column(db.String(30), default='INTERMEDIATE')
    start_date = db.Column(db.Date)
    target_date = db.Column(db.Date)
    status = db.Column(db.String(30), default='ACTIVE', index=True)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, default=0)
    unit = db.Column(db.String(40), default='hours')
    deadline = db.Column(db.Date)
    status = db.Column(db.String(30), default='ACTIVE')

class Milestone(db.Model):
    __tablename__ = 'milestones'
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    target_value = db.Column(db.Float, nullable=False)
    achieved = db.Column(db.Boolean, default=False)
    achieved_at = db.Column(db.DateTime)

class PracticeSession(db.Model):
    __tablename__ = 'practice_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False, index=True)
    duration_minutes = db.Column(db.Integer, nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, default='')
    practiced_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'))
    content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='uq_like_post_user'),)

class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='uq_follow_pair'),)

class FileAsset(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    object_key = db.Column(db.String(500), nullable=False, unique=True)
    original_name = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(20), default='private')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
