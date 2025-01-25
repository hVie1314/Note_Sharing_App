from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app import db
from app.models.models import Note, SharedUrl
import os
import pytz

def cleanup_expired(app):
    with app.app_context():
        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        
        # Lấy thời gian hiện tại theo múi giờ Việt Nam
        current_time = datetime.now(vietnam_tz)
        # Cleanup expired notes
        # expired_notes = Note.query.filter(Note.expires_at < now).all()
        # for note in expired_notes:
        #     try:
        #         os.remove(os.path.join(app.config['NOTES_DIR'], note.filename))
        #     except:
        #         pass
        #     db.session.delete(note)
        
        # Cleanup expired shared URLs
        expired_urls = SharedUrl.query.filter(SharedUrl.expires_atreplace(tzinfo=pytz.FixedOffset(7 * 60)) < current_time).all()
        for url in expired_urls:
            db.session.delete(url)
            
        db.session.commit()
        print(f"Cleanup completed at {current_time}")

def init_cleanup_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: cleanup_expired(app), trigger="interval", hours=1)
    scheduler.start()