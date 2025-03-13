# UPI Money Tracker

A Python-based application to track and manage UPI transactions for students.

## Problem Statement
Young people often lack money management skills. With the increased use of UPI apps, there's no centralized way to track spending across different platforms, leading to poor financial management.

## Solution
UPI Money Tracker is a comprehensive platform that:
1. Tracks spending across all UPI apps
2. Categorizes expenses automatically
3. Provides balance reminders and alerts
4. Offers money-saving tips
5. Allows sharing financial details with parents (useful for hostel students)

## Features

### Core Features
- **Multi-UPI Tracking**: Track spending across GooglePay, PhonePe, Paytm, BHIM, WhatsApp Pay, and other UPI apps
- **Expense Categorization**: Automatically categorize spending (Food, Transportation, Education, etc.)
- **Financial Dashboard**: View your spending patterns through intuitive charts and graphs
- **Balance Reminders**: Get alerts when your account balance runs low
- **Money Saving Tips**: Receive personalized tips to improve spending habits
- **Parent Sharing**: Share spending reports with parents or guardians
- **Data Export**: Export your transaction data for external analysis

### Technical Features
- Python-based application with both CLI and web interfaces
- Data visualization with matplotlib and seaborn
- Secure user authentication
- Local data storage with JSON
- Responsive web interface built with Flask

## Project Structure

```
upi-tracker/
├── app.py                  # Web application entry point
├── cli_tracker.py          # Command-line interface
├── data/                   # Data storage directory
├── static/                 # Static files (CSS, JS, images)
│   └── charts/             # Generated chart images
├── templates/              # HTML templates
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

## Setup Instructions

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Installation

1. Clone the repository or download the source code:
   ```
   git clone https://github.com/per-shree/upi-tracker.git
   cd upi-tracker
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the CLI Application

To run the command-line interface version:
```
python cli_tracker.py
```

### Running the Web Application

To run the web-based interface:
```
python app.py
```
Then open http://localhost:5000 in your web browser.

## Usage Guide

### Command-Line Interface
1. When you run the application for the first time, you'll be asked to set up your profile
2. Use the main menu to navigate through different options
3. Add transactions as you make UPI payments
4. View statistics and visualizations to track your spending

### Web Interface
1. Register a new account
2. Set up your profile with current balance and monthly budget
3. Add transactions manually
4. Explore the dashboard for spending insights
5. Use the analytics page for detailed spending breakdowns
6. Share reports with parents if needed

## Requirements

```
Flask==2.0.1
matplotlib==3.4.3
pandas==1.3.3
seaborn==0.11.2
tabulate==0.8.9
colorama==0.4.4
Werkzeug==2.0.1
```

## Presentation Points for Committee

1. **Problem Relevance**: Addresses a common issue among students with digital payment habits
2. **Technical Implementation**: Demonstrates Python programming, data visualization, and web development skills
3. **User Experience**: Intuitive interfaces for both technical and non-technical users
4. **Financial Education**: Promotes good money management habits through tips and analytics
5. **Scalability**: Can be extended to include direct UPI API integration in future versions
6. **Collaborative Potential**: Modular structure allows classmates to contribute to different components
7. **Educational Value**: Helps students learn about financial management

## Future Enhancements

1. **Direct UPI Integration**: Connect with UPI APIs to automatically fetch transaction data
2. **Machine Learning**: Implement ML for smarter categorization and spending predictions
3. **Mobile App**: Develop companion mobile applications for Android and iOS
4. **Budget Planning**: Add features for setting category-specific budgets
5. **Savings Goals**: Allow users to set and track financial goals
6. **Peer Comparison**: Anonymous comparison with peers to benchmark spending habits
7. **Financial Insights**: More advanced analytics and personalized financial advice

## Contribution Guidelines for Classmates

If you're collaborating on this project with classmates, here are potential areas for contribution:

1. **UI/UX Design**: Enhance the user interface and experience
2. **Data Visualization**: Improve or add new visualization charts
3. **Machine Learning**: Implement smart categorization or predictions
4. **Security**: Enhance data security and privacy features
5. **Testing**: Create comprehensive test cases and scenarios
6. **Documentation**: Improve user guides and documentation
7. **Mobile Development**: Create mobile app versions

## About This Project

This project was developed as a prototype to address the lack of centralized UPI transaction tracking for students. It aims to promote better financial habits and management skills among young adults who are new to managing their finances independently.
