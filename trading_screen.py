import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer
import db_connection
import pyqtgraph as pg
import requests

# Global style variables (only for reused styles)
header_button_style = "background-color:#14151c;color:white;border-radius:5px;padding:5px;font-size:16px;font-weight:bold;"
gray_frame_style = "background-color: #f0f0f0; border-radius: 5px;"
label_style = "font-size:16px;color:black;"
label_bold_style = "font-size:16px;color:black;font-weight:bold;"

class CandlestickChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Create the main price chart
        self.chart = pg.PlotWidget()
        self.chart.setBackground('w')
        self.chart.setLabel('left', 'Price (USDT)', color='black', size='12pt')
        self.chart.setLabel('bottom', 'Time', color='black', size='12pt')
        self.chart.showGrid(x=True, y=True)
        
        layout.addWidget(self.chart)
        self.setLayout(layout)
        
        self.candle_data = []  # Store data for indicator calculations
        
    def update_candlesticks(self, data, symbol, show_sma=False, show_rsi=False):
        #Data should be list of [timestamp, open, high, low, close, volume]
        self.chart.clear()
        
        if not data:
            return
            
        self.candle_data = data
        closes = [candle[4] for candle in data]  # Extract close prices
        
        # Calculate price range for RSI scaling
        all_prices = []
        for candle in data:
            all_prices.extend([candle[1], candle[2], candle[3], candle[4]])  # open, high, low, close
        price_min = min(all_prices)
        price_max = max(all_prices)
        price_range = price_max - price_min
            
        # Draw candlesticks
        for i, candle in enumerate(data):
            timestamp, open_price, high, low, close, volume = candle
            
            # Color: green if close > open, red otherwise
            color = 'g' if close >= open_price else 'r'
            body_color = (0, 255, 0, 150) if close >= open_price else (255, 0, 0, 150)
            
            # Draw high-low line (wick)
            wick_line = pg.PlotDataItem([i, i], [low, high], pen=pg.mkPen(color, width=2))
            self.chart.addItem(wick_line)
            
            # Draw open-close body
            body_height = abs(close - open_price)
            body_bottom = min(open_price, close)
            
            if body_height > 0:
                rect = pg.QtWidgets.QGraphicsRectItem(i-0.3, body_bottom, 0.6, body_height)
                rect.setBrush(pg.mkBrush(*body_color))
                rect.setPen(pg.mkPen(color, width=1))
                self.chart.addItem(rect)
            else:
                line = pg.PlotDataItem([i-0.3, i+0.3], [close, close], pen=pg.mkPen(color, width=2))
                self.chart.addItem(line)
        
        # Add SMA if enabled
        if show_sma and len(closes) >= 20:
            sma_20 = self.calculate_sma(closes, 20)
            if sma_20:
                x_data = list(range(19, len(closes)))  # Start from index 19 (20th candle)
                sma_line = pg.PlotDataItem(x_data, sma_20, pen=pg.mkPen('blue', width=2))
                self.chart.addItem(sma_line)
        
        # Add RSI if enabled (scaled to price range)
        if show_rsi and len(closes) >= 14:
            rsi_values = self.calculate_rsi(closes, 14)
            if rsi_values and price_range > 0:
                # RSI calculation produces values starting from index 15 (16th candle)
                x_data = list(range(15, len(closes)))  # Start from index 15 to match RSI array length
                
                # Ensure x_data and rsi_values have the same length
                if len(x_data) != len(rsi_values):
                    # Trim to match the shorter array
                    min_length = min(len(x_data), len(rsi_values))
                    x_data = x_data[:min_length]
                    rsi_values = rsi_values[:min_length]
                
                # Scale RSI (0-100) to price range (price_min to price_max)
                scaled_rsi = [price_min + (rsi / 100.0) * price_range for rsi in rsi_values]
                
                rsi_line = pg.PlotDataItem(x_data, scaled_rsi, pen=pg.mkPen('purple', width=3))
                self.chart.addItem(rsi_line)
                
                # Add scaled reference lines for RSI 30 and 70
                rsi_30_scaled = price_min + (30 / 100.0) * price_range
                rsi_70_scaled = price_min + (70 / 100.0) * price_range
                
                oversold_line = pg.PlotDataItem([0, len(closes)], [rsi_30_scaled, rsi_30_scaled], 
                                              pen=pg.mkPen('red', width=1, style=pg.QtCore.Qt.DashLine))
                overbought_line = pg.PlotDataItem([0, len(closes)], [rsi_70_scaled, rsi_70_scaled], 
                                                pen=pg.mkPen('red', width=1, style=pg.QtCore.Qt.DashLine))
                self.chart.addItem(oversold_line)
                self.chart.addItem(overbought_line)
    
    def calculate_sma(self, prices, period):
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return []
        
        sma_values = []
        for i in range(period - 1, len(prices)):
            sma = sum(prices[i - period + 1:i + 1]) / period
            sma_values.append(sma)
        return sma_values
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return []
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [max(0, delta) for delta in deltas]
        losses = [-min(0, delta) for delta in deltas]
        
        # Calculate initial average gain and loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi_values = []
        
        for i in range(period, len(gains)):
            # Smoothed moving averages
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            rsi_values.append(rsi)
        
        return rsi_values

class TradingScreen(QMainWindow):
    def __init__(self,username): 
        super().__init__()

        self.username=username

        if self.username is None:
            print("Warning: no user logged in")

        self.setWindowTitle(f"Trading Simulator - {self.username}")
        self.resize(1500,750)
        self.setStyleSheet("background-color:#edf7f7;")

        #Create all UI elements
        self.create_ui()

        
        #load real data
        self.load_portfolio_data()

        #Set up auto-refresh timer
        self.setup_auto_refresh()

        


    def create_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20,20,20,20)

        # Header
        header_container=QFrame()
        header_container.setFixedHeight(80)
        header_container.setStyleSheet("background-color: #14151c; border-radius: 10px;")

        header_layout=QHBoxLayout()

        trading_title=QLabel("Crypto Trading Simulator")
        trading_title.setAlignment(Qt.AlignLeft)
        trading_title.setStyleSheet("""font-size:24px;font-weight:bold;color:white;""")
        
        portfolio_b=QPushButton()
        portfolio_b.setText("Portfolio")
        portfolio_b.setStyleSheet(header_button_style)
        portfolio_b.clicked.connect(self.open_portfolio)

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
        header_layout.addWidget(portfolio_b)
        header_layout.addWidget(learning_b)
        header_layout.addWidget(leaderboard_b)
        header_layout.addWidget(logout_b)
        header_container.setLayout(header_layout)
        main_layout.addWidget(header_container)

        horis_layout=QHBoxLayout()

        # Portfolio summary section
        left_container=QFrame()
        left_container.setMaximumWidth(300)
        left_container.setStyleSheet("background-color: white; border-radius: 10px;")

        left_layout=QVBoxLayout()

        portfolio_summary=QLabel("Portfolio Summary")
        portfolio_summary.setAlignment(Qt.AlignLeft)
        portfolio_summary.setStyleSheet("""font-size:18px;font-weight:bold;color:black;""")

        # Total Balance
        total_balance=QFrame()
        total_balance.setStyleSheet(gray_frame_style)
        total_balance_layout=QHBoxLayout()

        total_balance_label=QLabel("Total Balance:")
        total_balance_label.setStyleSheet(label_style)

        self.total_balance_value=QLabel("Loading...")
        self.total_balance_value.setStyleSheet(label_bold_style)
        
        total_balance_layout.addWidget(total_balance_label)
        total_balance_layout.addWidget(self.total_balance_value)
        total_balance.setLayout(total_balance_layout)

        # Holding Value
        holding_value=QFrame()
        holding_value.setStyleSheet(gray_frame_style)
        holding_value_layout=QHBoxLayout()

        holding_value_label=QLabel("Holding Value:")
        holding_value_label.setStyleSheet(label_style)

        self.holding_value_value=QLabel("Loading...")
        self.holding_value_value.setStyleSheet(label_bold_style)
        
        holding_value_layout.addWidget(holding_value_label)
        holding_value_layout.addWidget(self.holding_value_value)
        holding_value.setLayout(holding_value_layout)

        # Available Cash
        available_cash=QFrame()
        available_cash.setStyleSheet(gray_frame_style)
        available_cash_layout=QHBoxLayout()

        available_cash_label=QLabel("Available Cash:")
        available_cash_label.setStyleSheet(label_style)

        self.available_cash_value=QLabel("Loading...")
        self.available_cash_value.setStyleSheet(label_bold_style)
        
        available_cash_layout.addWidget(available_cash_label)
        available_cash_layout.addWidget(self.available_cash_value)
        available_cash.setLayout(available_cash_layout)

        # Holdings List
        holdings=QFrame()
        holdings.setStyleSheet(gray_frame_style)    

        holdings_layout=QVBoxLayout()

        holdings_title=QLabel("Holdings:")
        holdings_title.setStyleSheet(label_bold_style)

        self.holdings_list=QListWidget()
        self.holdings_list.setStyleSheet("background-color: white;color: black; border-radius: 5px;")
        holdings_layout.addWidget(holdings_title)
        holdings_layout.addWidget(self.holdings_list)
        holdings.setLayout(holdings_layout)

        left_layout.addWidget(portfolio_summary)
        left_layout.addWidget(total_balance)
        left_layout.addWidget(holding_value)
        left_layout.addWidget(available_cash)
        left_layout.addWidget(holdings)
        left_container.setLayout(left_layout)
        horis_layout.addWidget(left_container)

        # Chart section (middle)
        middle_container=QFrame()
        middle_container.setStyleSheet("background-color: white; border-radius: 10px;")

        middle_layout=QVBoxLayout()

        #Chart controls
        chart_controls = QFrame()
        chart_controls.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 5px;")
        chart_controls_layout = QHBoxLayout(chart_controls)

        self.graph_title=QLabel("Bitcoin Price Chart")
        self.graph_title.setStyleSheet("font-size:18px;font-weight:bold;color:black;")

        # Timeframe selector
        timeframe_label = QLabel("Timeframe:")
        timeframe_label.setStyleSheet("font-size:12px;color:black;")

        self.chart_timeframe = QComboBox()
        self.chart_timeframe.addItems(["1 min", "5 min", "15 min", "1 hour"])
        self.chart_timeframe.setCurrentText("15 min")
        self.chart_timeframe.setStyleSheet("background-color:white;color:black;padding:3px;")
        self.chart_timeframe.currentTextChanged.connect(self.update_chart)
        
        # Indicator toggles
        self.sma_checkbox = QCheckBox("SMA")
        self.sma_checkbox.setStyleSheet("color:black;font-size:12px;")
        self.sma_checkbox.toggled.connect(self.redraw_chart)
        
        self.rsi_checkbox = QCheckBox("RSI")
        self.rsi_checkbox.setStyleSheet("color:black;font-size:12px;")
        self.rsi_checkbox.toggled.connect(self.redraw_chart)

        chart_controls_layout.addWidget(self.graph_title)
        chart_controls_layout.addStretch()
        chart_controls_layout.addWidget(timeframe_label)
        chart_controls_layout.addWidget(self.chart_timeframe)
        chart_controls_layout.addWidget(self.sma_checkbox)
        chart_controls_layout.addWidget(self.rsi_checkbox)

        # Add the actual chart
        self.chart_widget = CandlestickChart()

        middle_layout.addWidget(chart_controls)
        middle_layout.addWidget(self.chart_widget)
        middle_container.setLayout(middle_layout)
        horis_layout.addWidget(middle_container)
        
        # Trading section (right)
        right_container=QFrame()
        right_container.setMaximumWidth(300)
        right_container.setStyleSheet("background-color: white; border-radius: 10px;")

        right_layout=QVBoxLayout()

        place_order_l=QLabel("Place Order")
        place_order_l.setAlignment(Qt.AlignLeft)
        place_order_l.setStyleSheet("""font-size:18px;font-weight:bold;color:black;""")

        select_crypto_l=QLabel("Select Cryptocurrency:")
        select_crypto_l.setStyleSheet(label_style)

        self.select_crypto=QComboBox()
        self.select_crypto.setStyleSheet("background-color: #f0f0f0;color:black; border-radius: 5px;padding:5px;")   
        
        # Crypto mapping for API calls
        self.crypto_symbols = {
            "Bitcoin (BTC)": "BTC",
            "Ethereum (ETH)": "ETH",
            "Cardano (ADA)": "ADA", 
            "Solana (SOL)": "SOL"
        }
        
        for crypto in self.crypto_symbols.keys():
            self.select_crypto.addItem(crypto)
        
        self.select_crypto.currentTextChanged.connect(self.on_crypto_changed)

        # Current Price
        current_price=QFrame()
        current_price.setStyleSheet(gray_frame_style)
        current_price_layout=QHBoxLayout()

        current_price_label=QLabel("Current Price:")
        current_price_label.setStyleSheet(label_style)

        self.current_price_value=QLabel("Loading...")
        self.current_price_value.setStyleSheet(label_bold_style)
        
        current_price_layout.addWidget(current_price_label)
        current_price_layout.addWidget(self.current_price_value)
        current_price.setLayout(current_price_layout)

        # Quantity input
        quantity_label=QLabel("Quantity:")
        quantity_label.setStyleSheet(label_style)
        
        self.quantity_input=QLineEdit()
        self.quantity_input.setStyleSheet("background-color: #f0f0f0;color:black; border-radius: 5px;padding:5px;")
        self.quantity_input.setPlaceholderText("Enter quantity")
        self.quantity_input.textChanged.connect(self.calculate_total_cost)

        # Total Cost
        total_cost=QFrame()
        total_cost.setStyleSheet(gray_frame_style)
        total_cost_layout=QHBoxLayout()

        total_cost_label=QLabel("Total Cost:")
        total_cost_label.setStyleSheet(label_style)

        self.total_cost_value=QLabel("$0.00")
        self.total_cost_value.setStyleSheet(label_bold_style)
        
        total_cost_layout.addWidget(total_cost_label)
        total_cost_layout.addWidget(self.total_cost_value)
        total_cost.setLayout(total_cost_layout)

        # Action Buttons
        self.sell_b=QPushButton()
        self.sell_b.setText("SELL")
        self.sell_b.setStyleSheet("background-color:#e74c3c;color:white;border-radius:5px;padding:10px;font-size:16px;font-weight:bold;")
        self.sell_b.clicked.connect(self.sell_crypto)

        self.buy_b=QPushButton()
        self.buy_b.setText("BUY")
        self.buy_b.setStyleSheet("background-color:#2ecc71;color:white;border-radius:5px;padding:10px;font-size:16px;font-weight:bold;")
        self.buy_b.clicked.connect(self.buy_crypto)

        # Recent Orders
        orders=QFrame()
        orders.setStyleSheet(gray_frame_style)    

        orders_layout=QVBoxLayout()

        orders_title=QLabel("Recent Orders:")
        orders_title.setStyleSheet(label_bold_style)

        self.transactions_list=QListWidget()
        self.transactions_list.setStyleSheet("background-color: white;color: black; border-radius: 5px;")
        orders_layout.addWidget(orders_title)
        orders_layout.addWidget(self.transactions_list)  
        orders.setLayout(orders_layout)

        right_layout.addWidget(place_order_l)
        right_layout.addWidget(select_crypto_l)
        right_layout.addWidget(self.select_crypto)
        right_layout.addWidget(current_price)
        right_layout.addWidget(quantity_label)
        right_layout.addWidget(self.quantity_input)
        right_layout.addWidget(total_cost)
        right_layout.addWidget(self.buy_b)
        right_layout.addWidget(self.sell_b)
        right_layout.addWidget(orders)
        right_container.setLayout(right_layout)
        horis_layout.addWidget(right_container)

        main_layout.addLayout(horis_layout)
        container=QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_portfolio_data(self):
        #fetch portfolio data from db
        try:
            portfolio_data = db_connection.get_portfolio_summary(self.username)
            
            # Update portfolio summary
            self.total_balance_value.setText(f"${portfolio_data['total_balance']:.2f}")
            self.available_cash_value.setText(f"${portfolio_data['available_cash']:.2f}")
            self.holding_value_value.setText(f"${portfolio_data['holding_value']:.2f}")
            
            # Update holdings list
            self.holdings_list.clear()
            for holding in portfolio_data['holdings']:
                item_text = f"{holding['symbol']} - {holding['quantity']:.4f} (${holding['current_value']:.2f})"
                self.holdings_list.addItem(item_text)
            
            # Load recent transactions since if portfolio data loads, transactions should also be updated
            self.load_recent_transactions()
            
            # Load current crypto price
            self.on_crypto_changed()
            
        except Exception as e:
            print(f"Error loading portfolio data: {e}")
            self.show_error_message(f"Error loading portfolio: {e}")
    
    def load_recent_transactions(self):
        #update recent transactions list from db
        try:
            transactions = db_connection.get_recent_transactions(self.username, 5)
            self.transactions_list.clear()
            for transaction in transactions:
                self.transactions_list.addItem(transaction)
        except Exception as e:
            print(f"Error loading transactions: {e}")

    def on_crypto_changed(self):
        #When user selects different crypto, update current price and chart
        selected_crypto=self.select_crypto.currentText()
        symbol=self.crypto_symbols[selected_crypto]

        try:
            #Get current price from db
            current_price = db_connection.get_and_update_crypto_price(symbol)
            self.current_price_value.setText(f"${current_price:.2f}")

            #Recalculate total cost
            self.calculate_total_cost()

            self.update_chart() # Update chart for new crypto
        
        except Exception as e:
            print(f"Error fetching current price: {e}")
            self.current_price_value.setText("Error")
    
    def calculate_total_cost(self):
        #Calculate total cost based on quantity and current price
        try:
            quantity_text=self.quantity_input.text()
            if quantity_text:
                quantity=float(quantity_text)
                current_price_text=self.current_price_value.text().replace("$","")
                current_price=float(current_price_text)
                total_cost=quantity*current_price
                self.total_cost_value.setText(f"${total_cost:.2f}")
            else:
                self.total_cost_value.setText("$0.00")
        except Exception as e:
            print(f"Error calculating total cost: {e}")
            self.total_cost_value.setText("Error")

    def buy_crypto(self):
        #Handles buy orders
        try:
            selected_crypto = self.select_crypto.currentText()
            symbol = self.crypto_symbols[selected_crypto]
            quantity_text = self.quantity_input.text()
            
            # Validate input
            if not quantity_text:
                self.show_error_message("Please enter valid quantity")
                return
            try:
                quantity = float(quantity_text)
            except ValueError:
                self.show_error_message("Please enter valid quantity")
                return
            if quantity <= 0:
                self.show_error_message("Quantity must be positive")
                return

            price = float(self.current_price_value.text().replace("$", ""))

            #Execute buy order in db
            success, message = db_connection.execute_trade(self.username, symbol, quantity, price, "BUY")
            if success:
                self.show_success_message("Buy order executed successfully")
                self.quantity_input.clear()
                self.load_portfolio_data() # Refresh portfolio data after trade
            else:
                self.show_error_message(f"Buy order failed: {message}")
        except Exception as e:
            print(f"Error executing buy order: {e}")
            self.show_error_message(f"Error executing buy order: {e}")
    
    def sell_crypto(self):
        #Handles sell orders
        try:
            selected_crypto = self.select_crypto.currentText()
            symbol = self.crypto_symbols[selected_crypto]
            quantity_text = self.quantity_input.text()

            # Validate input
            if not quantity_text:
                self.show_error_message("Please enter valid quantity")
                return
            try:
                quantity = float(quantity_text)
            except ValueError:
                self.show_error_message("Please enter valid quantity")
                return
            if quantity <= 0:
                self.show_error_message("Quantity must be positive")
                return

            price = float(self.current_price_value.text().replace("$", ""))

            #Execute sell order in db
            success, message = db_connection.execute_trade(self.username, symbol, quantity, price, "SELL")
            if success:
                self.show_success_message("Sell order executed successfully")
                self.quantity_input.clear()
                self.load_portfolio_data() # Refresh portfolio data after trade
            else:
                self.show_error_message(f"Sell order failed: {message}")
        except Exception as e:
            print(f"Error executing sell order: {e}")
            self.show_error_message(f"Error executing sell order: {e}")

    def update_chart(self):
        """Update chart when crypto or timeframe changes (fetches new data)"""
        selected_crypto = self.select_crypto.currentText()
        symbol = self.crypto_symbols[selected_crypto]
        timeframe = self.chart_timeframe.currentText()
        
        # Update title
        self.graph_title.setText(f"{selected_crypto} Price Chart - {timeframe}")
        
        # Fetch chart data
        self.fetch_chart_data(symbol, timeframe)

    def redraw_chart(self):
        """Re-render chart with existing data when toggling indicators (no API call)"""
        candle_data = self.chart_widget.candle_data
        if candle_data:
            selected_crypto = self.select_crypto.currentText()
            symbol = self.crypto_symbols[selected_crypto]
            show_sma = self.sma_checkbox.isChecked()
            show_rsi = self.rsi_checkbox.isChecked()
            self.chart_widget.update_candlesticks(candle_data, symbol, show_sma, show_rsi)

    def fetch_chart_data(self, symbol, timeframe_text):
        """Fetch candlestick data from Bybit"""
        try:
            # Convert timeframe
            timeframe_map = {
                "1 min": "1",
                "5 min": "5",    
                "15 min": "15",
                "1 hour": "60"
            }
            
            api_symbol = symbol + "USDT"
            interval = timeframe_map.get(timeframe_text, "15")
            
            url = "https://api.bybit.com/v5/market/kline"
            params = {
                "category": "spot",
                "symbol": api_symbol,
                "interval": interval,
                "limit": 50
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['retCode'] == 0:
                    candles = []
                    for item in data['result']['list']:
                        timestamp = int(item[0])
                        open_price = float(item[1])
                        high = float(item[2])
                        low = float(item[3]) 
                        close = float(item[4])
                        volume = float(item[5])
                        
                        candles.append([timestamp, open_price, high, low, close, volume])
                    
                    # Sort by timestamp (oldest first)
                    candles.sort(key=lambda x: x[0])
                    
                    # Update chart with indicators
                    show_sma = self.sma_checkbox.isChecked()
                    show_rsi = self.rsi_checkbox.isChecked()
                    self.chart_widget.update_candlesticks(candles, symbol, show_sma, show_rsi)
                    
        except Exception as e:
            print(f"Error fetching chart data: {e}")


    def setup_auto_refresh(self):
        #Set up a timer to auto-refresh portfolio data every 30 seconds
        self.refresh_timer=QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_data)
        self.refresh_timer.start(30000) # Refresh every 30 seconds
    
    def refresh_all_data(self):
        #Refresh portfolio data and prices
        self.load_portfolio_data()

    def show_error_message(self, message):
        msg_box=QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()


    def show_success_message(self, message):
        msg_box=QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Information")
        msg_box.setText(message)
        msg_box.exec()


    def open_portfolio(self):
        from portfolio import PortfolioScreen
        self.portfolio_screen=PortfolioScreen(self.username)    
        self.portfolio_screen.show()
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

    


        
if __name__ =="__main__":
    app=QApplication(sys.argv)
    window=TradingScreen("superuser")
    window.show()
    sys.exit(app.exec())