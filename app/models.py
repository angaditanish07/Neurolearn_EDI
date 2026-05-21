"""MongoDB document wrappers (NeuroLearn collections)."""

from app.mongo import parse_object_id, utcnow

DEFAULT_PREFERENCES = {
    'font_size': 16,
    'dyslexic_font': False,
    'high_contrast': False,
    'read_aloud': False,
}


class User:
    """users collection"""

    def __init__(self, doc):
        self._doc = doc

    @property
    def id(self):
        return str(self._doc['_id'])

    @property
    def username(self):
        return self._doc.get('username', '')

    @property
    def email(self):
        return self._doc.get('email', '')

    @property
    def password_hash(self):
        return self._doc.get('password_hash', '')

    @property
    def role(self):
        return self._doc.get('role', 'student')

    @property
    def display_name(self):
        return self._doc.get('display_name', '')

    @property
    def link_code(self):
        return self._doc.get('link_code')

    @property
    def created_at(self):
        return self._doc.get('created_at')

    @property
    def preferences(self):
        return self._doc.get('preferences') or dict(DEFAULT_PREFERENCES)

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

    @staticmethod
    def new_document(username, email, password_hash, role, display_name, link_code=None):
        return {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'display_name': display_name,
            'link_code': link_code,
            'preferences': dict(DEFAULT_PREFERENCES),
            'created_at': utcnow(),
        }


class ParentChildLink:
    """parent_child_links collection"""

    def __init__(self, doc):
        self._doc = doc

    @property
    def id(self):
        return str(self._doc['_id'])

    @property
    def parent_id(self):
        return str(self._doc['parent_id'])

    @property
    def child_id(self):
        return str(self._doc['child_id'])

    @property
    def linked_at(self):
        return self._doc.get('linked_at')


class ScreeningResult:
    """screening_results collection"""

    def __init__(self, doc):
        self._doc = doc

    @property
    def id(self):
        return str(self._doc['_id'])

    @property
    def user_id(self):
        return str(self._doc['user_id'])

    @property
    def overall_score(self):
        return self._doc.get('overall_score')

    @property
    def risk_level(self):
        return self._doc.get('risk_level')

    @property
    def component_scores(self):
        return self._doc.get('component_scores') or {}

    @property
    def recommendations(self):
        return self._doc.get('recommendations') or []

    @property
    def feature_importance(self):
        return self._doc.get('feature_importance') or {}

    @property
    def created_at(self):
        return self._doc.get('created_at')

    @staticmethod
    def new_document(user_id, overall_score, risk_level, component_scores,
                     recommendations, feature_importance=None):
        oid = parse_object_id(user_id)
        return {
            'user_id': oid,
            'overall_score': float(overall_score),
            'risk_level': int(risk_level),
            'component_scores': component_scores or {},
            'recommendations': recommendations or [],
            'feature_importance': feature_importance or {},
            'created_at': utcnow(),
        }


class ProgressEvent:
    """progress_events collection"""

    def __init__(self, doc):
        self._doc = doc

    @property
    def id(self):
        return str(self._doc['_id'])

    @property
    def user_id(self):
        return str(self._doc['user_id'])

    @property
    def event_type(self):
        return self._doc.get('event_type', '')

    @property
    def payload(self):
        return self._doc.get('payload') or {}

    @property
    def created_at(self):
        return self._doc.get('created_at')

    @staticmethod
    def new_document(user_id, event_type, payload=None):
        return {
            'user_id': parse_object_id(user_id),
            'event_type': event_type,
            'payload': payload or {},
            'created_at': utcnow(),
        }
