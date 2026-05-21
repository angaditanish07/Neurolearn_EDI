import logging
from functools import wraps

from flask import Blueprint, jsonify, redirect, request, session, url_for

from app.services import auth_service

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('pages.login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapped(*args, **kwargs):
            if session.get('role') not in roles:
                return jsonify({'success': False, 'error': 'Forbidden'}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator


def _set_session(user):
    session['user_id'] = user.id
    session['role'] = user.role
    session['display_name'] = user.display_name
    session['username'] = user.username
    session.modified = True


@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    user, err = auth_service.register_user(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password'),
        role=data.get('role', 'student'),
        display_name=data.get('display_name'),
    )
    if err:
        return jsonify({'success': False, 'error': err}), 400
    _set_session(user)
    return jsonify({
        'success': True,
        'user': user.to_dict(include_link_code=True),
    })


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = auth_service.authenticate(
        data.get('username'), data.get('password')
    )
    if not user:
        return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
    _set_session(user)
    return jsonify({
        'success': True,
        'user': user.to_dict(include_link_code=(user.role == 'student')),
    })


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@auth_bp.route('/api/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    user = auth_service.get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    return jsonify({
        'success': True,
        'user': user.to_dict(include_link_code=(user.role == 'student')),
    })


@auth_bp.route('/api/parent/link-child', methods=['POST'])
@role_required('parent')
def link_child():
    data = request.get_json() or {}
    child, err = auth_service.link_parent_to_child(
        session['user_id'], data.get('link_code')
    )
    if err:
        return jsonify({'success': False, 'error': err}), 400
    return jsonify({
        'success': True,
        'child': child.to_dict(),
        'message': f'Linked to {child.display_name}',
    })
