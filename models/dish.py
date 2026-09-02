from database import db


class Dish(db.Model):

    __tablename__ = "dishes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(255)
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    available = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    category = db.relationship(
        "Category",
        backref="dishes"
    )

    def __repr__(self):
        return f"<Dish {self.name}>"