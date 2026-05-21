from flask import Blueprint, jsonify, request, session

from app.routes.auth import login_required, role_required
from app.services import progress_service

progress_bp = Blueprint('progress', __name__)


@progress_bp.route('/api/progress/summary', methods=['GET'])
@login_required
def progress_summary():
    user_id = session['user_id']
    if session.get('role') == 'parent':
        return jsonify({
            'success': True,
            'role': 'parent',
            'children': progress_service.get_parent_children(user_id),
        })
    return jsonify({
        'success': True,
        'role': 'student',
        'summary': progress_service.get_student_summary(user_id),
    })


@progress_bp.route('/api/progress/history', methods=['GET'])
@login_required
@role_required('student')
def progress_history():
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        'success': True,
        'history': progress_service.get_screening_history(session['user_id'], limit),
    })


@progress_bp.route('/api/progress/event', methods=['POST'])
@login_required
def progress_event():
    data = request.get_json() or {}
    event_type = data.get('event_type', 'generic')
    progress_service.record_progress_event(
        session['user_id'], event_type, data.get('payload', data)
    )
    return jsonify({'success': True})
