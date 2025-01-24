from app import create_app, db
from app.services.cleanup_service import init_cleanup_scheduler

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    init_cleanup_scheduler(app)
    app.run(debug=True)
