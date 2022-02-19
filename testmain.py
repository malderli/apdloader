from PyQt5.QtWidgets import QApplication
from windows.loginwindow import LoginWindow
from windows.selectorwindow import SelectorWindow

from lib.reader import readSignalsData

import sys

def load(cursor):
    return

def tryLogin(name, password):
    
    return

if __name__ == '__main__':
    app = QApplication(sys.argv)

    testloginwindow = LoginWindow()
    # testloginwindow.show()

    testselectingwindow = SelectorWindow(readSignalsData('ChoiceToExport.txt'))
    # testselectingwindow.setSignalsData(readSignalsData('ChoiceToExport.txt'))
    testselectingwindow.show()

    sys.exit(app.exec())
