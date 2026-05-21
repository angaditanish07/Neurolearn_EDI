#!/usr/bin/env python
"""
Create NeuroLearn MongoDB collections and indexes.

Run from project root (with venv active):
  python scripts/init_mongodb.py

Requires MONGODB_URI and MONGODB_DB_NAME in .env (or defaults).
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
except ImportError:
    pass

from pymongo import MongoClient

from app.config import Config
from app.mongo import ensure_indexes_on_database


def main():
    uri = Config.MONGODB_URI
    db_name = Config.MONGODB_DB_NAME
    print(f'Connecting to {uri}')
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print(f'Ping OK — database: {db_name}')

    db = client[db_name]
    ensure_indexes_on_database(db)
    for name in ('users', 'parent_child_links', 'screening_results', 'progress_events'):
        count = db[name].estimated_document_count()
        print(f'  collection {name!r}: {count} documents')

    print('Done. Collections and indexes are ready.')


if __name__ == '__main__':
    main()
