import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import QSize, Qt,QTimer
from PySide6.QtGui import QPixmap,QColor
import db_connection

# Global style variables (only for reused styles)
header_button_style = "background-color:#14151c;color:white;border-radius:5px;padding:5px;font-size:16px;font-weight:bold;"
module_frame_style = "background-color: #f0f0f0; border-radius: 5px; padding: 12px;"
label_bold_style = "font-size:16px;color:black;font-weight:bold;"
section_title_style = "font-size:18px;font-weight:bold;color:black;margin-bottom:10px;"

class LeaderBoardScreen(QMainWindow):
    def __init__(self,username): 
        super().__init__()

        self.username=username

        if self.username is None:
            print("Warning: no user logged in")

        self.setWindowTitle(f"Trading Simulator - {self.username}")
        self.resize(1500,750)
        self.setStyleSheet("background-color:#edf7f7;")

        self.setup_ui()
        self.load_leaderboard()
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20,20,20,20)

        header_container=QFrame()
        header_container.setFixedHeight(80)
        header_container.setStyleSheet("background-color: #14151c; border-radius: 10px;")

        header_layout=QHBoxLayout()

        trading_title=QLabel("Crypto Trading Simulator")
        trading_title.setAlignment(Qt.AlignLeft)
        trading_title.setStyleSheet("font-size:24px;font-weight:bold;color:white;")
        

        portfolio_b=QPushButton()
        portfolio_b.setText("Portfolio")
        portfolio_b.setStyleSheet(header_button_style)
        portfolio_b.clicked.connect(self.open_portfolio)

        dashboard_b=QPushButton()
        dashboard_b.setText("Dashboard")
        dashboard_b.setStyleSheet(header_button_style)
        dashboard_b.clicked.connect(self.open_dashboard)

        learning_b=QPushButton()
        learning_b.setText("Learning")
        learning_b.setStyleSheet(header_button_style)
        learning_b.clicked.connect(self.open_learning)

        
        logout_b=QPushButton()
        logout_b.setText("Logout")
        logout_b.setStyleSheet(header_button_style)
        logout_b.clicked.connect(self.logout)
        
        
        
        header_layout.addWidget(trading_title)
        header_layout.addWidget(dashboard_b)
        header_layout.addWidget(portfolio_b)
        header_layout.addWidget(learning_b  )
        header_layout.addWidget(logout_b)
        header_container.setLayout(header_layout)
        main_layout.addWidget(header_container)


        #Leader Board
        # Bottom - Transaction History (Full Width)
        leaderboard_container = QFrame()
        leaderboard_container.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; border: 1px solid #ddd;")
        
        leaderboard_layout = QVBoxLayout()
        
        # Transaction History Section
        leaderboard_title = QLabel("Leader Board - Top Users by Total Balance")
        leaderboard_title.setStyleSheet(section_title_style)

        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(3)
        self.leaderboard_table.setHorizontalHeaderLabels(["Rank", "Username", "Total Balance"])
        self.leaderboard_table.setMinimumHeight(400)
        self.leaderboard_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #f0f0f0;
                color: black;
            }
            QTableWidget::item {
                color: black;
                padding: 4px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: black;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        leaderboard_layout.addWidget(leaderboard_title)
        leaderboard_layout.addWidget(self.leaderboard_table)
        leaderboard_container.setLayout(leaderboard_layout)
        
        main_layout.addLayout(QHBoxLayout())  # Add some spacing
        main_layout.addWidget(leaderboard_container)


        

        container=QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_leaderboard(self):
        #Load and display leaderboard data
        try:
            # Get leaderboard data from database
            leaderboard_data = db_connection.get_leaderboard_data()
            self.leaderboard_table.setRowCount(len(leaderboard_data))
            
            for row, user_data in enumerate(leaderboard_data):
                # Rank
                rank_item = QTableWidgetItem(str(row + 1))
                rank_item.setTextAlignment(Qt.AlignCenter)
                
                # Username
                username_item = QTableWidgetItem(user_data['username'])
                username_item.setTextAlignment(Qt.AlignCenter)
                
                # Total Balance
                balance_item = QTableWidgetItem(f"${user_data['total_balance']:.2f}")
                balance_item.setTextAlignment(Qt.AlignRight)
                
                # Add items to table
                self.leaderboard_table.setItem(row, 0, rank_item)
                self.leaderboard_table.setItem(row, 1, username_item)
                self.leaderboard_table.setItem(row, 2, balance_item)
                    
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            # Show error in table
            self.leaderboard_table.setRowCount(1)
            error_item = QTableWidgetItem(f"Error loading leaderboard: {e}")
            error_item.setTextAlignment(Qt.AlignCenter)
            self.leaderboard_table.setItem(0, 0, error_item)

    

    def open_dashboard(self):
        from trading_screen import TradingScreen
        self.trading_screen=TradingScreen(self.username)
        self.trading_screen.show()
        self.close() 
    def open_portfolio(self):
        from portfolio import PortfolioScreen
        self.portfolio_screen=PortfolioScreen(self.username)    
        self.portfolio_screen.show()
        self.close()

    def open_learning(self):
        from learning import LearningScreen
        self.trading_screen=LearningScreen(self.username)
        self.trading_screen.show()
        self.close() 

    def logout(self):
        from login_screen import LoginWindow
        self.login_screen=LoginWindow()
        self.login_screen.show()
        self.close()

if __name__ =="__main__":
    app=QApplication(sys.argv)
    window=LeaderBoardScreen("superuser")
    window.show()
    sys.exit(app.exec())