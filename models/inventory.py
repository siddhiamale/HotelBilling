from database import db


class Inventory(db.Model):

    __tablename__ = "inventory"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    unit = db.Column(
        db.String(30),
        nullable=False
    )

    current_stock = db.Column(
        db.Numeric(10, 2),
        default=0,
        nullable=False
    )

    reorder_level = db.Column(
        db.Numeric(10, 2),
        default=0,
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):

        return f"<Inventory {self.name}>"