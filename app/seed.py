import os
from app import create_app, db, User

app=create_app()
with app.app_context():
    db.create_all()
    email=os.getenv("ADMIN_EMAIL","admin@eduprime.local")
    password=os.getenv("ADMIN_PASSWORD","")
    if len(password)<10:
        raise SystemExit("Set ADMIN_PASSWORD to a unique password of at least 10 characters before seeding.")
    if not User.query.filter_by(email=email).first():
        admin=User(full_name=os.getenv("ADMIN_NAME","EduPrime Administrator"),email=email,role="admin")
        admin.set_password(password); db.session.add(admin); db.session.commit()
        print("Created administrator account:",email)
    else:
        print("Administrator account already exists:",email)
