import PyQt5.Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QDateTimeEdit, QTableWidget, QLineEdit
from PyQt5.QtCore import pyqtSignal


class SelectorWindow(QtWidgets.QWidget):
    signalClose = pyqtSignal()

    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()
        self.setWindowTitle('Утилита выгрузки трендов САУ ПТУ ПТ-150/160-12,8. Версия 1.01.14, 2022-01-22 @INTAY')

        self.mainLayout = QGridLayout()

        # Time selecting part
        self.gbTime = QGroupBox('Выбор интервала выгрузки')
        self.layoutTime = QGridLayout()

        self.dteBeginTime = QDateTimeEdit()
        self.dteBeginTime.setDisplayFormat("yyyy.MM.dd hh:mm:ss")
        self.dteEndTime = QDateTimeEdit()
        self.dteEndTime.setDisplayFormat("yyyy.MM.dd hh:mm:ss")

        self.btnUpdateToTime = QPushButton('Обновить')
        self.btnUpdateToTime.setSizePolicy(PyQt5.Qt.QSizePolicy.Expanding, PyQt5.Qt.QSizePolicy.Preferred)

        self.layoutTime.addWidget(QLabel('От:'), 0, 0)
        self.layoutTime.addWidget(self.dteBeginTime, 0, 1)
        self.layoutTime.addWidget(QLabel('До:'), 0, 2)
        self.layoutTime.addWidget(self.dteEndTime, 0, 3)
        self.layoutTime.addWidget(self.btnUpdateToTime, 0, 4)

        self.gbTime.setLayout(self.layoutTime)
        self.gbTime.setSizePolicy(PyQt5.Qt.QSizePolicy.Minimum, PyQt5.Qt.QSizePolicy.Minimum)

        # Signals selecting part
        self.gbSignals = QGroupBox('Выбор выгружаемых сигналов')
        self.layoutSignals = QGridLayout()
        self.layoutSignals.setRowStretch(1, 1)

        self.tbPossibleSig = QTableWidget()
        self.tbPossibleSig.setMaximumHeight(3000)

        self.tbSelectedSig = QTableWidget()
        self.tbSelectedSig.setMaximumHeight(3000)

        self.btnAdd = QPushButton('>>')
        self.btnRem = QPushButton('<<')

        self.layoutSignals.addWidget(QLabel('Доступные сигналы:'), 0, 0)
        self.layoutSignals.addWidget(self.tbPossibleSig, 1, 0, 2, 1)

        self.layoutSignals.addWidget(QLabel('Выбранные сигналы:'), 0, 2)
        self.layoutSignals.addWidget(self.tbSelectedSig, 1, 2, 2, 1)

        self.subLayout = QVBoxLayout()
        self.subLayout.addWidget(self.btnAdd, 0, PyQt5.QtCore.Qt.AlignBottom)
        self.subLayout.addWidget(self.btnRem, 1, PyQt5.QtCore.Qt.AlignTop)
        self.layoutSignals.addLayout(self.subLayout, 1, 1, 2, 1)

        self.gbSignals.setLayout(self.layoutSignals)
        self.gbSignals.setSizePolicy(PyQt5.Qt.QSizePolicy.Expanding, PyQt5.Qt.QSizePolicy.Expanding)

        # File path
        self.gbFolder = QGroupBox('Выбор директории сохранения')
        self.layoutFolder = QGridLayout()
        self.layoutFolder.setColumnStretch(0, 1)

        self.leFolderPath = QLineEdit()
        self.btnSelectFolder = QPushButton('Открыть')

        self.layoutFolder.addWidget(self.leFolderPath, 0, 0)
        self.layoutFolder.addWidget(self.btnSelectFolder, 0, 1)

        self.gbFolder.setLayout(self.layoutFolder)

        # Main window
        self.btnDo = QPushButton('Выполнить выгрузку')

        self.mainLayout.addWidget(self.gbTime, 0, 0)
        self.mainLayout.addWidget(self.gbSignals, 1, 0)
        self.mainLayout.addWidget(self.gbFolder, 2, 0)
        self.mainLayout.addWidget(self.btnDo, 3, 0)

        self.setGeometry(100, 100, 700, 100)
        self.setLayout(self.mainLayout)

    def setBeginEndTime(self, beginTime, endTime):
        pass



    def setElementsList(self):
        return
