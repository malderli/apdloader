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

    # # selectingwindow.setBeginEndTime(getMinMaxTime(loginData))
    # selectingwindow.signalDo.connect(loop.quit)
    selectingwindow.show()

    selectingwindow.signalClose.connect(loop.quit)

    loop.exec()

    # uploader.signalChangeUploadState.connect(selectingwindow.setUploadState)
    # uploader.signalSwitchInterface.connect(selectingwindow.toggleUploadMode)
    # uploader.signalThrowMessageBox.connect(selectingwindow.throwMessageBox)
    #
    # # Reading signals data
    # while(True):
    #     loop.exec()
    #
    #     # Check fatal processed errors in selectingwindow
    #     if selectingwindow.checkErr():
    #         app.exit(selectingwindow.checkErr())
    #         exit(selectingwindow.checkErr())
    #
    #     data = selectingwindow.getData()
    #
    #     uploader.uploadFromDB_thread(data[0], data[1],  data[2], data[3], loginData)
