"""MongoDB connection and index setup for NeuroLearn."""

import logging
from datetime import datetime

from bson import ObjectId
from flask import current_app, g
from pymongo import ASCENDING, DESCENDING, MongoClient

logger = logging.getLogger(__name__)

_client = None


def _mongo_uri():
    return current_app.config['MONGODB_URI']


def _mongo_db_name():
    return current_app.config['MONGODB_DB_NAME']


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(_mongo_uri(), serverSelectionTimeoutMS=5000)
    return _client


def get_db():
    if 'mongo_db' not in g:
        g.mongo_db = get_client()[_mongo_db_name()]
    return g.mongo_db


def close_mongo(e=None):
    g.pop('mongo_db', None)


def parse_object_id(value):
    """Return ObjectId or None if invalid."""
    if value is None:
        return None
    if isinstance(value, ObjectId):
        return value
    try:
        return ObjectId(str(value))
    except Exception:
        return None


def ensure_indexes_on_database(db):
    """Create collections indexes (safe to run multiple times)."""
    db.users.create_index('username', unique=True)
    db.users.create_index('email', unique=True)
    db.users.create_index('link_code', unique=True, sparse=True)
    db.parent_child_links.create_index(
        [('parent_id', ASCENDING), ('child_id', ASCENDING)],
        unique=True,
    )
    db.parent_child_links.create_index('parent_id')
    db.parent_child_links.create_index('child_id')
    db.screening_results.create_index([('user_id', ASCENDING), ('created_at', DESCENDING)])
    db.progress_events.create_index([('user_id', ASCENDING), ('created_at', DESCENDING)])
    db.progress_events.create_index([('user_id', ASCENDING), ('event_type', ASCENDING)])


def init_mongo(app):
    global _client
    app.teardown_appcontext(close_mongo)

    uri = app.config['MONGODB_URI']
    db_name = app.config['MONGODB_DB_NAME']
    _client = MongoClient(uri, serverSelectionTimeoutMS=5000)

    try:
        _client.admin.command('ping')
        db = _client[db_name]
        ensure_indexes_on_database(db)
        logger.info('MongoDB connected: %s', db_name)
    except Exception as exc:
        logger.error('MongoDB connection failed: %s', exc)
        raise


def utcnow():
    return datetime.utcnow()
