import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap

# Global style variables (only for reused styles)
header_button_style = "background-color:#14151c;color:white;border-radius:5px;padding:5px;font-size:16px;font-weight:bold;"
module_frame_style = "background-color: #f0f0f0;color:black; border-radius: 5px; padding: 12px;text-align: left; border: none; font-weight: bold;"
label_bold_style = "font-size:16px;color:black;font-weight:bold;"

class Module_1(QWidget):
    def __init__(self,username): 
        super().__init__()

        self.username=username

        if self.username is None:
            print("Warning: no user logged in")

        self.setWindowTitle(f"Module 1 - {self.username}")
        self.resize(1500,750)
        self.setStyleSheet("background-color:#edf7f7;")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20,20,20,20)

        title=QLabel()
        title.setText("Module 1")
        title.setStyleSheet("font-size:24px;font-weight:bold;color:white;")

        main_layout.addWidget(title)
        container=QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)



class LearningScreen(QMainWindow):
    def __init__(self,username): 
        super().__init__()

        self.username=username

        if self.username is None:
            print("Warning: no user logged in")

        self.setWindowTitle(f"Trading Simulator - {self.username}")
        self.resize(1500,750)
        self.setStyleSheet("background-color:#edf7f7;")

        self.setup_ui()
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
        header_layout.addWidget(portfolio_b)
        header_layout.addWidget(leaderboard_b)
        header_layout.addWidget(logout_b)
        header_container.setLayout(header_layout)
        main_layout.addWidget(header_container)

        # Main content area with Course Modules
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left side - Course Modules
        modules_container = QFrame()
        modules_container.setStyleSheet("background-color: white; border-radius: 10px; padding: 20px; border: 1px solid #ddd;")
        modules_container.setMaximumWidth(350)
        modules_container.setMinimumHeight(500)
        
        modules_layout = QVBoxLayout()
        
        # Course Modules Header
        modules_header = QLabel("Course Modules")
        modules_header.setStyleSheet("font-size:20px;font-weight:bold;color:black;margin-bottom:10px;")
        
        # Progress section
        self.progress_label = QLabel("Progress 0%")
        self.progress_label.setStyleSheet("font-size:14px;color:#666;margin-bottom:5px;")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        self.total_modules = 4
        self.visited_modules = set()
        
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: #f0f0f0;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        modules_layout.addWidget(modules_header)
        modules_layout.addWidget(self.progress_label)
        modules_layout.addWidget(self.progress_bar)
        
        # Add some spacing
        modules_layout.addSpacing(20)
        
        # Module content data
        self.module_content = {
            1: {
                "title": "Getting Started with Crypto Trading",
                "content": """Welcome to cryptocurrency trading!

Cryptocurrency is a digital or virtual form of currency that uses cryptography for security. Bitcoin, created in 2009, was the first cryptocurrency and remains the most well-known.

Fun fact: In 2010, someone paid 10,000 Bitcoin for two pizzas. Those coins would be worth over $900 million today!

Key Concepts:
• Market Cap: Total value of all coins in circulation (price × supply)
• Volatility: How wildly the price swings — crypto is famous for 20%+ daily moves
• Liquidity: How easily you can buy or sell without moving the price
• HODL: Hold On for Dear Life — a meme-turned-strategy for long-term believers
• FOMO: Fear of Missing Out — the urge to buy when prices are already pumping
• Whale: Someone holding a massive amount of crypto who can move markets

Getting Started:
1. Learn the basics of blockchain technology
2. Understand different types of cryptocurrencies
3. Start with a simulator like this one — practice with fake money first!
4. When going live, begin with small investments
5. Never invest more than you can afford to lose

Popular Cryptocurrencies:
• Bitcoin (BTC) - The original "digital gold", capped at 21 million coins forever
• Ethereum (ETH) - Not just money but a platform for apps (DeFi, NFTs, games)
• Solana (SOL) - Built for speed: 65,000   /sec vs Ethereum's ~30
• Cardano (ADA) - The "academic" blockchain, built through peer-reviewed research

Reality Check: 95% of day traders lose money. The crypto market is open 24/7, highly volatile, and full of scams. This simulator exists to help you learn without financial risk."""
            },
            2: {
                "title": "Technical Analysis Fundamentals", 
                "content": """Technical Analysis is like reading the body language of the market. Instead of studying a company's finances, you study how traders are behaving — through price patterns, volume, and indicators.

Core belief: Price already reflects all available information.

Reading Candlesticks:
• Green candle = Price went UP — buyers won that round
• Red candle = Price went DOWN — sellers won that round
• Long wick up = Price tried to go higher but got rejected
• Long wick down = Price tried to go lower but buyers stepped in
• Tiny body (Doji) = Neither side won — big move coming soon

Support & Resistance — The Invisible Walls:
• Support = A floor where buyers consistently step in
• Resistance = A ceiling where sellers consistently take profits
• Real example: Bitcoin bounced off $30,000 support multiple times in 2021. When it finally broke below, it crashed to $17,000. That's how powerful these levels are.

Key Indicators (available in the Dashboard):
• SMA (Simple Moving Average) — Average closing price over X periods. Our simulator uses a 20-period SMA. Price above SMA = bullish, below = bearish.
• RSI (Relative Strength Index) — A 0-100 momentum scale:
    - Above 70 = Overbought (price may pull back)
    - Below 30 = Oversold (price may bounce)
    - 50 line = Dividing line between bullish and bearish
• Pro tip: RSI divergence (price makes new high but RSI doesn't) often predicts reversals

Time Frames:
• 1m, 5m, 15m — Day trading (fast, noisy, stressful)
• 1h, 4h — Swing trading (balanced, less noise)
• 1d, 1w — Position trading (big picture, patient)

Tip: Try using the SMA and RSI indicators in the Dashboard chart right now!"""
            },
            3: {
                "title": "Risk Management Essentials",
                "content": """It's not bad analysis that kills most traders — it's bad risk management. A trader who's right 60% of the time can still lose money if their losses are bigger than their wins.

The Brutal Math of Losses:
• 10% loss → need 11% gain to recover
• 25% loss → need 33% gain to recover
• 50% loss → need 100% gain (you must DOUBLE just to get back!)
• 90% loss → need 900% gain (nearly impossible)
This is why protecting your capital matters more than chasing profits.

The 1-2% Rule:
• Professional traders never risk more than 1-2% of their portfolio on a single trade
• Example: You have $10,000. Using the 1% rule, max loss per trade = $100

Stop Losses — Your Safety Net:
Think of a stop loss as a seatbelt for your portfolio — you hope you never need it, but it saves you when things go wrong.
• Set it BEFORE you enter the trade
• Swing trades: 3-5% below entry
• Day trades: 1-2% below entry
• Trailing stop: Moves up as price increases, locks in profits
• Golden rule: NEVER move your stop loss further away

Risk/Reward Ratio:
Before every trade, ask: "How much can I lose vs. how much can I gain?"
• 1:1 — Risk $1 to make $1 (not worth it)
• 1:2 — Risk $1 to make $2 (minimum target for most traders)
• 1:3+ — Risk $1 to make $3+ (excellent, be patient for these)
• With a 1:2 ratio, you only need to be right 34% of the time to break even!

Emotional Control:
• FOMO leads to bad decisions — don't chase pumps
• Don't revenge trade after losses
• Take profits systematically — don't be greedy
• Keep a trading journal to track performance

Portfolio Allocation:
• 70% in established coins (BTC, ETH) — your foundation
• 20% in mid-cap altcoins — growth potential
• 10% in high-risk plays — moonshots you can afford to lose

Critical Rule: Never trade with money you need for rent, food, or bills."""
            },
            4: {
                "title": "Trading Strategies Overview",
                "content": """There's no single "best" strategy. The right approach depends on your personality, schedule, and risk tolerance.

Day Trading
• Open and close all positions within the same day
• Time needed: 4-8 hours/day of screen time
• Charts: 1m, 5m, 15m candles
• Pros: Quick feedback, no overnight risk
• Cons: Very stressful, high fees, requires discipline
• Real talk: Most pro day traders spent 1-2 years losing money before becoming profitable

Swing Trading
• Ride price "swings" — hold for days to weeks
• Time needed: 30 min-1 hour/day to check charts
• Charts: 4h and 1d candles
• Pros: Less stressful, works alongside a day job
• Cons: Overnight risk, requires patience
• Best for: Part-time traders and beginners

HODLing (Buy & Hold)
• Buy promising projects and hold for months or years
• The simplest strategy — patience beats trading for most people
• If you bought $1,000 of Bitcoin in January 2020 and just held it, you'd have $5,000+ by 2025 — despite multiple "crashes"

DCA (Dollar Cost Averaging)
• Invest a fixed amount on a regular schedule regardless of price
• Example: Buy $100 of Bitcoin every Monday, no matter what
• When price is high → you buy fewer coins
• When price is low → you buy more coins
• Over time → your average cost smooths out volatility
• Often recommended as the #1 strategy for beginners

Scalping (Advanced)
• Extremely fast trades — seconds to minutes
• Not recommended for beginners
• Requires lightning-fast execution and nerves of steel

Which Strategy Should YOU Start With?
• Complete beginner → DCA + HODLing
• Some experience, limited time → Swing Trading
• Experienced, full-time availability → Day Trading
• Want to practice → Use this simulator!

Action Step: Go to the Dashboard and try placing a practice trade!"""
            }
        }
        

        # Module 1 - Getting Started (clickable) (clickable)
        module1 = QPushButton()
        module1.setText("1. Getting Started")
        module1.setStyleSheet(module_frame_style + "")
        module1.setMinimumHeight(55)
        module1.clicked.connect(lambda: self.show_module_content(1))
        
        # Module 2 - Technical Analysis (clickable)
        module2 = QPushButton()
        module2.setText("2. Technical Analysis")
        module2.setStyleSheet(module_frame_style)
        module2.setMinimumHeight(55)
        module2.clicked.connect(lambda: self.show_module_content(2))
        
        # Module 3 - Risk Management (clickable)
        module3 = QPushButton()
        module3.setText("3. Risk Management")
        module3.setStyleSheet(module_frame_style )
        module3.setMinimumHeight(55)
        module3.clicked.connect(lambda: self.show_module_content(3))
        
        # Module 4 - Trading Strategies (clickable)
        module4 = QPushButton()
        module4.setText("4. Trading Strategies")
        module4.setStyleSheet(module_frame_style)
        module4.setMinimumHeight(55)
        module4.clicked.connect(lambda: self.show_module_content(4))
        
        # Add all modules to the layout
        modules_layout.addWidget(module1)
        modules_layout.addWidget(module2)
        modules_layout.addWidget(module3)
        modules_layout.addWidget(module4)
        
        # Add stretch to push modules to top
        modules_layout.addStretch()
        
        modules_container.setLayout(modules_layout)
        
        # Right side - Dynamic content area
        self.content_area = QFrame()
        self.content_area.setStyleSheet("background-color: white; border-radius: 10px; padding: 20px; border: 1px solid #ddd;")
        
        self.content_area_layout = QVBoxLayout()
        
        # Title label
        self.content_title = QLabel("Select a module to view content")
        self.content_title.setStyleSheet("font-size:20px;font-weight:bold;color:black;margin-bottom:15px;")
        
        # Content text area with scroll capability  
        self.content_text = QLabel()
        self.content_text.setStyleSheet("font-size:14px;color:black;line-height:1.6;")
        self.content_text.setWordWrap(True)
        self.content_text.setAlignment(Qt.AlignTop)
        
        # Add scroll area for long content
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.content_text)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        self.content_area_layout.addWidget(self.content_title)
        self.content_area_layout.addWidget(scroll_area)
        self.content_area.setLayout(self.content_area_layout)
        
        content_layout.addWidget(modules_container)
        content_layout.addWidget(self.content_area)
        
        main_layout.addLayout(content_layout)

        container=QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def update_progress(self):
        progress = int((len(self.visited_modules) / self.total_modules) * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Progress {progress}%")

    def show_module_content(self, module_number):
        """Display content for the selected module"""
        if module_number in self.module_content:
            module_data = self.module_content[module_number]
            self.content_title.setText(module_data["title"])
            self.content_text.setText(module_data["content"])
            
            # Track progress
            if module_number not in self.visited_modules:
                self.visited_modules.add(module_number)
                self.update_progress()
        else:
            self.content_title.setText("Module Not Found")
            self.content_text.setText("Sorry, this module content is not available yet.")

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

    def open_leaderboard(self):
        from leaderboard import LeaderBoardScreen
        self.learning_screen=LeaderBoardScreen(self.username)    
        self.learning_screen.show()
        self.close()

    def logout(self):
        from login_screen import LoginWindow
        self.login_screen=LoginWindow()
        self.login_screen.show()
        self.close()

if __name__ =="__main__":
    app=QApplication(sys.argv)
    window=LearningScreen("superuser")
    window.show()
    sys.exit(app.exec())