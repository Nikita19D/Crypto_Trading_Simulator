import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import QSize, Qt
import mysql.connector
from mysql.connector import connect, Error
import bcrypt


base_entry_style="background-color:lightgray;color:black;border-radius:5px;padding:5px;border: 1px solid #403f3e;"
wrong_entry_style="background-color:lightgray;color:black;border-radius:5px;padding:5px;border: 1px solid #eb4034"
base_l="color:black"
wrong_l="color:red"

class RegistrationWindow(QMainWindow):
    def __init__  (self):

        def strong(password_t):
            if len(password_t)>=14:
                return True
            else:
                return False
        def reset():
            username.setStyleSheet(base_entry_style)
            username_l.setText("Username:")
            username_l.setStyleSheet(base_l)
            password.setStyleSheet(base_entry_style)
            password_l.setText("Password:")
            password_l.setStyleSheet(base_l)
            password_conf.setStyleSheet(base_entry_style)
            password_conf_l.setText("Confirm password:")
            password_conf_l.setStyleSheet(base_l)
            policy_agreement.setStyleSheet("color:black")
            
        def registration():
            print("Register attempted")
            reset()#clear previous error states   
            if username.text() and password.text() and password_conf.text(): #Check all fields are filled in
                if strong(password.text()):
                    if password.text()==password_conf.text():#check passwords match
                        #check if the terms are accepted
                        if policy_agreement.isChecked():
                            print("All validations passed")
                            try:
                                DB_NAME= "trading_simulator"
                                connection = mysql.connector.connect(
                                host="trading-simulator.chgu8gc0uejo.eu-west-2.rds.amazonaws.com",
                                user="admin",
                                password=")EF0T_oa0:N3",
                                port=3306,
                                ssl_disabled=False,
                                connect_timeout=30,
                                raise_on_warnings=True,
                                database=DB_NAME
                                )
                                cursor = connection.cursor()

                                username_val=username.text()
                                password_val=password.text()

                                #Hashing the password with bcrypt
                                password_hash=bcrypt.hashpw(password_val.encode("utf-8"),
                                                            bcrypt.gensalt()).decode("utf-8")#store as a string

                                try:
                                    #Attempt to insert the user
                                    cursor.execute("INSERT INTO USERS (username,password_hash) VALUES (%s,%s)",(username_val,password_hash))
                                    connection.commit()
                                    
                                    #switch to trading screen
                                    from trading_screen import TradingScreen
                                    self.trading=TradingScreen(username_val)
                                    self.trading.show()
                                    self.close()
                                    
                                except mysql.connector.IntegrityError:
                                    #If user name already exist:
                                    username_l.setStyleSheet("color:red;")
                                    username_l.setText("Username: Already exists")
                                    username.setStyleSheet(wrong_entry_style)

                            except mysql.connector.Error as err:
                                print(f"Failed connecting to database: {err}")

                            #ensures that connections are closed no matter what
                            finally:
                                if 'cursor' in locals() and cursor:
                                    cursor.close()
                                if 'connection' in locals() and connection.is_connected():
                                    connection.close()
                        else:
                            print("accept the terms and conditions")
                            policy_agreement.setStyleSheet("color:red")
                    else:
                       print("passwords do not match")
                       password_conf_l.setText("Confirm password: does not match")
                       password_conf_l.setStyleSheet(wrong_l)
                       password_l.setStyleSheet("color:red")
                       password.setStyleSheet(wrong_entry_style)
                       password_conf.setStyleSheet(wrong_entry_style)
                       
                else:
                   print("Your password is not complex enough")
                   password_l.setText("Password: not strong enough")
                   password_l.setStyleSheet("color:red")
                   password.setStyleSheet(wrong_entry_style)
                   password_conf.setStyleSheet(wrong_entry_style)
                   
            else:
                print("not all fields are filled in")
                if not username.text():  username.setStyleSheet(wrong_entry_style)
                if not password.text():  password.setStyleSheet(wrong_entry_style)
                if not password_conf.text():  password_conf.setStyleSheet(wrong_entry_style)

        def open_login():
            from login_screen import LoginWindow
            self.login=LoginWindow()
            self.login.show()
            self.close()

        super().__init__()

        self.setWindowTitle("Trading Simulator")
        self.resize(400,500)
        self.setStyleSheet("background-color:#edf7f7;")

        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20,20,20,20)

        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""font-size:24px;font-weight:bold;color:black;""")
        main_layout.addWidget(title)

        # Form layout for labeled inputs
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(6)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        # Username field
        username_l = QLabel("Username:")
        username_l.setStyleSheet("color:black;")
        username = QLineEdit()
        username.setPlaceholderText("Enter username")
        username.setStyleSheet(base_entry_style)

        # Password field
        password_l = QLabel("Password:")
        password_l.setStyleSheet("color:black;")
        password = QLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        password.setPlaceholderText("Password - at least 14 characters long")
        password.setStyleSheet(base_entry_style)

        # Confirm password field
        password_conf_l = QLabel("Confirm password:")
        password_conf_l.setStyleSheet("color:black;")
        password_conf = QLineEdit()
        password_conf.setEchoMode(QLineEdit.EchoMode.Password)
        password_conf.setPlaceholderText("Confirm password")
        password_conf.setStyleSheet(base_entry_style)

        login_link=QPushButton()
        login_link.setText("→ Aready have an account?")
        login_link.setFixedSize(160,25)
        login_link.setStyleSheet("background-color:#edf7f7;color:#0276fa;")
        login_link.clicked.connect(open_login)
       

        policy_agreement=QCheckBox("I agree to Terms of Service")
        policy_agreement.setCheckState(Qt.CheckState.Unchecked)
        policy_agreement.setStyleSheet("color:black;")
        
        submit_button=QPushButton()
        submit_button.setText("CREATE ACCOUNT")
        submit_button.setStyleSheet("background-color:#144b82;color:white;border-radius:5px;padding:5px;font-size:16px;font-weight:bold;")
        submit_button.clicked.connect(registration)

        #Virtual money notice
        account_info=QLabel("""Account information:
                            Starting Balance $10,000
                            Virtual currency only
                            No real money involved""")
        account_info.setStyleSheet("background-color:#40c746;color:#023d1e;")

        #Adding to layout
        form_layout.addRow(username_l,username)
        form_layout.addRow(password_l,password)
        form_layout.addRow(password_conf_l,password_conf)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(login_link)
        main_layout.addWidget(policy_agreement)
        main_layout.addWidget(submit_button)
        main_layout.addWidget(account_info)

        container=QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
if __name__ =="__main__":
    app=QApplication(sys.argv)
    window=RegistrationWindow()
    window.show()
    sys.exit(app.exec())

