from app import app, db, bcrypt
from models.user import User


with app.app_context():

    existing_user = User.query.filter_by(
        username="admin"
    ).first()

    if existing_user:

        print("Admin user already exists.")

    else:

        hashed_password = bcrypt.generate_password_hash(
            "admin123"
        ).decode("utf-8")

        admin = User(
            username="admin",
            password=hashed_password,
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin user created successfully.")