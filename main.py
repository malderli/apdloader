from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.Qt import QEventLoop
from windows.loginwindow import LoginWindow
from windows.selectorwindow import SelectorWindow

from lib.utils import readSignalsData, getMinMaxTime, uploadFromDB

import json

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    loop = QEventLoop()

    # Reading JSON
    try:
        with open('logindata.json', 'r') as f:
            loginData = json.load(f)
    except:
        QMessageBox.warning(None, 'Ошибка чтения файла', 'Возникла ошибка при попытке прочитать конфигурационный файл'
                            '\n[ logindata.json ]', QMessageBox.Ok)

        app.exit(2)
        exit(2)

    signalsData = readSignalsData('ChoiceToExport.txt')

    if signalsData == None:
        app.exit(1)
        exit(1)

    selectingwindow = SelectorWindow(signalsData)
    selectingwindow.setBeginEndTime(getMinMaxTime(loginData))
    selectingwindow.signalDo.connect(loop.quit)
    selectingwindow.show()

    # Reading signals data
    while(True):
        loop.exec()

        # Check fatal processed errors in selectingwindow
        if selectingwindow.checkErr():
            app.exit(selectingwindow.checkErr())
            exit(selectingwindow.checkErr())

        data = selectingwindow.getData()

        if not uploadFromDB(data[0], data[1], loginData, data[2]):
                QMessageBox.information(None, 'Выполнено', 'Выгрузка завершена успешно', QMessageBox.Ok)

