from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.Qt import QEventLoop
from windows.selectorwindow_v2 import SelectorWindowV2
from sys import exit

from lib.utils_v3 import readSignalsData

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

    selectingwindow = SelectorWindowV2()
    selectingwindow.setTypesList(signalsData['SIGNALTYPES'])
    selectingwindow.setGroupsList(signalsData['SIGNALGROUPS'])
    selectingwindow.setSignalsList(signalsData['SIGNALS'])

    selectingwindow.show()

    selectingwindow.signalClose.connect(loop.quit)

    loop.exec()
