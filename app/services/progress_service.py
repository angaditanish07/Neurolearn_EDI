from datetime import timedelta

from app.models import ProgressEvent, ScreeningResult, User
from app.mongo import get_db, parse_object_id, utcnow


def save_screening_result(user_id, overall_score, risk_level, component_scores,
                          recommendations, feature_importance=None):
    db = get_db()
    doc = ScreeningResult.new_document(
        user_id, overall_score, risk_level, component_scores,
        recommendations, feature_importance,
    )
    result = db.screening_results.insert_one(doc)
    doc['_id'] = result.inserted_id
    record_progress_event(user_id, 'dyslexia_screening', {
        'overall_score': overall_score,
        'risk_level': risk_level,
    })
    return ScreeningResult(doc)


def record_progress_event(user_id, event_type, payload=None):
    db = get_db()
    doc = ProgressEvent.new_document(user_id, event_type, payload)
    result = db.progress_events.insert_one(doc)
    doc['_id'] = result.inserted_id
    return ProgressEvent(doc)


def _user_oid(user_id):
    return parse_object_id(user_id)


def _compute_streak(user_id):
    oid = _user_oid(user_id)
    if not oid:
        return 0
    events = list(
        get_db().progress_events.find({'user_id': oid})
        .sort('created_at', -1)
        .limit(200)
    )
    if not events:
        return 0
    days = set()
    for e in events:
        created = e.get('created_at')
        if created:
            days.add(created.date())
    if not days:
        return 0
    streak = 0
    day = utcnow().date()
    while day in days:
        streak += 1
        day -= timedelta(days=1)
    return streak


def get_student_summary(user_id):
    db = get_db()
    oid = _user_oid(user_id)
    if not oid:
        return _empty_summary()

    latest_doc = db.screening_results.find_one(
        {'user_id': oid},
        sort=[('created_at', -1)],
    )
    latest = ScreeningResult(latest_doc) if latest_doc else None
    screening_count = db.screening_results.count_documents({'user_id': oid})
    event_count = db.progress_events.count_documents({'user_id': oid})

    component_scores = {}
    recommendations = []
    overall_score = None
    risk_level = None
    if latest:
        component_scores = latest.component_scores
        recommendations = latest.recommendations
        overall_score = latest.overall_score
        risk_level = latest.risk_level

    path_progress = {
        'interactive': _path_percent(user_id, 'module_visit', 'interactive'),
        'dyslexia': min(100, screening_count * 50),
        'games': _path_percent(user_id, 'interactive_fingers', 'games'),
    }

    last_doc = db.progress_events.find_one(
        {'user_id': oid},
        sort=[('created_at', -1)],
    )
    last_active = None
    if last_doc and last_doc.get('created_at'):
        last_active = last_doc['created_at'].isoformat()

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
        'last_active': last_active,
    }


def _empty_summary():
    return {
        'streak': 0,
        'lessons_completed': 0,
        'skills_mastered': 0,
        'screening_count': 0,
        'latest_screening': None,
        'path_progress': {'interactive': 0, 'dyslexia': 0, 'games': 0},
        'component_scores': {},
        'recommendations': [],
        'last_active': None,
    }


def _path_percent(user_id, event_type, key):
    oid = _user_oid(user_id)
    if not oid:
        return 0
    count = get_db().progress_events.count_documents({
        'user_id': oid,
        'event_type': event_type,
    })
    if key == 'interactive':
        return min(100, 20 + count * 15)
    return min(100, count * 25)


EVENT_LABELS = {
    'dyslexia_screening': 'Dyslexia screening',
    'interactive_emotion': 'Emotion learning',
    'interactive_fingers': 'Finger counting',
    'interactive_face': 'Face features',
    'module_visit': 'Module visit',
    'feedback': 'Feedback',
}


def get_activity_stats(user_id):
    oid = _user_oid(user_id)
    if not oid:
        return {
            'breakdown': {},
            'timeline': [],
            'events_this_week': 0,
            'total_events': 0,
            'last_active': None,
        }

    db = get_db()
    events = list(
        db.progress_events.find({'user_id': oid})
        .sort('created_at', -1)
        .limit(100)
    )
    breakdown = {}
    for e in events:
        et = e.get('event_type', '')
        breakdown[et] = breakdown.get(et, 0) + 1

    now = utcnow()
    week_ago = now - timedelta(days=7)
    events_this_week = sum(
        1 for e in events if e.get('created_at') and e['created_at'] >= week_ago
    )

    timeline = []
    for e in events[:25]:
        et = e.get('event_type', '')
        created = e.get('created_at')
        timeline.append({
            'type': et,
            'label': EVENT_LABELS.get(et, et.replace('_', ' ').title()),
            'at': created.isoformat() if created else None,
            'payload': e.get('payload') or {},
        })

    last_active = None
    if events and events[0].get('created_at'):
        last_active = events[0]['created_at'].isoformat()

    return {
        'breakdown': breakdown,
        'timeline': timeline,
        'events_this_week': events_this_week,
        'total_events': db.progress_events.count_documents({'user_id': oid}),
        'last_active': last_active,
    }


def get_path_progress_detailed(user_id):
    oid = _user_oid(user_id)
    if not oid:
        return {
            'interactive': {'percent': 0, 'emotion_sessions': 0, 'finger_sessions': 0},
            'dyslexia': {'percent': 0, 'screenings_done': 0},
            'games': {'percent': 0, 'sessions': 0},
        }

    db = get_db()
    screening_count = db.screening_results.count_documents({'user_id': oid})
    emotion = db.progress_events.count_documents({
        'user_id': oid, 'event_type': 'interactive_emotion',
    })
    fingers = db.progress_events.count_documents({
        'user_id': oid, 'event_type': 'interactive_fingers',
    })
    visits = db.progress_events.count_documents({
        'user_id': oid, 'event_type': 'module_visit',
    })

    return {
        'interactive': {
            'percent': min(100, 15 + emotion * 10 + fingers * 8 + visits * 5),
            'emotion_sessions': emotion,
            'finger_sessions': fingers,
        },
        'dyslexia': {
            'percent': min(100, screening_count * 50),
            'screenings_done': screening_count,
        },
        'games': {
            'percent': min(100, fingers * 5),
            'sessions': fingers,
        },
    }


def get_screening_history(user_id, limit=10):
    oid = _user_oid(user_id)
    if not oid:
        return []
    rows = (
        get_db().screening_results.find({'user_id': oid})
        .sort('created_at', -1)
        .limit(limit)
    )
    return [
        {
            'id': str(r['_id']),
            'overall_score': r.get('overall_score'),
            'risk_level': r.get('risk_level'),
            'component_scores': r.get('component_scores'),
            'recommendations': r.get('recommendations'),
            'created_at': r['created_at'].isoformat() if r.get('created_at') else None,
        }
        for r in rows
    ]


def get_parent_children(parent_id):
    parent_oid = _user_oid(parent_id)
    if not parent_oid:
        return []
    db = get_db()
    links = db.parent_child_links.find({'parent_id': parent_oid})
    children = []
    for link in links:
        child_doc = db.users.find_one({'_id': link['child_id']})
        if child_doc:
            child = User(child_doc)
            summary = get_student_summary(child.id)
            linked_at = link.get('linked_at')
            children.append({
                'id': child.id,
                'display_name': child.display_name,
                'username': child.username,
                'linked_at': linked_at.isoformat() if linked_at else None,
                'summary': summary,
            })
    return children


def get_child_summary_for_parent(parent_id, child_id):
    parent_oid = _user_oid(parent_id)
    child_oid = _user_oid(child_id)
    if not parent_oid or not child_oid:
        return None

    link = get_db().parent_child_links.find_one({
        'parent_id': parent_oid,
        'child_id': child_oid,
    })
    if not link:
        return None

    child_doc = get_db().users.find_one({'_id': child_oid})
    if not child_doc:
        return None

    child = User(child_doc)
    summary = get_student_summary(child_id)
    summary['path_progress'] = get_path_progress_detailed(child_id)

    return {
        'child': child.to_dict(),
        'summary': summary,
        'history': get_screening_history(child_id, limit=10),
        'activity': get_activity_stats(child_id),
    }


def parent_owns_child(parent_id, child_id):
    parent_oid = _user_oid(parent_id)
    child_oid = _user_oid(child_id)
    if not parent_oid or not child_oid:
        return False
    return get_db().parent_child_links.find_one({
        'parent_id': parent_oid,
        'child_id': child_oid,
    }) is not None
