from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGridLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt5.QtCore import pyqtSignal


class LoginWindow(QtWidgets.QWidget):
    signalTryLogin = pyqtSignal(str, str)

    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setWindowTitle('Login')

        self.leUser = QLineEdit()

        self.lePassword = QLineEdit()

        self.btnOk = QPushButton()
        self.btnOk.clicked.connect(self.btnOkClicked)
        self.btnOk.setMaximumHeight(100)
        self.btnOk.setText('Login')

        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(QLabel('User:'), 0, 0)
        self.mainLayout.addWidget(self.leUser, 0, 1)
        self.mainLayout.addWidget(QLabel('Pass:'), 1, 0)
        self.mainLayout.addWidget(self.lePassword, 1, 1)
        self.mainLayout.addWidget(self.btnOk, 0, 2, 2, 1)

        self.setGeometry(100, 100, 700, 100)

        self.setLayout(self.mainLayout)

    def btnOkClicked(self):
        self.signalTryLogin.emit(self.leUser.text(), self.lePassword.text())