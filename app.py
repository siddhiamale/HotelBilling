from dotenv import load_dotenv
load_dotenv()
from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

from flask_bcrypt import Bcrypt

from functools import wraps
from config import Config
from database import db

from models.category import Category
from models.user import User
from models.dish import Dish
from models.order import Order
from models.order_item import OrderItem
from models.inventory import Inventory


# Create Flask application
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Secret key for sessions
app.config["SECRET_KEY"] = "hotel_billing_secret_key"

# Initialize database
db.init_app(app)

# Initialize Bcrypt
bcrypt = Bcrypt(app)



# ---------------------------------------------------
# ADMIN / MANAGER ACCESS
# ---------------------------------------------------

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        if session.get("role") not in ["admin", "manager"]:
            return "Access denied. Admin/Manager access required.", 403

        return f(*args, **kwargs)

    return decorated_function


# ---------------------------------------------------
# HOME
# ---------------------------------------------------

@app.route("/")
def home():

    return render_template("home.html")


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            return redirect(url_for("dashboard"))

        return "Invalid username or password"

    return render_template("login.html")


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    from datetime import datetime

    today = datetime.now().date()

    # Today's orders
    todays_orders = Order.query.filter(
        db.func.date(Order.created_at) == today
    ).all()

    # Total orders
    total_orders = len(todays_orders)

    # Paid orders
    paid_orders = [
        order
        for order in todays_orders
        if order.payment_status == "Paid"
    ]

    # Pending orders
    pending_orders = [
        order
        for order in todays_orders
        if order.payment_status != "Paid"
    ]

    # Today's sales
    total_sales = sum(
        float(order.grand_total)
        for order in paid_orders
    )

    # Pending payment amount
    pending_amount = sum(
        float(order.grand_total)
        for order in pending_orders
    )

    # Low stock items
    low_stock_items = Inventory.query.filter(
        Inventory.is_active == True,
        Inventory.current_stock <= Inventory.reorder_level
    ).all()

    return render_template(
        "dashboard.html",

        total_orders=total_orders,

        total_sales=total_sales,

        paid_orders=len(paid_orders),

        pending_orders=len(pending_orders),

        pending_amount=pending_amount,

        low_stock_count=len(low_stock_items)
    )

# ---------------------------------------------------
# CATEGORIES
# ---------------------------------------------------

@app.route("/categories")
@admin_required
def categories():

    if "user_id" not in session:
        return redirect(url_for("login"))

    categories = Category.query.order_by(
        Category.name
    ).all()

    return render_template(
        "categories.html",
        categories=categories
    )


# ---------------------------------------------------
# ADD CATEGORY
# ---------------------------------------------------

@app.route("/categories/add", methods=["GET", "POST"])
@admin_required
def add_category():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"].strip()
        description = request.form["description"].strip()

        existing_category = Category.query.filter_by(
            name=name
        ).first()

        if existing_category:
            return "Category already exists."

        new_category = Category(
            name=name,
            description=description
        )

        db.session.add(new_category)
        db.session.commit()

        return redirect(url_for("categories"))

    return render_template("add_category.html")


# ---------------------------------------------------
# EDIT CATEGORY
# ---------------------------------------------------

@app.route("/categories/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_category(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    category = Category.query.get_or_404(id)

    if request.method == "POST":

        name = request.form["name"].strip()
        description = request.form["description"].strip()

        existing_category = Category.query.filter(
            Category.name == name,
            Category.id != id
        ).first()

        if existing_category:
            return "Another category with this name already exists."

        category.name = name
        category.description = description

        db.session.commit()

        return redirect(url_for("categories"))

    return render_template(
        "edit_category.html",
        category=category
    )


# ---------------------------------------------------
# DEACTIVATE / ACTIVATE CATEGORY
# ---------------------------------------------------

@app.route("/categories/toggle/<int:id>", methods=["POST"])
@admin_required
def toggle_category(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    category = Category.query.get_or_404(id)

    category.is_active = not category.is_active

    db.session.commit()

    return redirect(url_for("categories"))


# ---------------------------------------------------
# DISHES
# ---------------------------------------------------

@app.route("/dishes")
@admin_required
def dishes():

    if "user_id" not in session:
        return redirect(url_for("login"))

    dishes = Dish.query.order_by(
        Dish.name
    ).all()

    return render_template(
        "dishes.html",
        dishes=dishes
    )


# ---------------------------------------------------
# ADD DISH
# ---------------------------------------------------

@app.route("/dishes/add", methods=["GET", "POST"])
@admin_required
def add_dish():

    if "user_id" not in session:
        return redirect(url_for("login"))

    categories = Category.query.order_by(
        Category.name
    ).all()

    if request.method == "POST":

        name = request.form["name"].strip()

        description = request.form["description"].strip()

        category_id = request.form["category_id"]

        price = request.form["price"]

        available = "available" in request.form

        # Check duplicate dish
        existing_dish = Dish.query.filter_by(
            name=name
        ).first()

        if existing_dish:

            return "Dish already exists."

        new_dish = Dish(
            name=name,
            description=description,
            category_id=int(category_id),
            price=price,
            available=available
        )

        db.session.add(new_dish)

        db.session.commit()

        return redirect(url_for("dishes"))

    return render_template(
        "add_dish.html",
        categories=categories
    )


# ---------------------------------------------------
# EDIT DISH
# ---------------------------------------------------

@app.route("/dishes/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_dish(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    dish = Dish.query.get_or_404(id)

    categories = Category.query.order_by(
        Category.name
    ).all()

    if request.method == "POST":

        name = request.form["name"].strip()
        description = request.form["description"].strip()
        category_id = request.form["category_id"]
        price = request.form["price"]

        available = "available" in request.form

        dish.name = name
        dish.description = description
        dish.category_id = int(category_id)
        dish.price = price
        dish.available = available

        db.session.commit()

        return redirect(url_for("dishes"))

    return render_template(
        "edit_dish.html",
        dish=dish,
        categories=categories
    )


# ---------------------------------------------------
# DEACTIVATE DISH
# ---------------------------------------------------

@app.route("/dishes/deactivate/<int:id>")
@admin_required
def deactivate_dish(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    dish = Dish.query.get_or_404(id)

    dish.available = False

    db.session.commit()

    return redirect(url_for("dishes"))


# ---------------------------------------------------
# ACTIVATE DISH
# ---------------------------------------------------

@app.route("/dishes/activate/<int:id>")
@admin_required
def activate_dish(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    dish = Dish.query.get_or_404(id)

    dish.available = True

    db.session.commit()

    return redirect(url_for("dishes"))


# ---------------------------------------------------
# ORDERS
# ---------------------------------------------------

@app.route("/orders")
def orders():

    if "user_id" not in session:
        return redirect(url_for("login"))

    orders = Order.query.order_by(
        Order.id.desc()
    ).all()

    return render_template(
        "orders.html",
        orders=orders
    )

# ---------------------------------------------------
# SALES REPORT
# ---------------------------------------------------

@app.route("/sales")
@admin_required
def sales():

    if "user_id" not in session:
        return redirect(url_for("login"))

    from datetime import datetime

    selected_date = request.args.get("date")

    if selected_date:

        try:
            report_date = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            report_date = datetime.now().date()

    else:

        report_date = datetime.now().date()

    orders = Order.query.filter(
        db.func.date(Order.created_at) == report_date
    ).order_by(
        Order.id.desc()
    ).all()

    total_orders = len(orders)

    paid_orders = [
        order
        for order in orders
        if order.payment_status == "Paid"
    ]

    pending_orders = [
        order
        for order in orders
        if order.payment_status != "Paid"
    ]

    total_sales = sum(
        float(order.grand_total)
        for order in paid_orders
    )

    cash_sales = sum(
        float(order.grand_total)
        for order in paid_orders
        if order.payment_method == "Cash"
    )

    upi_sales = sum(
        float(order.grand_total)
        for order in paid_orders
        if order.payment_method == "UPI"
    )

    card_sales = sum(
        float(order.grand_total)
        for order in paid_orders
        if order.payment_method == "Card"
    )

    pending_amount = sum(
        float(order.grand_total)
        for order in pending_orders
    )

    return render_template(
        "sales.html",
        orders=orders,
        report_date=report_date,
        total_orders=total_orders,
        total_sales=total_sales,
        cash_sales=cash_sales,
        upi_sales=upi_sales,
        card_sales=card_sales,
        pending_orders=len(pending_orders),
        pending_amount=pending_amount
    )



# ---------------------------------------------------
# BEST SELLING DISHES
# ---------------------------------------------------

@app.route("/best-selling")
@admin_required
def best_selling():

    if "user_id" not in session:
        return redirect(url_for("login"))

    from datetime import datetime

    # Get selected date
    selected_date = request.args.get("date")

    if selected_date:

        try:
            report_date = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            report_date = datetime.now().date()

    else:

        report_date = datetime.now().date()


    # Get orders for selected date
    orders = Order.query.filter(
        db.func.date(Order.created_at) == report_date
    ).all()


    # ---------------------------------------------
    # CALCULATE DISH SALES
    # ---------------------------------------------

    dish_data = {}


    for order in orders:

        # Only count paid orders
        if order.payment_status != "Paid":
            continue


        for item in order.items:

            dish = item.dish

            if not dish:
                continue


            dish_id = dish.id


            if dish_id not in dish_data:

                dish_data[dish_id] = {

                    "name": dish.name,

                    "category": dish.category.name
                    if dish.category
                    else "Uncategorized",

                    "quantity": 0,

                    "revenue": 0

                }


            dish_data[dish_id]["quantity"] += item.quantity


            dish_data[dish_id]["revenue"] += (
                float(item.price) *
                item.quantity
            )


    # ---------------------------------------------
    # SORT BY QUANTITY SOLD
    # ---------------------------------------------

    best_dishes = sorted(

        dish_data.values(),

        key=lambda x: x["quantity"],

        reverse=True

    )


    return render_template(

        "best_selling.html",

        best_dishes=best_dishes,

        report_date=report_date

    )


# ---------------------------------------------------
# MONTHLY SALES REPORT
# ---------------------------------------------------

@app.route("/monthly-sales")
@admin_required
def monthly_sales():

    if "user_id" not in session:
        return redirect(url_for("login"))

    from datetime import datetime
    import calendar

    # Get selected month and year
    selected_month = request.args.get("month")
    selected_year = request.args.get("year")

    today = datetime.now()

    try:
        month = int(selected_month) if selected_month else today.month
        year = int(selected_year) if selected_year else today.year

        if month < 1 or month > 12:
            raise ValueError

        if year < 2000 or year > 2100:
            raise ValueError

    except (ValueError, TypeError):

        month = today.month
        year = today.year


    # Number of days in selected month
    days_in_month = calendar.monthrange(
        year,
        month
    )[1]


    # ---------------------------------------------
    # GET ORDERS FOR SELECTED MONTH
    # ---------------------------------------------

    orders = Order.query.filter(
        db.extract(
            "month",
            Order.created_at
        ) == month,

        db.extract(
            "year",
            Order.created_at
        ) == year

    ).order_by(
        Order.created_at.asc()
    ).all()


    # ---------------------------------------------
    # DAILY SALES
    # ---------------------------------------------

    daily_sales = {}

    for day in range(1, days_in_month + 1):

        daily_sales[day] = 0


    for order in orders:

        if order.payment_status != "Paid":
            continue

        day = order.created_at.day

        daily_sales[day] += float(
            order.grand_total
        )


    # ---------------------------------------------
    # TOTAL SALES
    # ---------------------------------------------

    total_sales = sum(
        daily_sales.values()
    )


    # ---------------------------------------------
    # TOTAL ORDERS
    # ---------------------------------------------

    total_orders = len(orders)


    # ---------------------------------------------
    # PAID ORDERS
    # ---------------------------------------------

    paid_orders = [
        order
        for order in orders
        if order.payment_status == "Paid"
    ]


    # ---------------------------------------------
    # PENDING ORDERS
    # ---------------------------------------------

    pending_orders = [
        order
        for order in orders
        if order.payment_status != "Paid"
    ]


    # ---------------------------------------------
    # PAYMENT BREAKDOWN
    # ---------------------------------------------

    cash_sales = sum(
        float(order.grand_total)
        for order in paid_orders
        if order.payment_method == "Cash"
    )


    upi_sales = sum(
        float(order.grand_total)
        for order in paid_orders
        if order.payment_method == "UPI"
    )


    card_sales = sum(
        float(order.grand_total)
        for order in paid_orders
        if order.payment_method == "Card"
    )


    pending_amount = sum(
        float(order.grand_total)
        for order in pending_orders
    )


    # ---------------------------------------------
    # HIGHEST SALES DAY
    # ---------------------------------------------

    highest_sales_day = max(
        daily_sales,
        key=daily_sales.get
    )


    highest_sales_amount = daily_sales[
        highest_sales_day
    ]


    # ---------------------------------------------
    # LOWEST SALES DAY
    # ---------------------------------------------

    lowest_sales_day = min(
        daily_sales,
        key=daily_sales.get
    )


    lowest_sales_amount = daily_sales[
        lowest_sales_day
    ]


    return render_template(

        "monthly_sales.html",

        month=month,

        year=year,

        days_in_month=days_in_month,

        daily_sales=daily_sales,

        total_sales=total_sales,

        total_orders=total_orders,

        cash_sales=cash_sales,

        upi_sales=upi_sales,

        card_sales=card_sales,

        pending_orders=len(
            pending_orders
        ),

        pending_amount=pending_amount,

        highest_sales_day=highest_sales_day,

        highest_sales_amount=highest_sales_amount,

        lowest_sales_day=lowest_sales_day,

        lowest_sales_amount=lowest_sales_amount

    )


# ---------------------------------------------------
# INVENTORY
# ---------------------------------------------------

@app.route("/inventory")
@admin_required
def inventory():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get search text
    search = request.args.get("search", "").strip()

    # Start with active inventory items
    query = Inventory.query.filter_by(
        is_active=True
    )

    # Apply search
    if search:
        query = query.filter(
            Inventory.name.ilike(
                f"%{search}%"
            )
        )

    inventory_items = query.order_by(
        Inventory.name.asc()
    ).all()

    # Count low-stock items
    low_stock_count = sum(
        1
        for item in inventory_items
        if item.current_stock <= item.reorder_level
    )

    return render_template(
        "inventory.html",
        inventory=inventory_items,
        low_stock_count=low_stock_count,
        search=search
    )


# ---------------------------------------------------
# ADD INVENTORY ITEM
# ---------------------------------------------------

@app.route("/inventory/add", methods=["GET", "POST"])
@admin_required
def add_inventory():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"].strip()
        unit = request.form["unit"]
        current_stock = request.form["current_stock"]
        reorder_level = request.form["reorder_level"]

        # Check duplicate item
        existing_item = Inventory.query.filter_by(
            name=name
        ).first()

        if existing_item:

            return "Inventory item already exists."

        item = Inventory(

            name=name,

            unit=unit,

            current_stock=current_stock,

            reorder_level=reorder_level,

            is_active=True

        )

        db.session.add(item)

        db.session.commit()

        return redirect(
            url_for("inventory")
        )

    return render_template(
        "add_inventory.html"
    )


# ---------------------------------------------------
# EDIT INVENTORY ITEM
# ---------------------------------------------------

@app.route("/inventory/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_inventory(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Inventory.query.get_or_404(id)

    if request.method == "POST":

        item.name = request.form["name"].strip()
        item.unit = request.form["unit"]
        item.current_stock = request.form["current_stock"]
        item.reorder_level = request.form["reorder_level"]

        db.session.commit()

        return redirect(
            url_for("inventory")
        )

    return render_template(
        "edit_inventory.html",
        item=item
    )


# ---------------------------------------------------
# STOCK IN
# ---------------------------------------------------

@app.route("/inventory/stock-in/<int:id>", methods=["GET", "POST"])
@admin_required
def stock_in(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Inventory.query.get_or_404(id)

    if request.method == "POST":

        from decimal import Decimal

        quantity = Decimal(
            request.form["quantity"]
        )

        if quantity <= 0:
            return "Quantity must be greater than zero."

        item.current_stock += quantity

        db.session.commit()

        return redirect(
            url_for("inventory")
        )

    return render_template(
        "stock_update.html",
        item=item,
        action="Stock In"
    )


# ---------------------------------------------------
# STOCK OUT
# ---------------------------------------------------

@app.route("/inventory/stock-out/<int:id>", methods=["GET", "POST"])
@admin_required
def stock_out(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Inventory.query.get_or_404(id)

    if request.method == "POST":

        from decimal import Decimal

        quantity = Decimal(
            request.form["quantity"]
        )

        if quantity <= 0:
            return "Quantity must be greater than zero."

        if quantity > item.current_stock:
            return "Not enough stock available."

        item.current_stock -= quantity

        db.session.commit()

        return redirect(
            url_for("inventory")
        )

    return render_template(
        "stock_update.html",
        item=item,
        action="Stock Out"
    )



# ---------------------------------------------------
# DEACTIVATE INVENTORY ITEM
# ---------------------------------------------------

@app.route("/inventory/deactivate/<int:id>")
@admin_required
def deactivate_inventory(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Inventory.query.get_or_404(id)

    item.is_active = False

    db.session.commit()

    return redirect(
        url_for("inventory")
    )


# ---------------------------------------------------
# ACTIVATE INVENTORY ITEM
# ---------------------------------------------------

@app.route("/inventory/activate/<int:id>")
@admin_required
def activate_inventory(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = Inventory.query.get_or_404(id)

    item.is_active = True

    db.session.commit()

    return redirect(
        url_for("inventory")
    )


# ---------------------------------------------------
# NEW ORDER
# ---------------------------------------------------

@app.route("/orders/new", methods=["GET", "POST"])
def new_order():

    if "user_id" not in session:
        return redirect(url_for("login"))

    dishes = Dish.query.filter_by(
        available=True
    ).order_by(
        Dish.name
    ).all()

    categories = Category.query.order_by(
        Category.name
    ).all()

    if request.method == "POST":

        order_type = request.form.get("order_type")

        order_data = request.form.get("order_data")

        if not order_data:
            return "No dishes selected."

        import json

        items = json.loads(order_data)

        if not items:
            return "No dishes selected."

        subtotal = 0

        order_items_data = []

        for item in items:

            dish_id = int(item["id"])

            quantity = int(item["quantity"])

            dish = Dish.query.get(dish_id)

            if not dish or not dish.available:
                continue

            if quantity <= 0:
                continue

            price = float(dish.price)

            amount = price * quantity

            subtotal += amount

            order_items_data.append({
                "dish": dish,
                "quantity": quantity,
                "price": price,
                "amount": amount
            })

        if not order_items_data:
            return "No valid dishes selected."

        tax = subtotal * 0.05

        discount = 0

        grand_total = subtotal + tax - discount

        # Create Order

        order = Order(
            order_type=order_type,
            subtotal=subtotal,
            tax=tax,
            discount=discount,
            grand_total=grand_total,
            payment_status="Pending",
            status="Completed"
        )

        db.session.add(order)

        db.session.flush()

        # Create Order Items

        for item in order_items_data:

            order_item = OrderItem(
                order_id=order.id,
                dish_id=item["dish"].id,
                quantity=item["quantity"],
                price=item["price"],
                amount=item["amount"]
            )

            db.session.add(order_item)

        db.session.commit()

        # Open Bill after saving order

        return redirect(
            url_for(
                "view_bill",
                id=order.id
            )
        )

    # Show New Order page

    return render_template(
        "new_order.html",
        dishes=dishes,
        categories=categories
    )
# ---------------------------------------------------
# VIEW BILL
# ---------------------------------------------------

@app.route("/orders/<int:id>/bill")
def view_bill(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    order = Order.query.get_or_404(id)

    return render_template(
        "bill.html",
        order=order
    )


# ---------------------------------------------------
# PAYMENT
# ---------------------------------------------------

@app.route("/orders/<int:id>/payment", methods=["GET", "POST"])
def payment(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    order = Order.query.get_or_404(id)

    if request.method == "POST":

        payment_method = request.form.get(
            "payment_method"
        )

        if payment_method not in [
            "Cash",
            "UPI",
            "Card"
        ]:
            return "Invalid payment method"

        order.payment_method = payment_method

        order.payment_status = "Paid"

        db.session.commit()

        return redirect(
            url_for(
                "view_bill",
                id=order.id
            )
        )

    return render_template(
        "payment.html",
        order=order
    )


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)