import secrets
import string

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import db
from app.models import ParentChildLink, User, UserPreferences


def _generate_link_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        if not User.query.filter_by(link_code=code).first():
            return code
    return secrets.token_hex(4).upper()


def register_user(username, email, password, role, display_name):
    username = (username or '').strip().lower()
    email = (email or '').strip().lower()
    display_name = (display_name or username or '').strip()
    role = (role or 'student').strip().lower()

    if role not in ('student', 'parent'):
        return None, 'Invalid role. Choose student or parent.'
    if len(username) < 3:
        return None, 'Username must be at least 3 characters.'
    if len(password) < 6:
        return None, 'Password must be at least 6 characters.'
    if User.query.filter_by(username=username).first():
        return None, 'Username already taken.'
    if User.query.filter_by(email=email).first():
        return None, 'Email already registered.'

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        display_name=display_name or username,
        link_code=_generate_link_code() if role == 'student' else None,
    )
    db.session.add(user)
    db.session.flush()
    db.session.add(UserPreferences(user_id=user.id))
    db.session.commit()
    return user, None


def authenticate(username, password):
    username = (username or '').strip().lower()
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None


def link_parent_to_child(parent_id, link_code):
    link_code = (link_code or '').strip().upper()
    child = User.query.filter_by(link_code=link_code, role='student').first()
    if not child:
        return None, 'Invalid link code. Check the code from your child\'s profile.'

    existing = ParentChildLink.query.filter_by(
        parent_id=parent_id, child_id=child.id
    ).first()
    if existing:
        return child, None

    db.session.add(ParentChildLink(parent_id=parent_id, child_id=child.id))
    db.session.commit()
    return child, None


def get_user_by_id(user_id):
    return User.query.get(user_id)
