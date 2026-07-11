import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
import db_connection
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Global style variables (only for reused styles)
header_button_style = "background-color:#14151c;color:white;border-radius:5px;padding:5px;font-size:16px;font-weight:bold;"
gray_frame_style = "background-color: #f0f0f0; border-radius: 5px;"
label_style = "font-size:16px;color:black;"
label_bold_style="font-size:16px;color:black;font-weight:bold;"
positive_change = "font-size:16px;color:green;font-weight:bold;"
negative_change = "font-size:16px;color:red;font-weight:bold;"
section_title_style = "font-size:18px;font-weight:bold;color:black;margin-bottom:10px;"

class PortfolioScreen(QMainWindow):
    def __init__(self,username): 
        super().__init__()

        self.username=username

        if self.username is None:
            print("Warning: no user logged in")

        self.setWindowTitle(f"Trading Simulator - {self.username}")
        self.resize(1500,750)
        self.setStyleSheet("background-color:#edf7f7;")

        self.setup_ui()
        
        # Load portfolio data on startup
        self.load_portfolio_data()
        
        # Set up auto-refresh timer
        self.setup_auto_refresh()
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(20,20,20,20)

        header_container=QFrame()
        header_container.setFixedHeight(80)
        header_container.setStyleSheet("background-color: #14151c; border-radius: 10px;")

        header_layout=QHBoxLayout()

        trading_title=QLabel("Crypto Trading Simulator")
        trading_title.setAlignment(Qt.AlignLeft)
        trading_title.setStyleSheet("""font-size:24px;font-weight:bold;color:white;""")
        

        dashboard_b=QPushButton()
        dashboard_b.setText("Dashboard")
        dashboard_b.setStyleSheet(header_button_style)
        dashboard_b.clicked.connect(self.open_dashboard)

        learning_b=QPushButton()
        learning_b.setText("Learning")
        learning_b.setStyleSheet(header_button_style)
        learning_b.clicked.connect(self.open_learning)

        leaderboard_b=QPushButton()
        leaderboard_b.setText("Leaderboard")
        leaderboard_b.setStyleSheet(header_button_style)
        leaderboard_b.clicked.connect(self.open_leaderboard)
        
        logout_b=QPushButton()
        logout_b.setText("Logout")
        logout_b.setStyleSheet(header_button_style)
        logout_b.clicked.connect(self.logout)
        
        
        header_layout.addWidget(trading_title)
        header_layout.addWidget(dashboard_b)
        header_layout.addWidget(learning_b)
        header_layout.addWidget(leaderboard_b)
        header_layout.addWidget(logout_b)
        header_container.setLayout(header_layout)
        main_layout.addWidget(header_container)

        # Portfolio Summary Cards - Trading Screen Pattern
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)

        # Total Balance Card
        total_balance = QFrame()
        total_balance.setStyleSheet(gray_frame_style)
        total_balance_layout = QHBoxLayout()

        total_balance_label = QLabel("Total Balance:")
        total_balance_label.setStyleSheet(label_style)

        self.total_balance_value = QLabel("Loading...")
        self.total_balance_value.setStyleSheet(label_bold_style)
        
        total_balance_layout.addWidget(total_balance_label)
        total_balance_layout.addWidget(self.total_balance_value)
        total_balance.setLayout(total_balance_layout)

        # Available Cash Card 
        available_cash = QFrame()
        available_cash.setStyleSheet(gray_frame_style)
        available_cash_layout = QHBoxLayout()

        available_cash_label = QLabel("Available Cash:")
        available_cash_label.setStyleSheet(label_style)

        self.available_cash_value = QLabel("Loading...")
        self.available_cash_value.setStyleSheet(label_bold_style)
        
        available_cash_layout.addWidget(available_cash_label)
        available_cash_layout.addWidget(self.available_cash_value)
        available_cash.setLayout(available_cash_layout)

        # 24h Change Card
        change_24h = QFrame()
        change_24h.setStyleSheet(gray_frame_style)
        change_24h_layout = QHBoxLayout()

        change_24h_label = QLabel("24h Change:")
        change_24h_label.setStyleSheet(label_style)

        self.change_24h_value = QLabel("Loading...")
        self.change_24h_value.setStyleSheet(label_bold_style)
        
        change_24h_layout.addWidget(change_24h_label)
        change_24h_layout.addWidget(self.change_24h_value)
        change_24h.setLayout(change_24h_layout)

        # Win Rate Card
        win_rate = QFrame()
        win_rate.setStyleSheet(gray_frame_style)
        win_rate_layout = QHBoxLayout()

        win_rate_label = QLabel("Win Rate:")
        win_rate_label.setStyleSheet(label_style)

        self.win_rate_value = QLabel("Loading...")
        self.win_rate_value.setStyleSheet(label_bold_style)
        
        win_rate_layout.addWidget(win_rate_label)
        win_rate_layout.addWidget(self.win_rate_value)
        win_rate.setLayout(win_rate_layout)

        summary_layout.addWidget(total_balance)
        summary_layout.addWidget(available_cash) 
        summary_layout.addWidget(change_24h)
        summary_layout.addWidget(win_rate)
        
        main_layout.addLayout(summary_layout)

        # Main content area - Holdings Table and Pie Chart
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(15)

        # Left side - Holdings Table
        holdings_container = QFrame()
        holdings_container.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; border: 1px solid #ddd;")
        holdings_container.setMaximumWidth(500)
        
        holdings_layout = QVBoxLayout()
        
        # Holdings Section
        holdings_title = QLabel("Current Holdings")
        holdings_title.setStyleSheet(section_title_style)

        # Holdings table - simplified columns
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(3)
        self.holdings_table.setHorizontalHeaderLabels(["Asset", "Quantity", "Value"])
        self.holdings_table.setMinimumHeight(200)
        self.holdings_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #f0f0f0;
                color: #333;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f0f0f0;
                color: #333;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #333;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #333;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        holdings_layout.addWidget(holdings_title)
        holdings_layout.addWidget(self.holdings_table)
        holdings_container.setLayout(holdings_layout)
        
        # Right side - Crypto Distribution Pie Chart
        chart_container = QFrame()
        chart_container.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; border: 1px solid #ddd;")
        
        chart_layout = QVBoxLayout()
        
        chart_title = QLabel("Crypto Distribution")
        chart_title.setStyleSheet(section_title_style)
        chart_title.setAlignment(Qt.AlignCenter)
        
        # Create matplotlib pie chart
        self.figure = Figure(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMaximumHeight(300)
        
        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.canvas)
        chart_container.setLayout(chart_layout)
        
        middle_layout.addWidget(holdings_container)
        middle_layout.addWidget(chart_container)
        
        main_layout.addLayout(middle_layout)
        
        # Bottom - Transaction History (Full Width)
        transactions_container = QFrame()
        transactions_container.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; border: 1px solid #ddd;")
        
        transactions_layout = QVBoxLayout()
        
        # Transaction History Section
        transactions_title = QLabel("Transaction History")
        transactions_title.setStyleSheet(section_title_style)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Type", "Asset", "Quantity", "Price"])
        self.transactions_table.setMinimumHeight(200)
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #333;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        transactions_layout.addWidget(transactions_title)
        transactions_layout.addWidget(self.transactions_table)
        transactions_container.setLayout(transactions_layout)
        
        main_layout.addSpacing(10)
        main_layout.addWidget(transactions_container)

        container=QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_portfolio_data(self):
        #Load portfolio data from database
        try:
            # Get portfolio summary
            portfolio_data = db_connection.get_portfolio_summary(self.username)
            
            # Update summary values
            self.total_balance_value.setText(f"${portfolio_data['total_balance']:.2f}")
            self.available_cash_value.setText(f"${portfolio_data['available_cash']:.2f}")
            
            # Update holdings table
            self.update_holdings_table(portfolio_data['holdings'])
            
            # Update pie chart
            self.update_pie_chart(portfolio_data['holdings'])
            
            # Calculate additional metrics with error handling
            try:
                self.calculate_additional_metrics(portfolio_data,self.username)
            except Exception as metrics_error:
                print(f"Error calculating metrics: {metrics_error}")
                # Set fallback values
                self.change_24h_value.setText("Unavailable")
                self.win_rate_value.setText("Unavailable")
            
            # Load transaction history
            self.load_transaction_history()
            
        except Exception as e:
            print(f"Error loading portfolio data: {e}")
            # Set fallback values for UI
            self.total_balance_value.setText("Connection Error")
            self.available_cash_value.setText("Connection Error")
            self.change_24h_value.setText("Unavailable")
            self.win_rate_value.setText("Unavailable")
            self.show_error_message(f"Database connection error. Please check your internet connection.")

    def update_holdings_table(self, holdings):
        #Update the holdings table with simplified columns
        self.holdings_table.setRowCount(len(holdings))
        
        for row, holding in enumerate(holdings):
            # Asset symbol
            crypto_item = QTableWidgetItem(holding['symbol'])
            crypto_item.setTextAlignment(Qt.AlignCenter)
            self.holdings_table.setItem(row, 0, crypto_item)
            
            # Quantity
            quantity_item = QTableWidgetItem(f"{holding['quantity']:.6f}")
            quantity_item.setTextAlignment(Qt.AlignRight)
            self.holdings_table.setItem(row, 1, quantity_item)
            
            # Current value
            value_item = QTableWidgetItem(f"${holding['current_value']:.2f}")
            value_item.setTextAlignment(Qt.AlignRight)
            self.holdings_table.setItem(row, 2, value_item)

    def update_pie_chart(self, holdings):
        #Update the pie chart with current holdings distribution
        if not holdings:
            return
            
        # Clear the figure
        self.figure.clear()
        
        # Prepare data for pie chart
        labels = []
        sizes = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        
        for holding in holdings:
            labels.append(f"{holding['symbol']}")
            sizes.append(float(holding['current_value']))
        
        # Create pie chart
        ax = self.figure.add_subplot(111)
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors[:len(holdings)], 
                                         autopct='%1.0f%%', startangle=90)
        
        ax.set_title('Portfolio Distribution', fontsize=14, fontweight='bold')
        
        # Make text smaller
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('white')
            autotext.set_weight('bold')
        
        # Refresh the canvas
        self.canvas.draw()
    
    def calculate_additional_metrics(self, portfolio_data, username):
        #Calculate 24h change and win rate
        
        # Get 24h change with error handling (function handles update logic internally)
        try:
            change_amount = db_connection.get_24h_balance_change(username)
            
            if change_amount >= 0:
                self.change_24h_value.setText(f"+${round(change_amount, 2)}")
                self.change_24h_value.setStyleSheet(positive_change)
            else:
                self.change_24h_value.setText(f"-${round(abs(change_amount), 2)}")
                self.change_24h_value.setStyleSheet(negative_change)
        except Exception as e:
            print(f"Error calculating 24h change: {e}")
            self.change_24h_value.setText("Unavailable")
        
        # Calculate win rate with error handling
        try:
            win_rate = db_connection.calculate_win_rate(username)
            self.win_rate_value.setText(f"{win_rate}%")
        except Exception as e:
            print(f"Error calculating win rate: {e}")
            self.win_rate_value.setText("Error")

    def load_transaction_history(self):
        #Load and display transaction history
        try:
            transactions = db_connection.get_recent_transactions(self.username, 15)
            
            if not transactions:
                self.transactions_table.setRowCount(1)
                no_data_item = QTableWidgetItem("No transactions found")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.transactions_table.setItem(0, 0, no_data_item)
                return
                
            self.transactions_table.setRowCount(len(transactions))
            default_color = QColor("#333")
            
            # Color map for transaction types
            type_colors = {
                "BUY":  (QColor(220, 248, 225), QColor(25, 135, 45)),
                "SELL": (QColor(255, 230, 230), QColor(200, 50, 50)),
            }
            
            for row, transaction in enumerate(transactions):
                parsed = db_connection.parse_transaction_string(transaction)
                
                if not parsed:
                    fallback_item = QTableWidgetItem(transaction)
                    self.transactions_table.setItem(row, 0, fallback_item)
                    continue
                
                # Date
                date_str = parsed['timestamp'][:10]
                date_item = QTableWidgetItem(date_str)
                date_item.setTextAlignment(Qt.AlignCenter)
                date_item.setForeground(default_color)
                self.transactions_table.setItem(row, 0, date_item)
                
                # Type (BUY/SELL) with color coding
                type_item = QTableWidgetItem(parsed['transaction_type'])
                type_item.setTextAlignment(Qt.AlignCenter)
                if parsed['transaction_type'] in type_colors:
                    bg, fg = type_colors[parsed['transaction_type']]
                    type_item.setBackground(bg)
                    type_item.setForeground(fg)
                self.transactions_table.setItem(row, 1, type_item)
                
                # Asset
                crypto_item = QTableWidgetItem(parsed['crypto_symbol'])
                crypto_item.setTextAlignment(Qt.AlignCenter)
                crypto_item.setForeground(default_color)
                self.transactions_table.setItem(row, 2, crypto_item)
                
                # Quantity
                qty_item = QTableWidgetItem(f"{parsed['quantity']:.4f}")
                qty_item.setTextAlignment(Qt.AlignRight)
                qty_item.setForeground(default_color)
                self.transactions_table.setItem(row, 3, qty_item)
                
                # Price
                price_item = QTableWidgetItem(f"${parsed['price']:.2f}")
                price_item.setTextAlignment(Qt.AlignRight)
                price_item.setForeground(default_color)
                self.transactions_table.setItem(row, 4, price_item)
                    
        except Exception as e:
            print(f"Error loading transaction history: {e}")
            self.transactions_table.setRowCount(1)
            error_item = QTableWidgetItem(f"Error loading transactions: {e}")
            error_item.setTextAlignment(Qt.AlignCenter)
            self.transactions_table.setItem(0, 0, error_item)

    def setup_auto_refresh(self):
        """Set up auto-refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_portfolio_data)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds

    def show_error_message(self, message):
        """Show error message dialog"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()

    def open_dashboard(self):
        from trading_screen import TradingScreen
        self.trading_screen=TradingScreen(self.username)
        self.trading_screen.show()
        self.close() 
    def open_learning(self):
        from learning import LearningScreen
        self.learning_screen=LearningScreen(self.username)    
        self.learning_screen.show()
        self.close()

    def open_leaderboard(self):
        from leaderboard import LeaderBoardScreen
        self.leaderboard_screen=LeaderBoardScreen(self.username)    
        self.leaderboard_screen.show()
        self.close()

    def logout(self):
        from login_screen import LoginWindow
        self.login_screen=LoginWindow()
        self.login_screen.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PortfolioScreen("superuser")
    window.show()
    sys.exit(app.exec())