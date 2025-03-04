import os
import datetime
import json
import csv
import matplotlib.pyplot as plt
from tabulate import tabulate
import pandas as pd
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)

class UPITracker:
    def __init__(self):
        self.data_dir = "data"
        self.transactions_file = os.path.join(self.data_dir, "transactions.json")
        self.user_file = os.path.join(self.data_dir, "user_info.json")
        self.categories = [
            "Food", "Transportation", "Shopping", "Entertainment", 
            "Education", "Utilities", "Health", "Other"
        ]
        self.upi_apps = [
            "Google Pay", "PhonePe", "Paytm", "Amazon Pay", 
            "BHIM", "WhatsApp Pay", "Other"
        ]
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Initialize or load user data
        if os.path.exists(self.user_file):
            with open(self.user_file, 'r') as f:
                self.user_info = json.load(f)
        else:
            self.user_info = {
                "name": "",
                "account_balance": 0,
                "monthly_budget": 0,
                "parent_email": "",
                "share_with_parents": False
            }
            self.save_user_info()
            
        # Initialize or load transaction data
        if os.path.exists(self.transactions_file):
            with open(self.transactions_file, 'r') as f:
                self.transactions = json.load(f)
        else:
            self.transactions = []
            self.save_transactions()

    def save_transactions(self):
        with open(self.transactions_file, 'w') as f:
            json.dump(self.transactions, f, indent=4)

    def save_user_info(self):
        with open(self.user_file, 'w') as f:
            json.dump(self.user_info, f, indent=4)

    def setup_user(self):
        print(Fore.CYAN + "\n===== User Setup =====" + Style.RESET_ALL)
        self.user_info["name"] = input("Enter your name: ")
        
        try:
            self.user_info["account_balance"] = float(input("Enter your current account balance: ₹"))
            self.user_info["monthly_budget"] = float(input("Enter your monthly budget: ₹"))
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter numbers only." + Style.RESET_ALL)
            return self.setup_user()
            
        self.user_info["parent_email"] = input("Enter parent's email (leave empty if not applicable): ")
        
        share = input("Share spending details with parents? (yes/no): ").lower()
        self.user_info["share_with_parents"] = share == "yes"
        
        self.save_user_info()
        print(Fore.GREEN + "User setup completed successfully!" + Style.RESET_ALL)

    def add_transaction(self):
        print(Fore.CYAN + "\n===== Add New Transaction =====" + Style.RESET_ALL)
        
        # Get transaction details
        try:
            amount = float(input("Enter transaction amount: ₹"))
            if amount <= 0:
                print(Fore.RED + "Amount must be greater than 0." + Style.RESET_ALL)
                return
        except ValueError:
            print(Fore.RED + "Invalid amount. Please enter a number." + Style.RESET_ALL)
            return
            
        description = input("Enter description: ")
        
        # Select UPI app
        print("\nSelect UPI app:")
        for i, app in enumerate(self.upi_apps):
            print(f"{i+1}. {app}")
            
        try:
            app_choice = int(input("Enter your choice (number): "))
            if not 1 <= app_choice <= len(self.upi_apps):
                print(Fore.RED + "Invalid choice." + Style.RESET_ALL)
                return
            upi_app = self.upi_apps[app_choice-1]
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)
            return
            
        # Select category
        print("\nSelect category:")
        for i, category in enumerate(self.categories):
            print(f"{i+1}. {category}")
            
        try:
            category_choice = int(input("Enter your choice (number): "))
            if not 1 <= category_choice <= len(self.categories):
                print(Fore.RED + "Invalid choice." + Style.RESET_ALL)
                return
            category = self.categories[category_choice-1]
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)
            return
            
        # Create transaction record
        transaction = {
            "id": len(self.transactions) + 1,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "description": description,
            "upi_app": upi_app,
            "category": category
        }
        
        # Update account balance
        self.user_info["account_balance"] -= amount
        
        # Save transaction and user info
        self.transactions.append(transaction)
        self.save_transactions()
        self.save_user_info()
        
        print(Fore.GREEN + "Transaction added successfully!" + Style.RESET_ALL)
        
        # Check if balance is low
        if self.user_info["account_balance"] < 0.2 * self.user_info["monthly_budget"]:
            print(Fore.RED + f"\nWARNING: Your balance (₹{self.user_info['account_balance']:.2f}) is less than 20% of your monthly budget!" + Style.RESET_ALL)

    def view_transactions(self, limit=10):
        if not self.transactions:
            print(Fore.YELLOW + "No transactions found." + Style.RESET_ALL)
            return
            
        print(Fore.CYAN + f"\n===== Recent Transactions (Last {min(limit, len(self.transactions))}) =====" + Style.RESET_ALL)
        
        transactions = sorted(self.transactions, key=lambda x: x["date"], reverse=True)[:limit]
        
        table_data = []
        for t in transactions:
            table_data.append([
                t["id"],
                t["date"],
                f"₹{t['amount']:.2f}",
                t["description"],
                t["upi_app"],
                t["category"]
            ])
            
        headers = ["ID", "Date", "Amount", "Description", "UPI App", "Category"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def view_statistics(self):
        if not self.transactions:
            print(Fore.YELLOW + "No transactions found. Add some transactions first." + Style.RESET_ALL)
            return
            
        print(Fore.CYAN + "\n===== Spending Statistics =====" + Style.RESET_ALL)
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(self.transactions)
        
        # Current month transactions
        current_month = datetime.datetime.now().strftime("%Y-%m")
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.strftime('%Y-%m')
        monthly_df = df[df['month'] == current_month]
        
        # Total spending
        total_spent = df['amount'].sum()
        monthly_spent = monthly_df['amount'].sum() if not monthly_df.empty else 0
        
        print(f"Total spending: {Fore.RED}₹{total_spent:.2f}{Style.RESET_ALL}")
        print(f"This month's spending: {Fore.RED}₹{monthly_spent:.2f}{Style.RESET_ALL}")
        print(f"Current balance: {Fore.GREEN}₹{self.user_info['account_balance']:.2f}{Style.RESET_ALL}")
        
        # Category-wise spending
        print(Fore.CYAN + "\nCategory-wise Spending:" + Style.RESET_ALL)
        category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        for category, amount in category_spending.items():
            percentage = (amount / total_spent) * 100
            print(f"{category}: ₹{amount:.2f} ({percentage:.1f}%)")
            
        # UPI app-wise spending
        print(Fore.CYAN + "\nUPI App-wise Spending:" + Style.RESET_ALL)
        app_spending = df.groupby('upi_app')['amount'].sum().sort_values(ascending=False)
        
        for app, amount in app_spending.items():
            percentage = (amount / total_spent) * 100
            print(f"{app}: ₹{amount:.2f} ({percentage:.1f}%)")
            
        # Budget tracking
        if self.user_info["monthly_budget"] > 0:
            budget_used = (monthly_spent / self.user_info["monthly_budget"]) * 100
            print(Fore.CYAN + "\nBudget Tracking:" + Style.RESET_ALL)
            print(f"Monthly budget: ₹{self.user_info['monthly_budget']:.2f}")
            print(f"Budget used: {budget_used:.1f}%")
            
            if budget_used > 80:
                print(Fore.RED + "Warning: You've used more than 80% of your monthly budget!" + Style.RESET_ALL)
                
        # Money saving tips
        self.show_saving_tips()

    def visualize_spending(self):
        if not self.transactions:
            print(Fore.YELLOW + "No transactions found. Add some transactions first." + Style.RESET_ALL)
            return
            
        df = pd.DataFrame(self.transactions)
        df['date'] = pd.to_datetime(df['date'])
        
        # Create a figure with subplots
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Category-wise spending (Pie chart)
        plt.subplot(2, 2, 1)
        category_spending = df.groupby('category')['amount'].sum()
        plt.pie(category_spending, labels=category_spending.index, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Spending by Category')
        
        # Plot 2: UPI app-wise spending (Pie chart)
        plt.subplot(2, 2, 2)
        app_spending = df.groupby('upi_app')['amount'].sum()
        plt.pie(app_spending, labels=app_spending.index, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Spending by UPI App')
        
        # Plot 3: Daily spending over time (Line chart)
        plt.subplot(2, 1, 2)
        daily_spending = df.groupby(df['date'].dt.date)['amount'].sum()
        plt.plot(daily_spending.index, daily_spending.values, marker='o')
        plt.xlabel('Date')
        plt.ylabel('Amount (₹)')
        plt.title('Daily Spending')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save the visualization
        vis_dir = "visualizations"
        if not os.path.exists(vis_dir):
            os.makedirs(vis_dir)
            
        plt.savefig(os.path.join(vis_dir, "spending_analysis.png"))
        plt.close()
        
        print(Fore.GREEN + f"Visualizations saved to {vis_dir}/spending_analysis.png" + Style.RESET_ALL)

    def export_data(self):
        if not self.transactions:
            print(Fore.YELLOW + "No transactions found. Add some transactions first." + Style.RESET_ALL)
            return
            
        print(Fore.CYAN + "\n===== Export Data =====" + Style.RESET_ALL)
        print("1. Export as CSV")
        print("2. Export as JSON")
        print("3. Back to main menu")
        
        try:
            choice = int(input("Enter your choice: "))
            
            if choice == 1:
                export_file = os.path.join(self.data_dir, "transactions_export.csv")
                with open(export_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self.transactions[0].keys())
                    writer.writeheader()
                    writer.writerows(self.transactions)
                print(Fore.GREEN + f"Data exported to {export_file}" + Style.RESET_ALL)
                
            elif choice == 2:
                export_file = os.path.join(self.data_dir, "transactions_export.json")
                with open(export_file, 'w') as f:
                    json.dump(self.transactions, f, indent=4)
                print(Fore.GREEN + f"Data exported to {export_file}" + Style.RESET_ALL)
                
            elif choice == 3:
                return
                
            else:
                print(Fore.RED + "Invalid choice." + Style.RESET_ALL)
                
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)

    def show_saving_tips(self):
        tips = [
            "Track your daily expenses and set spending limits for each category.",
            "Cook at home instead of ordering food to save on food expenses.",
            "Use student discounts wherever available.",
            "Plan your purchases and avoid impulse buying.",
            "Use public transportation instead of cabs when possible.",
            "Cancel unused subscriptions.",
            "Wait 24 hours before making non-essential purchases.",
            "Set aside a small percentage of your income as savings."
        ]
        
        print(Fore.CYAN + "\n===== Money Saving Tips =====" + Style.RESET_ALL)
        tip = tips[len(self.transactions) % len(tips)]  # Show different tips based on transaction count
        print(f"💡 {tip}")

    def share_with_parent(self):
        if not self.user_info["parent_email"]:
            print(Fore.YELLOW + "Parent email not set. Please update your profile." + Style.RESET_ALL)
            return
            
        if not self.user_info["share_with_parents"]:
            print(Fore.YELLOW + "Sharing with parents is disabled. Please update your profile." + Style.RESET_ALL)
            return
            
        print(Fore.CYAN + "\n===== Share With Parents =====" + Style.RESET_ALL)
        print(f"This would send an email to {self.user_info['parent_email']} with your spending details.")
        print("(Email functionality will be implemented in the full version)")
        
        # In a real implementation, this would create and send an email with a spending report
        confirm = input("Do you want to continue? (yes/no): ").lower()
        
        if confirm == "yes":
            print(Fore.GREEN + "Spending report has been shared with your parents." + Style.RESET_ALL)
            
            # Simulate email content
            print("\nEmail preview:")
            print(f"To: {self.user_info['parent_email']}")
            print(f"Subject: {self.user_info['name']}'s Spending Report")
            print("\nDear Parent,")
            print(f"\nHere is the spending report for {self.user_info['name']}:")
            print(f"Current balance: ₹{self.user_info['account_balance']:.2f}")
            print(f"Monthly budget: ₹{self.user_info['monthly_budget']:.2f}")
            
            if self.transactions:
                total_spent = sum(t["amount"] for t in self.transactions)
                print(f"Total spent: ₹{total_spent:.2f}")
                
                # Get recent transactions
                recent = sorted(self.transactions, key=lambda x: x["date"], reverse=True)[:5]
                print("\nRecent transactions:")
                for t in recent:
                    print(f"- {t['date']}: ₹{t['amount']:.2f} on {t['category']} via {t['upi_app']}")

    def run(self):
        # Check if user needs to set up
        if not self.user_info["name"]:
            self.setup_user()
        
        while True:
            print(Fore.CYAN + "\n===== UPI Tracker - Main Menu =====" + Style.RESET_ALL)
            print(f"Welcome, {self.user_info['name']}!")
            print(f"Current balance: {Fore.GREEN}₹{self.user_info['account_balance']:.2f}{Style.RESET_ALL}")
            
            print("\n1. Add transaction")
            print("2. View recent transactions")
            print("3. View spending statistics")
            print("4. Visualize spending")
            print("5. Export data")
            print("6. Share with parent")
            print("7. Update profile")
            print("8. Exit")
            
            try:
                choice = int(input("\nEnter your choice: "))
                
                if choice == 1:
                    self.add_transaction()
                elif choice == 2:
                    self.view_transactions()
                elif choice == 3:
                    self.view_statistics()
                elif choice == 4:
                    self.visualize_spending()
                elif choice == 5:
                    self.export_data()
                elif choice == 6:
                    self.share_with_parent()
                elif choice == 7:
                    self.setup_user()
                elif choice == 8:
                    print(Fore.GREEN + "Thank you for using UPI Tracker. Goodbye!" + Style.RESET_ALL)
                    break
                else:
                    print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)
                    
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)


# Add some sample data
def add_sample_data(tracker):
    sample_transactions = [
        {
            "id": 1,
            "date": (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 150.00,
            "description": "Lunch at campus canteen",
            "upi_app": "Google Pay",
            "category": "Food"
        },
        {
            "id": 2,
            "date": (datetime.datetime.now() - datetime.timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 500.00,
            "description": "Textbook for Computer Science",
            "upi_app": "PhonePe",
            "category": "Education"
        },
        {
            "id": 3,
            "date": (datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 200.00,
            "description": "Movie tickets",
            "upi_app": "Paytm",
            "category": "Entertainment"
        },
        {
            "id": 4,
            "date": (datetime.datetime.now() - datetime.timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 50.00,
            "description": "Bus fare",
            "upi_app": "BHIM",
            "category": "Transportation"
        },
        {
            "id": 5,
            "date": (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 800.00,
            "description": "New headphones",
            "upi_app": "Amazon Pay",
            "category": "Shopping"
        }
    ]
    
    # Check if transactions already exist
    if not tracker.transactions:
        tracker.transactions = sample_transactions
        tracker.save_transactions()
        print(Fore.GREEN + "Sample data added successfully!" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "Data already exists. Sample data not added." + Style.RESET_ALL)


if __name__ == "__main__":
    print(Fore.CYAN + """
    ╔════════════════════════════════════════╗
    ║          UPI EXPENSE TRACKER           ║
    ╠════════════════════════════════════════╣
    ║ Track • Analyze • Save • Share         ║
    ╚════════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    tracker = UPITracker()
    
    # Ask if user wants to add sample data
    if not tracker.transactions:
        add_sample = input("Would you like to add sample data for testing? (yes/no): ").lower()
        if add_sample == "yes":
            add_sample_data(tracker)
    
    tracker.run()
