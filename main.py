from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.Qt import QEventLoop
from windows.selectorwindow import SelectorWindow
from sys import exit

from lib.utils_v3 import readSignalsData

import json
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    loop = QEventLoop()

    visual = None
    loginData = None

    # Reading JSON
    try:
        with open('configs/logindata.json', 'r') as f:
            loginData = json.load(f)
    except:
        QMessageBox.warning(None, 'Ошибка чтения файла', 'Возникла ошибка при попытке прочитать конфигурационный файл'
                            '\n[ logindata.json ]', QMessageBox.Ok)

        app.exit(2)
        exit(2)

    try:
        with open('configs/visual.json', 'r') as f:
            visual = json.load(f)
    except:
        visual = None

    signalsData = readSignalsData('configs/ChoiceToExport.txt')

    if signalsData == None:
        app.exit(1)
        exit(1)

    selectingwindow = SelectorWindow()
    selectingwindow.setTypesList(signalsData['SIGNALTYPES'])
    selectingwindow.setGroupsList(signalsData['SIGNALGROUPS'])
    selectingwindow.setSignalsList(signalsData['SIGNALS'])

    if visual is not None:
        selectingwindow.setVisualConfig(visual)

    selectingwindow.show()

    selectingwindow.signalClose.connect(loop.quit)

    loop.exec()
