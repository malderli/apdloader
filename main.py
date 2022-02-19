from PyQt5.QtWidgets import QApplication

from windows.loginwindow import LoginWindow


import psycopg2
import sys


def load(cursor):
    return


def tryLogin(name, password):

    return


if __name__ == '__main__':
    app = QApplication(sys.argv)

    testloginwindow = LoginWindow()

    # Trying to login
    con = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="Kaliakakya",
        host="127.0.0.1",
        port="5432"
    )

    cursor = con.cursor()

    testloginwindow.show()
    sys.exit(app.exec())
