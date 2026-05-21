import secrets
import string

from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User
from app.mongo import get_db, parse_object_id, utcnow


def _generate_link_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    db = get_db()
    for _ in range(20):
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        if not db.users.find_one({'link_code': code}):
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

    db = get_db()
    if db.users.find_one({'username': username}):
        return None, 'Username already taken.'
    if db.users.find_one({'email': email}):
        return None, 'Email already registered.'

    doc = User.new_document(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        display_name=display_name or username,
        link_code=_generate_link_code() if role == 'student' else None,
    )
    try:
        result = db.users.insert_one(doc)
    except DuplicateKeyError:
        return None, 'Username or email already registered.'
    doc['_id'] = result.inserted_id
    return User(doc), None


def authenticate(username, password):
    username = (username or '').strip().lower()
    doc = get_db().users.find_one({'username': username})
    if doc and check_password_hash(doc['password_hash'], password):
        return User(doc)
    return None


def link_parent_to_child(parent_id, link_code):
    link_code = (link_code or '').strip().upper()
    db = get_db()
    child_doc = db.users.find_one({'link_code': link_code, 'role': 'student'})
    if not child_doc:
        return None, 'Invalid link code. Check the code from your child\'s profile.'

    child = User(child_doc)
    parent_oid = parse_object_id(parent_id)
    child_oid = parse_object_id(child.id)
    if not parent_oid or not child_oid:
        return None, 'Invalid account.'

    existing = db.parent_child_links.find_one({
        'parent_id': parent_oid,
        'child_id': child_oid,
    })
    if existing:
        return child, None

    try:
        db.parent_child_links.insert_one({
            'parent_id': parent_oid,
            'child_id': child_oid,
            'linked_at': utcnow(),
        })
    except DuplicateKeyError:
        pass
    return child, None


def get_user_by_id(user_id):
    oid = parse_object_id(user_id)
    if not oid:
        return None
    doc = get_db().users.find_one({'_id': oid})
    return User(doc) if doc else None
