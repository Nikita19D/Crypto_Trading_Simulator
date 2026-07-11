import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
import mysql.connector
from mysql.connector import connect, Error
import bcrypt

base_entry_style="background-color:lightgray;color:black;border-radius:5px;padding:5px;border: 1px solid #403f3e;"
wrong_entry_style="background-color:lightgray;color:black;border-radius:5px;padding:5px;border: 1px solid #eb4034"
base_l="color:black"
wrong_l="color:red"

class LoginWindow(QMainWindow):
    def __init__(self): 

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
        def login():
            print("Login attempted")
            reset()
            if username.text() and password.text():
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
                                cursor.execute("SELECT password_hash FROM USERS WHERE username=%s",(username_val,))
                                hashed_password=cursor.fetchone()
                                if hashed_password:
                                    if bcrypt.checkpw(password_val.encode("utf-8"),hashed_password[0].encode("utf-8")):
                                        #switch to trading screen
                                        from trading_screen import TradingScreen
                                        self.trading=TradingScreen(username_val )
                                        self.trading.show()
                                        self.close()
                                    else:
                                        #If user name already exist:
                                        password_l.setStyleSheet("color:red;")
                                        password_l.setText("Password: Entered password is wrong")
                                        password.setStyleSheet(wrong_entry_style)
                                else:
                                     #If user name already exist:
                                    username_l.setStyleSheet("color:red;")
                                    username_l.setText("Username: user with this username doesn't exist")
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
                print("not all fields are filled in")
                if not username.text():  username.setStyleSheet(wrong_entry_style)
                if not password.text():  password.setStyleSheet(wrong_entry_style)

        def open_reg():
            from registration_screen import RegistrationWindow
            self.registration=RegistrationWindow()
            self.registration.show()
            self.close()


        super().__init__()

        self.setWindowTitle("Trading Simulator")
        self.resize(400,500)
        self.setStyleSheet("background-color:#edf7f7;")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20,20,20,20)

        #logo
        logo=QLabel()
        logo .setAlignment(Qt.AlignCenter)
        pixmap=QPixmap('logo.jpg')
        pixmap = pixmap.scaled(70, 70)
        logo.setPixmap(pixmap)
        main_layout.addWidget(logo)

        #title
        title = QLabel("Crypto Trading Simulator")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""font-size:24px;font-weight:bold;color:black;""")
        main_layout.addWidget(title)

        form_layout= QFormLayout()
        form_layout.setVerticalSpacing(6)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        username_l=QLabel("Username:")
        username_l.setStyleSheet("color:black;")

        username=QLineEdit()
        username.setPlaceholderText("Enter username")
        username.setStyleSheet(base_entry_style)


        password_l=QLabel("Password:")
        password_l.setStyleSheet("color:black;")

        password=QLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        password.setPlaceholderText("Enter Password")
        password.setStyleSheet(base_entry_style)

        login_b=QPushButton()
        login_b.setText("LOGIN")
        login_b.setStyleSheet("background-color:#144b82;color:white;border-radius:5px;padding:5px;font-size:16px;font-weight:bold;")
        login_b.clicked.connect(login)

        or_label=QLabel()
        or_label.setText("----OR----")
        or_label.setAlignment(Qt.AlignCenter)
        or_label.setStyleSheet("font-weight:bold;color:#144b82;font-size:16px;")
            
        create_account=QPushButton()
        create_account.setText("CREATE ACCOUNT")
        create_account.setStyleSheet("""background-color:white;color:#144b82;border-radius:7px;border-color:#144b82;
                                     border-style:solid ;border-width:2px;padding:5px;font-size:16px;font-weight:bold;""")
        create_account.clicked.connect(open_reg)

        form_layout.addRow(username_l,username)
        form_layout.addRow(password_l,password)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(login_b)
        main_layout.addWidget(or_label)
        main_layout.addWidget(create_account)   

        container=QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

if __name__ =="__main__":
    app=QApplication(sys.argv)
    window=LoginWindow()
    window.show()
    sys.exit(app.exec())