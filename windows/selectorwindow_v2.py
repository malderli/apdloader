import PyQt5.Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QDateEdit, QTimeEdit, QTableWidget, QLineEdit, QRadioButton
from PyQt5.QtWidgets import QFrame, QTabWidget, QWidget, QCheckBox, QSpacerItem, QHeaderView, QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QColor, QCloseEvent, QMovie
from PyQt5.QtCore import pyqtSignal
from datetime import datetime


class SelectorWindowV2(QtWidgets.QWidget):
    signalDo = pyqtSignal()

    def __init__(self, sigData=None):
        super(QtWidgets.QWidget, self).__init__()

        self.listRbGroups = []
        self.listRbTypes = []
        self.listChbTypes = []

        self.errCode = 0
        self.colorSelected = QColor('#8DDF8D')



        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Signals

        # ------------------------------------------------- Signals group box

        self.tbPossibleSig = QTableWidget()
        self.tbPossibleSig.setMaximumHeight(3000)
        self.tbPossibleSig.setColumnCount(3)
        self.tbPossibleSig.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbPossibleSig.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbPossibleSig.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tbPossibleSig.setColumnHidden(1, True)
        self.tbPossibleSig.setHorizontalHeaderLabels(['KKS', 'Тег', 'Наименование'])
        self.tbPossibleSig.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbPossibleSig.setAlternatingRowColors(True)
        self.tbPossibleSig.setWordWrap(True)
        self.tbPossibleSig.doubleClicked.connect(self.tbPossibleItemDClicked)
        self.tbPossibleSig.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        self.tbSelectedSig = QTableWidget()
        self.tbSelectedSig.setMaximumHeight(3000)
        self.tbSelectedSig.setColumnCount(3)
        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tbSelectedSig.setColumnHidden(1, True)
        self.tbSelectedSig.setHorizontalHeaderLabels(['KKS', 'Тег', 'Наименование'])
        self.tbSelectedSig.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbSelectedSig.setAlternatingRowColors(True)
        self.tbSelectedSig.setWordWrap(True)
        self.tbSelectedSig.doubleClicked.connect(self.tbSelectedItemDClicked)
        self.tbSelectedSig.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        # -------------------------------------------------

        # ------------------------------------------------- Groups filters

        self.lytGroups = QGridLayout()

        frm = QFrame()
        frm.setFrameShape(QFrame.HLine)
        frm.setFrameShadow(QFrame.Sunken)

        # -------------------------------------------------

        # +++++++++++++++++++++++++++++++++++++++++++++++++ Types filters

        self.tabwTypes = QTabWidget()
        self.tabwTypes.setSizePolicy(PyQt5.Qt.QSizePolicy.Minimum, PyQt5.Qt.QSizePolicy.Minimum)
        self.tabwTypes.currentChanged.connect(self.typesTabChanged)

        # ------------------------------------------------- Rbs

        self.wgtTypesRb = QWidget()

        self.lytTypesRb = QGridLayout()

        frmH = QFrame()
        frmH.setFrameShape(QFrame.HLine)
        frmH.setFrameShadow(QFrame.Sunken)

        self.lytTypesRb.addWidget(frmH, 1, 0, 1, 2)
        self.wgtTypesRb.setLayout(self.lytTypesRb)

        # -------------------------------------------------

        # ------------------------------------------------- Chbs

        self.wgtTypesChb = QWidget()

        self.btnChbSelectAll = QPushButton('Все')
        self.btnChbSelectAll.clicked.connect(self.btnChbStateClicked)

        self.btnChbSelectNone = QPushButton('Сброс')
        self.btnChbSelectNone.clicked.connect(self.btnChbStateClicked)

        frmH = QFrame()
        frmH.setFrameShape(QFrame.HLine)
        frmH.setFrameShadow(QFrame.Sunken)

        self.layoutChbTypes = QGridLayout()
        self.layoutChbTypes.addWidget(self.btnChbSelectAll, 0, 0, 1, 2)
        self.layoutChbTypes.addWidget(self.btnChbSelectNone, 1, 0, 1, 2)
        self.layoutChbTypes.addWidget(frmH, 2, 0, 1, 2)
        self.wgtTypesChb.setLayout(self.layoutChbTypes)

        # -------------------------------------------------

        self.tabwTypes.addTab(self.wgtTypesRb, 'ОДИН')
        self.tabwTypes.addTab(self.wgtTypesChb, 'МНОГО')

        # +++++++++++++++++++++++++++++++++++++++++++++++++

        # ------------------------------------------------- Columns view mode selection

        self.gbColumnsMode = QGroupBox('Колонки')

        self.listRbColumnsModes = [QRadioButton('KKS'), QRadioButton('Тег'), QRadioButton('KKS + Тег')]
        self.listRbColumnsModes[0].setChecked(True)

        self.lytColumnsMode = QGridLayout()

        for row, rb in enumerate(self.listRbColumnsModes):
            self.listRbColumnsModes[row].clicked.connect(self.rbViewClicked)
            self.lytColumnsMode.addWidget(self.listRbColumnsModes[row], row, 0)

        self.gbColumnsMode.setLayout(self.lytColumnsMode)

        # -------------------------------------------------

        # ------------------------------------------------- Filters apply mode selection

        self.gbFiltersMode = QGroupBox('Фильтровать')

        self.listRbFiltersMode = [QRadioButton('Все'), QRadioButton('Доступные')]
        self.listRbFiltersMode[0].setChecked(True)

        self.lytFiltersMode = QGridLayout()

        for row, rb in enumerate(self.listRbFiltersMode):
            self.listRbFiltersMode[row].clicked.connect(self.rbFiltersClicked)
            self.lytFiltersMode.addWidget(self.listRbFiltersMode[row], row, 0)

        self.gbFiltersMode.setLayout(self.lytFiltersMode)

        # -------------------------------------------------

        # ------------------------------------------------- Config import/export

        self.gbConfig = QGroupBox('Конфигурация')

        self.btnImport = QPushButton('Импорт')
        self.btnImport.clicked.connect(self.btnConfigClicked)
        self.btnExport = QPushButton('Экспорт')
        self.btnExport.clicked.connect(self.btnConfigClicked)

        self.lytConfig = QGridLayout()
        self.lytConfig.addWidget(self.btnImport, 0, 0)
        self.lytConfig.addWidget(self.btnExport, 1, 0)
        self.gbConfig.setLayout(self.lytConfig)

        # -------------------------------------------------

        # ------------------------------------------------- Signals move buttons

        self.btnAddSelected = QPushButton('>')
        self.btnAddAll = QPushButton('>>')
        self.btnRemAll = QPushButton('<<')
        self.btnRemSelected = QPushButton('<')

        self.lytMoveButtons = QVBoxLayout()
        self.lytMoveButtons.addWidget(self.btnAddSelected, 0)
        self.lytMoveButtons.addWidget(self.btnAddAll, 1)
        self.lytMoveButtons.addWidget(self.btnRemAll, 2)
        self.lytMoveButtons.addWidget(self.btnRemSelected, 3)

        # -------------------------------------------------

        self.lblTotalPossible = QLabel('[0]')
        self.lblTotalSelected = QLabel('[0]')

        # Filters fields
        self.leFiltersPos = QLineEdit()
        self.leFiltersPos.setClearButtonEnabled(True)
        self.leFiltersPos.setPlaceholderText('Введите фильтр...')

        self.leFiltersSel = QLineEdit()
        self.leFiltersSel.setClearButtonEnabled(True)
        self.leFiltersSel.setPlaceholderText('Введите фильтр...')

        frmH = QFrame()
        frmH.setFrameShape(QFrame.HLine)
        frmH.setFrameShadow(QFrame.Sunken)

        frmV = QFrame()
        frmV.setFrameShape(QFrame.VLine)
        frmV.setFrameShadow(QFrame.Sunken)

        self.lytRight = QGridLayout()

        self.lytRight.addWidget(self.tabwTypes, 0, 0)
        self.lytRight.addWidget(self.gbColumnsMode, 1, 0)
        self.lytRight.addWidget(self.gbFiltersMode, 2, 0)
        self.lytRight.addWidget(self.gbConfig, 3, 0)

        self.lytRight.addItem(QSpacerItem(1, 1, PyQt5.Qt.QSizePolicy.Minimum,
                                          PyQt5.Qt.QSizePolicy.Expanding), 4, 0)

        self.gbSignals = QGroupBox('Выбор выгружаемых сигналов')
        self.gbSignals.setSizePolicy(PyQt5.Qt.QSizePolicy.Expanding, PyQt5.Qt.QSizePolicy.Expanding)

        self.lytSignals = QGridLayout()
        self.lytSignals.setRowStretch(4, 1)

        self.lytSignals.setColumnStretch(0, 1)
        self.lytSignals.setColumnStretch(1, 1)
        self.lytSignals.setColumnStretch(3, 1)
        self.lytSignals.setColumnStretch(4, 1)

        self.lytSignals.addWidget(QLabel('Доступные сигналы:'), 3, 0)
        self.lytSignals.addWidget(self.tbPossibleSig, 4, 0, 3, 2)
        self.lytSignals.addWidget(self.lblTotalPossible, 3, 1, PyQt5.QtCore.Qt.AlignRight)

        self.lytSignals.addWidget(QLabel('Выбранные сигналы:'), 3, 3)
        self.lytSignals.addWidget(self.tbSelectedSig, 4, 3, 3, 2)
        self.lytSignals.addWidget(self.lblTotalSelected, 3, 4, PyQt5.QtCore.Qt.AlignRight)

        self.lytSignals.addLayout(self.lytMoveButtons, 4, 2, 1, 1)
        self.lytSignals.addItem(QSpacerItem(1, 3000, PyQt5.Qt.QSizePolicy.Minimum,
                                            PyQt5.Qt.QSizePolicy.Expanding), 5, 1)

        self.lytSignals.addWidget(QLabel('Технологическая группа:'), 0, 0, 1, 5)
        self.lytSignals.addLayout(self.lytGroups, 1, 0, 1, 5)
        self.lytSignals.addWidget(frmH, 2, 0, 1, 5)

        self.lytSignals.addLayout(self.lytRight, 4, 6, 4, 1)
        self.lytSignals.addWidget(frmV, 4, 5, 4, 1)

        self.lytSignals.addWidget(self.leFiltersPos, 7, 0, 1, 2)
        self.lytSignals.addWidget(self.leFiltersSel, 7, 3, 1, 2)

        self.gbSignals.setLayout(self.lytSignals)

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        # ------------------------------------------------- Time

        self.gbTime = QGroupBox('Интервал выгрузки')
        self.layoutTime = QGridLayout()

        self.dteBeginTime = QTimeEdit()
        self.dteBeginTime.setDisplayFormat('hh:mm:ss')
        self.dteEndTime = QTimeEdit()
        self.dteEndTime.setDisplayFormat('hh:mm:ss')

        self.dteBeginDate = QDateEdit()
        self.dteBeginDate.setDisplayFormat('yyyy.MM.dd')
        self.dteEndDate = QDateEdit()
        self.dteEndDate.setDisplayFormat('yyyy.MM.dd')

        self.layoutTime.addWidget(QLabel('От:'), 0, 0)
        self.layoutTime.addWidget(self.dteBeginDate, 0, 1)
        self.layoutTime.addWidget(self.dteBeginTime, 0, 2)

        self.layoutTime.addWidget(QLabel('До:'), 0, 3)
        self.layoutTime.addWidget(self.dteEndDate, 0, 4)
        self.layoutTime.addWidget(self.dteEndTime, 0, 5)

        self.gbTime.setLayout(self.layoutTime)
        self.gbTime.setSizePolicy(PyQt5.Qt.QSizePolicy.Minimum, PyQt5.Qt.QSizePolicy.Minimum)

        # -------------------------------------------------

        # ------------------------------------------------- File path

        self.gbFolder = QGroupBox('Директория сохранения')

        self.btnSelectDataSP = QPushButton('Выбрать')
        self.btnSelectDataSP.clicked.connect(self.btnSavePathClicked)
        self.leDataPath = QLineEdit()

        self.lytFolder = QGridLayout()
        self.lytFolder.setColumnStretch(0, 1)
        self.lytFolder.addWidget(self.leDataPath, 0, 0)
        self.lytFolder.addWidget(self.btnSelectDataSP, 0, 1)

        self.gbFolder.setLayout(self.lytFolder)

        # -------------------------------------------------

        # ------------------------------------------------- Main window

        self.setWindowTitle('Утилита выгрузки трендов САУ ПТУ ПТ-150/160-12,8. Версия 1.06.04, 2022-02-20 @INTAY')

        self.btnDo = QPushButton('Выполнить выгрузку')
        self.btnDo.clicked.connect(self.btnDoClicked)

        self.lblUploadStatus = QLabel('Начало выгрузки...')
        self.lblUploadStatus.hide()

        self.layoutMain = QGridLayout()
        self.layoutMain.addWidget(self.gbSignals, 0, 0, 1, 2)
        self.layoutMain.addWidget(self.gbFolder, 1, 1)
        self.layoutMain.addWidget(self.gbTime, 1, 0)
        self.layoutMain.addWidget(self.btnDo, 3, 0, 1, 2)
        self.layoutMain.addWidget(self.lblUploadStatus, 4, 0, 1, 2)
        self.setLayout(self.layoutMain)

        self.setGeometry(100, 100, 700, 100)

        # -------------------------------------------------

    def setBeginEndTime(self, beginTime, endTime):
        pass

    def remSelected(self):
        pass

    def tbPossibleItemDClicked(self, index):
        pass

    def tbSelectedItemDClicked(self, index):
        pass

    def rbGroupsClicked(self):
        pass

    def typesTabChanged(self, index):
        pass

    def rbViewClicked(self):
        pass

    def rbTypesClicked(self):
        pass

    def rbFiltersClicked(self):
        pass

    def chbTypesClicked(self):
        pass

    def btnChbStateClicked(self):
        pass

    def applyFiltersTPossible(self, filterGroup=None, filterType=None):
        pass

    def applyFiltersTSelected(self, filterGroup=None, filterType=None):
        pass

    def btnConfigClicked(self):
        pass

    def btnSavePathClicked(self):
        pass

    def btnDoClicked(self):
        pass

    def closeEvent(self, event):
        pass

    def getData(self):
        pass

    def checkErr(self):
        pass

    def toggleUploadMode(self, state):
        pass

    def setUploadState(self, text):
        pass

    def throwMessageBox(self, title, text):
        pass