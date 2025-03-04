from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import json
import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "upitrackersecretkey"  # For session and flash messages

# App configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

CHARTS_DIR = os.path.join(STATIC_DIR, "charts")
if not os.path.exists(CHARTS_DIR):
    os.makedirs(CHARTS_DIR)

# Categories and UPI apps
CATEGORIES = [
    "Food", "Transportation", "Shopping", "Entertainment", 
    "Education", "Utilities", "Health", "Other"
]

UPI_APPS = [
    "Google Pay", "PhonePe", "Paytm", "Amazon Pay", 
    "BHIM", "WhatsApp Pay", "Other"
]

# Helper functions
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_user_file(username):
    return os.path.join(DATA_DIR, f"{username}_data.json")

def load_user_data(username):
    user_file = get_user_file(username)
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            return json.load(f)
    return {
        "profile": {
            "name": "",
            "account_balance": 0,
            "monthly_budget": 0,
            "parent_email": "",
            "share_with_parents": False
        },
        "transactions": []
    }

def save_user_data(username, data):
    user_file = get_user_file(username)
    with open(user_file, 'w') as f:
        json.dump(data, f, indent=4)

def generate_charts(username):
    user_data = load_user_data(username)
    transactions = user_data["transactions"]
    
    if not transactions:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    
    # Category spending chart
    plt.figure(figsize=(10, 6))
    category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
    
    # Create a colorful bar chart
    sns.barplot(x=category_spending.index, y=category_spending.values)
    plt.title('Spending by Category')
    plt.xlabel('Category')
    plt.ylabel('Amount (₹)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    category_chart = f"{username}_category.png"
    plt.savefig(os.path.join(CHARTS_DIR, category_chart))
    plt.close()
    
    # UPI app spending chart
    plt.figure(figsize=(10, 6))
    app_spending = df.groupby('upi_app')['amount'].sum().sort_values(ascending=False)
    
    # Create a pie chart for UPI apps
    plt.pie(app_spending, labels=app_spending.index, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Spending by UPI App')
    plt.tight_layout()
    
    app_chart = f"{username}_upiapp.png"
    plt.savefig(os.path.join(CHARTS_DIR, app_chart))
    plt.close()
    
    # Time series chart if enough data
    if len(df) > 1:
        plt.figure(figsize=(12, 6))
        # Ensure chronological order
        df = df.sort_values('date')
        # Group by date and sum amounts
        daily_spending = df.groupby(df['date'].dt.date)['amount'].sum()
        
        plt.plot(daily_spending.index, daily_spending.values, marker='o', linestyle='-')
        plt.title('Daily Spending Over Time')
        plt.xlabel('Date')
        plt.ylabel('Amount (₹)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        time_chart = f"{username}_timeseries.png"
        plt.savefig(os.path.join(CHARTS_DIR, time_chart))
        plt.close()
        
        return {
            "category": category_chart,
            "app": app_chart,
            "time": time_chart
        }
    
    return {
        "category": category_chart,
        "app": app_chart
    }

def get_saving_tip():
    tips = [
        "Track your daily expenses and set spending limits for each category.",
        "Cook at home instead of ordering food to save on food expenses.",
        "Use student discounts wherever available.",
        "Plan your purchases and avoid impulse buying.",
        "Use public transportation instead of cabs when possible.",
        "Cancel unused subscriptions.",
        "Wait 24 hours before making non-essential purchases.",
        "Set aside a small percentage of your income as savings.",
        "Look for second-hand textbooks instead of buying new ones.",
        "Make a shopping list before going to the store and stick to it.",
        "Use campus facilities like library and computer labs instead of buying equipment.",
        "Split subscription costs with friends or roommates."
    ]
    
    # Return a random tip
    import random
    return random.choice(tips)

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        users = load_users()
        
        if username in users:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        users[username] = {
            "password_hash": generate_password_hash(password),
            "created_at": datetime.datetime.now().isoformat()
        }
        
        save_users(users)
        
        # Create initial user data
        user_data = load_user_data(username)
        save_user_data(username, user_data)
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        
        if username not in users or not check_password_hash(users[username]["password_hash"], password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        session['username'] = username
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    # Generate charts for the dashboard
    charts = generate_charts(username) or {}
    
    # Get transactions, sorted by date (newest first)
    transactions = sorted(
        user_data["transactions"], 
        key=lambda x: x.get("date", ""), 
        reverse=True
    )
    
    # Calculate spending statistics
    total_spent = sum(t["amount"] for t in user_data["transactions"])
    
    # Monthly spending
    current_month = datetime.datetime.now().strftime("%Y-%m")
    monthly_transactions = [
        t for t in user_data["transactions"] 
        if t["date"].startswith(current_month)
    ]
    monthly_spent = sum(t["amount"] for t in monthly_transactions)
    
    # Budget calculations
    budget = user_data["profile"]["monthly_budget"]
    balance = user_data["profile"]["account_balance"]
    budget_percent = (monthly_spent / budget * 100) if budget > 0 else 0
    
    # Get a saving tip
    saving_tip = get_saving_tip()
    
    return render_template(
        'dashboard.html',
        profile=user_data["profile"],
        transactions=transactions[:10],  # Show only the 10 most recent
        charts=charts,
        total_spent=total_spent,
        monthly_spent=monthly_spent,
        budget_percent=budget_percent,
        balance=balance,
        saving_tip=saving_tip
    )

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    if request.method == 'POST':
        # Update profile
        user_data["profile"]["name"] = request.form['name']
        user_data["profile"]["account_balance"] = float(request.form['account_balance'])
        user_data["profile"]["monthly_budget"] = float(request.form['monthly_budget'])
        user_data["profile"]["parent_email"] = request.form['parent_email']
        user_data["profile"]["share_with_parents"] = 'share_with_parents' in request.form
        
        save_user_data(username, user_data)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('profile.html', profile=user_data["profile"])

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form['description']
            upi_app = request.form['upi_app']
            category = request.form['category']
            
            if amount <= 0:
                flash('Amount must be greater than 0', 'danger')
                return redirect(url_for('add_transaction'))
            
            # Create transaction
            transaction = {
                "id": str(uuid.uuid4()),  # Generate unique ID
                "date": datetime.datetime.now().isoformat(),
                "amount": amount,
                "description": description,
                "upi_app": upi_app,
                "category": category
            }
            
            # Update balance
            user_data["profile"]["account_balance"] -= amount
            
            # Add transaction
            user_data["transactions"].append(transaction)
            save_user_data(username, user_data)
            
            flash('Transaction added successfully', 'success')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid amount', 'danger')
            return redirect(url_for('add_transaction'))
    
    return render_template(
        'add_transaction.html', 
        categories=CATEGORIES, 
        upi_apps=UPI_APPS
    )

@app.route('/all_transactions')
def all_transactions():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    # Sort transactions by date (newest first)
    transactions = sorted(
        user_data["transactions"], 
        key=lambda x: x.get("date", ""), 
        reverse=True
    )
    
    return render_template('all_transactions.html', transactions=transactions)

@app.route('/analytics')
def analytics():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    # Generate fresh charts
    charts = generate_charts(username) or {}
    
    # If no transactions, redirect to add transaction
    if not user_data["transactions"]:
        flash('Add some transactions to see analytics', 'info')
        return redirect(url_for('add_transaction'))
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(user_data["transactions"])
    
    # Calculate basic stats
    total_spent = sum(t["amount"] for t in user_data["transactions"])
    transaction_count = len(user_data["transactions"])
    avg_transaction = total_spent / transaction_count if transaction_count > 0 else 0
    
    # Category breakdown
    category_data = {}
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        for category, amount in category_spending.items():
            percentage = (amount / total_spent) * 100
            category_data[category] = {
                "amount": amount,
                "percentage": percentage
            }
    
    # UPI app breakdown
    app_data = {}
    if not df.empty:
        app_spending = df.groupby('upi_app')['amount'].sum().sort_values(ascending=False)
        
        for app, amount in app_spending.items():
            percentage = (amount / total_spent) * 100
            app_data[app] = {
                "amount": amount,
                "percentage": percentage
            }
    
    # Monthly spending trend
    monthly_trend = {}
    if not df.empty:
        df['month'] = df['date'].dt.strftime('%Y-%m')
        monthly_spending = df.groupby('month')['amount'].sum().to_dict()
        monthly_trend = dict(sorted(monthly_spending.items()))
    
    return render_template(
        'analytics.html',
        charts=charts,
        total_spent=total_spent,
        transaction_count=transaction_count,
        avg_transaction=avg_transaction,
        category_data=category_data,
        app_data=app_data,
        monthly_trend=monthly_trend,
        profile=user_data["profile"]
    )

@app.route('/share_with_parent')
def share_with_parent():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    parent_email = user_data["profile"]["parent_email"]
    share_enabled = user_data["profile"]["share_with_parents"]
    
    if not parent_email or not share_enabled:
        flash('Please enable sharing with parents in your profile', 'warning')
        return redirect(url_for('profile'))
    
    # In a real app, this would send an email to the parent
    # For the prototype, we'll just show a success message
    
    flash(f'Spending report has been shared with {parent_email}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/export_data')
def export_data():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_data = load_user_data(username)
    
    # For the prototype, we'll just return the raw JSON data
    return jsonify(user_data["transactions"])

# Sample data for testing
def add_sample_data(username):
    user_data = load_user_data(username)
    
    # Only add sample data if no transactions exist
    if not user_data["transactions"]:
        # Set profile data
        user_data["profile"] = {
            "name": "Sample User",
            "account_balance": 5000.00,
            "monthly_budget": 10000.00,
            "parent_email": "parent@example.com",
            "share_with_parents": True
        }
        
        # Sample transactions
        now = datetime.datetime.now()
        
        sample_transactions = [
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=20)).isoformat(),
                "amount": 150.00,
                "description": "Lunch at campus canteen",
                "upi_app": "Google Pay",
                "category": "Food"
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=18)).isoformat(),
                "amount": 500.00,
                "description": "Textbook for Computer Science",
                "upi_app": "PhonePe",
                "category": "Education"
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=15)).isoformat(),
                "amount": 200.00,
                "description": "Movie tickets",
                "upi_app": "Paytm",
                "category": "Entertainment"
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=12)).isoformat(),
                "amount": 50.00,
                "description": "Bus fare",
                "upi_app": "BHIM",
                "category": "Transportation"
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=10)).isoformat(),
                "amount": 800.00,
                "description": "New headphones",
                "upi_app": "Amazon Pay",
                "category": "Shopping"
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=8)).isoformat(),
                "amount": 120.00,
                "description": "Pizza delivery",
                "upi_app": "Google Pay",
                "category": "Food"
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=5)).isoformat(),
                "amount": 350.00,
                "description": "Project supplies",
                "upi_app": "PhonePe",
                "category": "Education"
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=3)).isoformat(),
                "amount": 180.00,
                "description": "Uber ride",
                "upi_app": "Paytm",
                "category": "Transportation"
            },
            {
                "id": str(uuid.uuid4()),
                "date": (now - datetime.timedelta(days=1)).isoformat(),
                "amount": 250.00,
                "description": "Mobile recharge",
                "upi_app": "PhonePe",
                "category": "Utilities"
            }
        ]
        
        user_data["transactions"] = sample_transactions
        save_user_data(username, user_data)
        return True
    
    return False

@app.route('/add_sample_data')
def route_add_sample_data():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    success = add_sample_data(username)
    
    if success:
        flash('Sample data added successfully', 'success')
    else:
        flash('Sample data not added (transactions already exist)', 'info')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
