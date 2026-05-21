from flask import Blueprint, jsonify, render_template, request, session

from app.routes.auth import login_required, role_required
from app.services import progress_service

parent_bp = Blueprint('parent', __name__)


@parent_bp.route('/parent/dashboard')
@login_required
@role_required('parent')
def parent_dashboard_page():
    return render_template('parent_dashboard.html')


@parent_bp.route('/api/parent/children', methods=['GET'])
@login_required
@role_required('parent')
def parent_children():
    return jsonify({
        'success': True,
        'children': progress_service.get_parent_children(session['user_id']),
    })


@parent_bp.route('/api/parent/child/<child_id>/summary', methods=['GET'])
@login_required
@role_required('parent')
def parent_child_summary(child_id):
    data = progress_service.get_child_summary_for_parent(session['user_id'], child_id)
    if not data:
        return jsonify({'success': False, 'error': 'Child not found or not linked'}), 403
    return jsonify({'success': True, **data})
