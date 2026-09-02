from database import db


class OrderItem(db.Model):

    __tablename__ = "order_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    dish_id = db.Column(
        db.Integer,
        db.ForeignKey("dishes.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    dish = db.relationship(
        "Dish",
        backref="order_items"
    )

    def __repr__(self):
        return f"<OrderItem {self.id}>"