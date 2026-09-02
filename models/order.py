from database import db


class Order(db.Model):

    __tablename__ = "orders"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_type = db.Column(
        db.String(30),
        nullable=False,
        default="Dine In"
    )

    subtotal = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    tax = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    discount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    grand_total = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    payment_method = db.Column(
        db.String(30),
        nullable=True
    )

    payment_status = db.Column(
        db.String(30),
        nullable=False,
        default="Pending"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Completed"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    items = db.relationship(
        "OrderItem",
        backref="order",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order {self.id}>"