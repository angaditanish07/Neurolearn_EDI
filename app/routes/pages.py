from flask import Blueprint, redirect, render_template, request, session, url_for

from app.routes.auth import login_required

pages_bp = Blueprint('pages', __name__)


def _require_student_page(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('pages.login', next=request.path))
        if session.get('role') == 'parent':
            return redirect(url_for('parent.parent_dashboard_page'))
        return f(*args, **kwargs)
    return wrapped


@pages_bp.route('/')
@login_required
def index():
    if session.get('role') == 'parent':
        return redirect(url_for('parent.parent_dashboard_page'))
    return render_template('index.html')


@pages_bp.route('/interactive_learning')
@_require_student_page
def interactive_model():
    return render_template('interactive_model.html')


@pages_bp.route('/dyslexia_screening')
@_require_student_page
def dyslexia_screening():
    return render_template('dyslexia_screening.html')


@pages_bp.route('/dyslexia_screening_redirect')
def dyslexia_screening_redirect():
    return redirect(url_for('pages.dyslexia_screening'))


@pages_bp.route('/login')
def login():
    if session.get('user_id'):
        if session.get('role') == 'parent':
            return redirect(url_for('parent.parent_dashboard_page'))
        return redirect(url_for('pages.index'))
    return render_template('login.html', next_url=request.args.get('next', '/'))


@pages_bp.route('/register')
def register():
    if session.get('user_id'):
        return redirect(url_for('pages.index'))
    return render_template('register.html')


@pages_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@pages_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@pages_bp.route('/help')
def help_page():
    return render_template('help.html')
