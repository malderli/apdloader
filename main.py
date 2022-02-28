from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QEventLoop
from windows.loginwindow import LoginWindow
from windows.selectorwindow import SelectorWindow

from lib.utils import readSignalsData, getMinMaxTime, uploadFromDB

import json

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    loop = QEventLoop()

    with open('logindata.json', 'r') as f:
        loginData = json.load(f)

    selectingwindow = SelectorWindow(readSignalsData('ChoiceToExport.txt'))
    selectingwindow.setBeginEndTime(getMinMaxTime(loginData))
    selectingwindow.signalDoTheJob.connect(loop.quit)
    selectingwindow.show()

    loop.exec()

    data = selectingwindow.getData()

    uploadFromDB(data[0], data[1], loginData, data[2])

    app.exit(0)
    # sys.exit(app.exec())
