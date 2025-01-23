from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app import db
from app.models.models import Note, SharedUrl
import os

def cleanup_expired(app):
    with app.app_context():
        now = datetime.utcnow()
        
        # Tìm các shared URL đã hết hạn
        expired_shares = SharedUrl.query.filter(SharedUrl.expires_at < now).all()
        
        for share in expired_shares:
            try:
                db.session.delete(share)
            except Exception as e:
                print(f"Error deleting expired share {share.id}: {str(e)}")
                
        try:
            db.session.commit()
            print(f"Cleaned up {len(expired_shares)} expired shares")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing cleanup: {str(e)}")

def init_cleanup_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: cleanup_expired(app), trigger="interval", hours=1)
    scheduler.start()