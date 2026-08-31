# clear_cache.py
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from backend.database import get_db, DBVideoRecord, DBForensicReport, DBAuditLog

def clear_database():
    # Get the database session from your existing setup
    db = next(get_db())
    try:
        print("🧼 Wiping cached records...")
        db.query(DBForensicReport).delete()
        db.query(DBVideoRecord).delete()
        db.query(DBAuditLog).delete()
        db.commit()
        print("✅ Database cache successfully cleared!")
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to clear database: {e}")

if __name__ == "__main__":
    clear_database()