from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.Qt import QEventLoop
from windows.selectorwindow import SelectorWindow
from sys import exit

from lib.utils import Uploader

import json
import sys

date = '2023-05-01'
version = '1.22.0'
isDebug = False

title = 'Утилита выгрузки трендов САУ ПТУ ПТ-150/160-12,8. Версия {}{}, {} @INTAY'.format(
    version, '.DEBUG' if isDebug else '', date)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    loop = QEventLoop()

    uploader = Uploader()

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

    signalsData = uploader.readSignalsData('configs/ChoiceToExport.txt')

    if signalsData == None:
        app.exit(1)
        exit(1)

    selectingwindow = SelectorWindow(title)

    if visual is not None:
        selectingwindow.setVisualConfig(visual)

    selectingwindow.setTypesList(signalsData['SIGNALTYPES'])
    selectingwindow.setGroupsList(signalsData['SIGNALGROUPS'])
    selectingwindow.setSignalsList(signalsData['SIGNALS'])

    selectingwindow.signalStartUploading.connect(loop.quit)
    selectingwindow.signalClose.connect(loop.quit)
    selectingwindow.show()

    uploader.signalChangeUploadState.connect(selectingwindow.setUploadState)
    uploader.signalSwitchInterface.connect(selectingwindow.toggleUploadMode)
    uploader.signalThrowMessageBox.connect(selectingwindow.throwMessageBox)

    # Reading signals data
    while(True):
        loop.exec()

        if not selectingwindow.isVisible():
            exit(0)

        data = selectingwindow.getUploadingData()

        uploader.uploadFromDB_thread(*data, loginData)
