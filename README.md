# HotelBilling
Hotel Billing System built with Flask and PostgreSQL

# 🏨 Hotel Billing System

A web-based Hotel Billing and Management System built using **Flask** and **PostgreSQL**.

The system helps hotel staff manage orders, dishes, categories, inventory, bills, payments, and sales reports from a single web application.

---

## 🚀 Features

- 🔐 User Login & Role-Based Access
- 📊 Dashboard
- 🧾 Create and Manage Orders
- 🍽️ Dish Management
- 📂 Category Management
- 📦 Inventory Management
- 💰 Billing & Payment Status
- 📈 Sales Reports
- 🏆 Best Selling Dishes
- 📅 Monthly Sales Reports
- ✅ Activate / Deactivate Categories
- ✅ Activate / Deactivate Dishes
- ✅ Activate / Deactivate Inventory Items
- 🖨️ Printable Bills

---

## 🛠️ Technologies Used

- **Python**
- **Flask**
- **Flask-SQLAlchemy**
- **PostgreSQL**
- **SQLAlchemy**
- **Jinja2**
- **HTML**
- **CSS**
- **JavaScript**
- **Bootstrap**

---

## 📁 Project Structure

```text
HotelBilling/
│
├── app.py
├── config.py
├── database.py
├── create_admin.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── database/
│   └── hotel_billing.sql
│
├── models/
│   ├── category.py
│   ├── dish.py
│   ├── inventory.py
│   ├── order.py
│   ├── order_item.py
│   └── user.py
│
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── categories.html
    ├── dishes.html
    ├── inventory.html
    ├── new_order.html
    ├── orders.html
    ├── bill.html
    ├── payment.html
    ├── sales.html
    ├── best_selling.html
    └── monthly_sales.html
