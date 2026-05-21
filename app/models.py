from datetime import datetime

from app.db import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student | parent
    display_name = db.Column(db.String(120), nullable=False)
    link_code = db.Column(db.String(12), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    preferences = db.relationship(
        'UserPreferences', backref='user', uselist=False, cascade='all, delete-orphan'
    )
    screening_results = db.relationship(
        'ScreeningResult', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )
    progress_events = db.relationship(
        'ProgressEvent', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )

    def to_dict(self, include_link_code=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'display_name': self.display_name,
        }
        if include_link_code and self.link_code:
            data['link_code'] = self.link_code
        return data


class ParentChildLink(db.Model):
    __tablename__ = 'parent_child_links'
    __table_args__ = (db.UniqueConstraint('parent_id', 'child_id', name='uq_parent_child'),)

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    child_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    linked_at = db.Column(db.DateTime, default=datetime.utcnow)

    parent = db.relationship('User', foreign_keys=[parent_id], backref='children_links')
    child = db.relationship('User', foreign_keys=[child_id], backref='parent_links')


class ScreeningResult(db.Model):
    __tablename__ = 'screening_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    overall_score = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.Integer, nullable=False)
    component_scores = db.Column(db.JSON, nullable=True)
    recommendations = db.Column(db.JSON, nullable=True)
    feature_importance = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class ProgressEvent(db.Model):
    __tablename__ = 'progress_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    payload = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    font_size = db.Column(db.Integer, default=16)
    dyslexic_font = db.Column(db.Boolean, default=False)
    high_contrast = db.Column(db.Boolean, default=False)
    read_aloud = db.Column(db.Boolean, default=False)
