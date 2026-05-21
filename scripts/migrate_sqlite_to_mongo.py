#!/usr/bin/env python
"""
One-time migration: SQLite data/neurolearn.db -> MongoDB.

Run from project root (with venv active and MongoDB running):
  python scripts/migrate_sqlite_to_mongo.py

Skips documents that already exist (by username / unique keys).
"""

import os
import sqlite3
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
except ImportError:
    pass

from bson import ObjectId
from pymongo import MongoClient

from app.config import Config


def parse_dt(value):
    if not value:
        return datetime.utcnow()
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace('Z', ''))
    except Exception:
        return datetime.utcnow()


def main():
    sqlite_path = os.path.join(PROJECT_ROOT, 'data', 'neurolearn.db')
    if not os.path.isfile(sqlite_path):
        print(f'No SQLite file at {sqlite_path} — nothing to migrate.')
        return

    client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client[Config.MONGODB_DB_NAME]

    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row

    id_map = {}  # old int user id -> ObjectId

    print('Migrating users...')
    for row in conn.execute('SELECT * FROM users ORDER BY id'):
        if db.users.find_one({'username': row['username']}):
            existing = db.users.find_one({'username': row['username']})
            id_map[row['id']] = existing['_id']
            continue
        doc = {
            'username': row['username'],
            'email': row['email'],
            'password_hash': row['password_hash'],
            'role': row['role'],
            'display_name': row['display_name'],
            'link_code': row['link_code'],
            'created_at': parse_dt(row['created_at']),
            'preferences': {
                'font_size': 16,
                'dyslexic_font': False,
                'high_contrast': False,
                'read_aloud': False,
            },
        }
        pref = conn.execute(
            'SELECT * FROM user_preferences WHERE user_id = ?', (row['id'],)
        ).fetchone()
        if pref:
            doc['preferences'] = {
                'font_size': pref['font_size'] or 16,
                'dyslexic_font': bool(pref['dyslexic_font']),
                'high_contrast': bool(pref['high_contrast']),
                'read_aloud': bool(pref['read_aloud']),
            }
        oid = db.users.insert_one(doc).inserted_id
        id_map[row['id']] = oid
    print(f'  {len(id_map)} users mapped')

    print('Migrating parent_child_links...')
    for row in conn.execute('SELECT * FROM parent_child_links'):
        parent_oid = id_map.get(row['parent_id'])
        child_oid = id_map.get(row['child_id'])
        if not parent_oid or not child_oid:
            continue
        if db.parent_child_links.find_one({'parent_id': parent_oid, 'child_id': child_oid}):
            continue
        db.parent_child_links.insert_one({
            'parent_id': parent_oid,
            'child_id': child_oid,
            'linked_at': parse_dt(row['linked_at']),
        })

    print('Migrating screening_results...')
    for row in conn.execute('SELECT * FROM screening_results ORDER BY id'):
        user_oid = id_map.get(row['user_id'])
        if not user_oid:
            continue
        import json
        comp = row['component_scores']
        rec = row['recommendations']
        feat = row['feature_importance']
        if isinstance(comp, str):
            comp = json.loads(comp) if comp else {}
        if isinstance(rec, str):
            rec = json.loads(rec) if rec else []
        if isinstance(feat, str):
            feat = json.loads(feat) if feat else {}
        db.screening_results.insert_one({
            'user_id': user_oid,
            'overall_score': float(row['overall_score']),
            'risk_level': int(row['risk_level']),
            'component_scores': comp or {},
            'recommendations': rec or [],
            'feature_importance': feat or {},
            'created_at': parse_dt(row['created_at']),
        })

    print('Migrating progress_events...')
    for row in conn.execute('SELECT * FROM progress_events ORDER BY id'):
        user_oid = id_map.get(row['user_id'])
        if not user_oid:
            continue
        import json
        payload = row['payload']
        if isinstance(payload, str):
            payload = json.loads(payload) if payload else {}
        db.progress_events.insert_one({
            'user_id': user_oid,
            'event_type': row['event_type'],
            'payload': payload or {},
            'created_at': parse_dt(row['created_at']),
        })

    conn.close()
    from app.mongo import ensure_indexes_on_database

    ensure_indexes_on_database(db)
    print('Migration complete. Re-login may be required (user IDs are now MongoDB ObjectIds).')


if __name__ == '__main__':
    main()
