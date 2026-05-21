from datetime import datetime, timedelta

from app.db import db
from app.models import ParentChildLink, ProgressEvent, ScreeningResult, User


def save_screening_result(user_id, overall_score, risk_level, component_scores,
                          recommendations, feature_importance=None):
    row = ScreeningResult(
        user_id=user_id,
        overall_score=float(overall_score),
        risk_level=int(risk_level),
        component_scores=component_scores or {},
        recommendations=recommendations or [],
        feature_importance=feature_importance or {},
    )
    db.session.add(row)
    record_progress_event(user_id, 'dyslexia_screening', {
        'overall_score': overall_score,
        'risk_level': risk_level,
    })
    db.session.commit()
    return row


def record_progress_event(user_id, event_type, payload=None):
    event = ProgressEvent(
        user_id=user_id,
        event_type=event_type,
        payload=payload or {},
    )
    db.session.add(event)
    db.session.commit()
    return event


def _compute_streak(user_id):
    events = (
        ProgressEvent.query.filter_by(user_id=user_id)
        .order_by(ProgressEvent.created_at.desc())
        .limit(200)
        .all()
    )
    if not events:
        return 0
    days = set()
    for e in events:
        if e.created_at:
            days.add(e.created_at.date())
    if not days:
        return 0
    streak = 0
    day = datetime.utcnow().date()
    while day in days:
        streak += 1
        day -= timedelta(days=1)
    return streak


def get_student_summary(user_id):
    latest = (
        ScreeningResult.query.filter_by(user_id=user_id)
        .order_by(ScreeningResult.created_at.desc())
        .first()
    )
    screening_count = ScreeningResult.query.filter_by(user_id=user_id).count()
    event_count = ProgressEvent.query.filter_by(user_id=user_id).count()

    component_scores = {}
    recommendations = []
    overall_score = None
    risk_level = None
    if latest:
        component_scores = latest.component_scores or {}
        recommendations = latest.recommendations or []
        overall_score = latest.overall_score
        risk_level = latest.risk_level

    path_progress = {
        'interactive': _path_percent(user_id, 'module_visit', 'interactive'),
        'dyslexia': min(100, screening_count * 50),
        'games': _path_percent(user_id, 'interactive_fingers', 'games'),
    }

    return {
        'streak': _compute_streak(user_id),
        'lessons_completed': screening_count + max(0, event_count // 5),
        'skills_mastered': len([k for k, v in (component_scores or {}).items() if v >= 0.75]),
        'screening_count': screening_count,
        'latest_screening': {
            'overall_score': overall_score,
            'risk_level': risk_level,
            'component_scores': component_scores,
            'recommendations': recommendations,
            'created_at': latest.created_at.isoformat() if latest and latest.created_at else None,
        } if latest else None,
        'path_progress': path_progress,
        'component_scores': component_scores,
        'recommendations': recommendations,
    }


def _path_percent(user_id, event_type, key):
    count = ProgressEvent.query.filter_by(
        user_id=user_id, event_type=event_type
    ).count()
    if key == 'interactive':
        return min(100, 20 + count * 15)
    return min(100, count * 25)


def get_screening_history(user_id, limit=10):
    rows = (
        ScreeningResult.query.filter_by(user_id=user_id)
        .order_by(ScreeningResult.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            'id': r.id,
            'overall_score': r.overall_score,
            'risk_level': r.risk_level,
            'component_scores': r.component_scores,
            'recommendations': r.recommendations,
            'created_at': r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


def get_parent_children(parent_id):
    links = ParentChildLink.query.filter_by(parent_id=parent_id).all()
    children = []
    for link in links:
        child = User.query.get(link.child_id)
        if child:
            summary = get_student_summary(child.id)
            children.append({
                'id': child.id,
                'display_name': child.display_name,
                'username': child.username,
                'linked_at': link.linked_at.isoformat() if link.linked_at else None,
                'summary': summary,
            })
    return children


def get_child_summary_for_parent(parent_id, child_id):
    link = ParentChildLink.query.filter_by(
        parent_id=parent_id, child_id=child_id
    ).first()
    if not link:
        return None
    child = User.query.get(child_id)
    if not child:
        return None
    return {
        'child': child.to_dict(),
        'summary': get_student_summary(child_id),
        'history': get_screening_history(child_id, limit=10),
    }


def parent_owns_child(parent_id, child_id):
    return ParentChildLink.query.filter_by(
        parent_id=parent_id, child_id=child_id
    ).first() is not None
