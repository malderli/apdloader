import PyQt5.Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QDateTimeEdit, QTableWidget, QLineEdit, QRadioButton
from PyQt5.QtWidgets import QFrame, QTabWidget, QWidget, QCheckBox, QSpacerItem, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal


class SelectorWindow(QtWidgets.QWidget):
    signalClose = pyqtSignal()

    def __init__(self, sigData = None):
        super(QtWidgets.QWidget, self).__init__()

        # Data
        self.signalGroups = []
        self.signalTypes = []
        self.signals = {}

        self.selectedSignals = []
        self.sortHelper = {}

        self.filteringMode = 'OR' # 'OR' | 'AND'

        if sigData != None:
            self.signalGroups = sigData['SIGNALGROUPS']
            self.signalTypes = sigData['SIGNALTYPES']
            self.signals = sigData['SIGNALS']

        self.currTypeFilters = self.signalTypes
        self.currGroupFilters = self.signalGroups

        for kks in self.signals.keys():
            # Adding feild 'selected' to each signal
            self.signals[kks]['SELECTED'] = False

            # Forming sort dict
            if (self.signals[kks]['GROUP'], self.signals[kks]['TYPE']) not in self.sortHelper:
                self.sortHelper[(self.signals[kks]['GROUP'], self.signals[kks]['TYPE'])] = []

            self.sortHelper[(self.signals[kks]['GROUP'], self.signals[kks]['TYPE'])].append(kks)

        # Time selecting part
        self.gbTime = QGroupBox('Выбор интервала выгрузки')
        self.layoutTime = QGridLayout()

        self.dteBeginTime = QDateTimeEdit()
        self.dteBeginTime.setDisplayFormat("yyyy.MM.dd hh:mm:ss")
        self.dteEndTime = QDateTimeEdit()
        self.dteEndTime.setDisplayFormat("yyyy.MM.dd hh:mm:ss")

        self.layoutTime.addWidget(QLabel('От:'), 0, 0)
        self.layoutTime.addWidget(self.dteBeginTime, 0, 1)
        self.layoutTime.addWidget(QLabel('До:'), 0, 2)
        self.layoutTime.addWidget(self.dteEndTime, 0, 3)

        self.gbTime.setLayout(self.layoutTime)
        self.gbTime.setSizePolicy(PyQt5.Qt.QSizePolicy.Minimum, PyQt5.Qt.QSizePolicy.Minimum)

        # Signals selecting part
        self.gbSignals = QGroupBox('Выбор выгружаемых сигналов')
        self.layoutSignals = QGridLayout()
        self.layoutSignals.setRowStretch(4, 1)

        # Signals group box
        self.tbPossibleSig = QTableWidget()
        self.tbPossibleSig.setMaximumHeight(3000)
        self.tbPossibleSig.setColumnCount(2)
        self.tbPossibleSig.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbPossibleSig.setHorizontalHeaderLabels(['KKS', 'Наименование'])
        self.tbPossibleSig.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbPossibleSig.setAlternatingRowColors(True)
        self.tbPossibleSig.setWordWrap(True)
        self.tbPossibleSig.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        self.tbSelectedSig = QTableWidget()
        self.tbSelectedSig.setMaximumHeight(3000)
        self.tbSelectedSig.setColumnCount(2)
        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbSelectedSig.setHorizontalHeaderLabels(['KKS', 'Наименование'])
        self.tbSelectedSig.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbSelectedSig.setAlternatingRowColors(True)
        self.tbSelectedSig.setWordWrap(True)
        self.tbSelectedSig.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        self.layoutSignals.addWidget(QLabel('Доступные сигналы:'), 3, 0)
        self.layoutSignals.addWidget(self.tbPossibleSig, 4, 0, 3, 1)

        self.layoutSignals.addWidget(QLabel('Выбранные сигналы:'), 3, 2)
        self.layoutSignals.addWidget(self.tbSelectedSig, 4, 2, 3, 1)

        self.btnAddSelected = QPushButton('>')
        self.btnAddAll = QPushButton('>>')
        self.btnRemAll = QPushButton('<<')
        self.btnRemSelected = QPushButton('<')

        self.subLayout = QVBoxLayout()
        self.subLayout.addWidget(self.btnAddSelected, 0, PyQt5.QtCore.Qt.AlignCenter)
        self.subLayout.addWidget(self.btnAddAll, 1, PyQt5.QtCore.Qt.AlignBottom)
        self.subLayout.addWidget(self.btnRemAll, 2, PyQt5.QtCore.Qt.AlignTop)
        self.subLayout.addWidget(self.btnRemSelected, 3, PyQt5.QtCore.Qt.AlignBottom)

        self.layoutSignals.addLayout(self.subLayout, 4, 1, 1, 1)
        self.layoutSignals.addItem(QSpacerItem(1, 3000, PyQt5.Qt.QSizePolicy.Minimum,
                                               PyQt5.Qt.QSizePolicy.Expanding), 5, 1)

        self.gbSignals.setLayout(self.layoutSignals)
        self.gbSignals.setSizePolicy(PyQt5.Qt.QSizePolicy.Expanding, PyQt5.Qt.QSizePolicy.Expanding)

        # - Groups
        self.layoutSignals.addWidget(QLabel('Выборка по технологической группе:'), 0, 0, 1, 3)

        self.layoutGroups = QGridLayout()
        self.listRbGroups = []

        for pos, group in enumerate(['Все'] + self.signalGroups):
            self.listRbGroups.append(QRadioButton(group))
            self.listRbGroups[-1].clicked.connect(self.rbGroupsClicked)
            self.layoutGroups.addWidget(self.listRbGroups[-1], 0, pos)

        self.layoutGroups.addItem(QSpacerItem(1, 1, PyQt5.Qt.QSizePolicy.Expanding,
                                             PyQt5.Qt.QSizePolicy.Minimum), 0, len(self.signalGroups) + 1)

        self.listRbGroups[0].setChecked(True)

        self.layoutSignals.addLayout(self.layoutGroups, 1, 0, 1, 3)

        frm = QFrame(); frm.setFrameShape(QFrame.HLine); frm.setFrameShadow(QFrame.Sunken)
        self.layoutSignals.addWidget(frm, 2, 0, 1, 3)

        # - Types
        self.twTypes = QTabWidget()
        self.twTypes.setSizePolicy(PyQt5.Qt.QSizePolicy.Minimum, PyQt5.Qt.QSizePolicy.Minimum)
        self.twTypes.currentChanged.connect(self.typesTabChanged)

        self.layoutTypes = QGridLayout()

        self.wgtTypesRb = QWidget()
        self.wgtTypesChb = QWidget()

        # -- Rbs
        self.layoutRbTypes = QGridLayout()
        self.listRbTypes = []

        frm = QFrame(); frm.setFrameShape(QFrame.HLine); frm.setFrameShadow(QFrame.Sunken)
        self.layoutRbTypes.addWidget(frm, 2, 0, 1, 2)

        for pos, TYPE in enumerate(['Все', 'Ничто'] + self.signalTypes):
            self.listRbTypes.append(QRadioButton(TYPE))
            self.listRbTypes[-1].clicked.connect(self.rbTypesClicked)

            if pos <= 1:
                self.layoutRbTypes.addWidget(self.listRbTypes[-1], pos, 0)
            else:
                self.layoutRbTypes.addWidget(self.listRbTypes[-1],
                                             3 + (pos - 2) % ((len(self.signalTypes) + 1) // 2),
                                             (pos - 2) // ((len(self.signalTypes) + 1) // 2))

        self.listRbTypes[0].setChecked(True)

        # -- Chbs
        self.layoutChbTypes = QGridLayout()
        self.listChbTypes = []

        self.btnChbSelectAll = QPushButton('Все')
        self.btnChbSelectAll.clicked.connect(self.btnChbStateClicked)
        self.layoutChbTypes.addWidget(self.btnChbSelectAll, 0, 0, 1, 2)

        self.btnChbSelectNone = QPushButton('Ничто')
        self.btnChbSelectNone.clicked.connect(self.btnChbStateClicked)
        self.layoutChbTypes.addWidget(self.btnChbSelectNone, 1, 0, 1, 2)

        frm = QFrame(); frm.setFrameShape(QFrame.HLine); frm.setFrameShadow(QFrame.Sunken)
        self.layoutChbTypes.addWidget(frm, 2, 0, 1, 2)

        for pos, TYPE in enumerate(self.signalTypes):
            self.listChbTypes.append(QCheckBox(TYPE))
            self.listChbTypes[-1].clicked.connect(self.chbTypesClicked)
            self.listChbTypes[-1].setChecked(True)

            self.layoutChbTypes.addWidget(self.listChbTypes[-1],
                                         3 + pos % ((len(self.signalTypes) + 1) // 2),
                                         pos // ((len(self.signalTypes) + 1) // 2))

        self.wgtTypesRb.setLayout(self.layoutRbTypes)
        self.wgtTypesChb.setLayout(self.layoutChbTypes)

        self.twTypes.addTab(self.wgtTypesRb, 'ИЛИ')
        self.twTypes.addTab(self.wgtTypesChb, 'И')

        self.layoutTypes.addWidget(self.twTypes, 0, 0)
        self.layoutTypes.addItem(QSpacerItem(1, 1, PyQt5.Qt.QSizePolicy.Minimum,
                                               PyQt5.Qt.QSizePolicy.Expanding), 1, 0)

        self.layoutSignals.addLayout(self.layoutTypes, 4, 4, 3, 1)

        frm = QFrame(); frm.setFrameShape(QFrame.VLine); frm.setFrameShadow(QFrame.Sunken)
        self.layoutSignals.addWidget(frm, 4, 3, 3, 1)

        # File path
        self.gbFolder = QGroupBox('Выбор директории сохранения')
        self.layoutFolder = QGridLayout()
        self.layoutFolder.setColumnStretch(0, 1)

        self.leFolderPath = QLineEdit()
        self.btnSelectFolder = QPushButton('Открыть')

        self.layoutFolder.addWidget(self.leFolderPath, 0, 0)
        self.layoutFolder.addWidget(self.btnSelectFolder, 0, 1)

        self.gbFolder.setLayout(self.layoutFolder)

        # Filling signal tables with data
        self.applyFiltersTPossible(self.currGroupFilters, self.currTypeFilters)

        # Main window
        self.setWindowTitle('Утилита выгрузки трендов САУ ПТУ ПТ-150/160-12,8. Версия 1.01.14, 2022-01-22 @INTAY')
        self.mainLayout = QGridLayout()

        self.btnDo = QPushButton('Выполнить выгрузку')

        self.mainLayout.addWidget(self.gbSignals, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.gbFolder, 1, 1)
        self.mainLayout.addWidget(self.gbTime, 1, 0)
        self.mainLayout.addWidget(self.btnDo, 3, 0, 1, 2)

        self.setGeometry(100, 100, 700, 100)
        self.setLayout(self.mainLayout)

    def setBeginEndTime(self, beginTime, endTime):
        pass

    def setSignalsData(self, sigData):
        pass

    def tbPossibleDClicked(self):
        pass

    # Changing shown group after rb click
    def rbGroupsClicked(self):
        if self.sender() == self.listRbGroups[0]:
            self.currGroupFilters = self.signalGroups
        else:
            self.currGroupFilters = [self.sender().text()]

        self.applyFiltersTPossible()

    def typesTabChanged(self, index):
        if index == 0:
            for rb in self.listRbTypes:
                if rb.isChecked():
                    rb.click()
                    break
        else:
            self.currTypeFilters = []

            for chb in self.listChbTypes:
                if chb.isChecked():
                    self.currTypeFilters.append(chb.text())

            self.applyFiltersTPossible()

    # Changing shown types after rb click
    def rbTypesClicked(self):
        if self.sender() == self.listRbTypes[0]:
            self.currTypeFilters = self.signalTypes
        elif self.sender() == self.listRbTypes[1]:
            self.currTypeFilters = []
        else:
            self.currTypeFilters = [self.sender().text()]

        self.applyFiltersTPossible()

    def chbTypesClicked(self):
        if self.sender().isChecked():
            self.currTypeFilters.append(self.sender().text())
            self.currTypeFilters.sort()
        else:
            self.currTypeFilters.remove(self.sender().text())

        self.applyFiltersTPossible()

    def btnChbStateClicked(self):
        if self.sender() == self.btnChbSelectAll:
            for chb in self.listChbTypes:
                chb.setChecked(True)
            self.currTypeFilters = self.signalTypes
        elif self.sender() == self.btnChbSelectNone:
            for chb in self.listChbTypes:
                chb.setChecked(False)
            self.currTypeFilters = []

        self.applyFiltersTPossible()

    # Applying current group and type filters state to data in table with possible signals
    def applyFiltersTPossible(self, filterGroup = None, filterType = None):
        row = 0

        if filterGroup == None:
            filterGroup = self.currGroupFilters
        if filterType == None:
            filterType = self.currTypeFilters

        self.tbPossibleSig.setRowCount(0)
        self.tbPossibleSig.clear()
        self.tbPossibleSig.setHorizontalHeaderLabels(['KKS', 'Наименование'])

        for group in filterGroup:
            for TYPE in filterType:
                if (group, TYPE) in self.sortHelper:
                    self.tbPossibleSig.setRowCount(self.tbPossibleSig.rowCount() + len(self.sortHelper[(group, TYPE)]))

                    for kks in self.sortHelper[(group, TYPE)]:
                        self.tbPossibleSig.setItem(row, 0, QTableWidgetItem(kks))
                        self.tbPossibleSig.setItem(row, 1, QTableWidgetItem(self.signals[kks]['TEXT']))
                        self.tbPossibleSig.setRowHeight(row, 35)
                        row += 1

        self.tbPossibleSig.resizeColumnToContents(0)

    # Applying current group and type filters state to data in table with selected signals
    def applyFiltersTSelected(self, filterGroup, filterType):
        row = 0

        if filterGroup == None:
            filterGroup = self.currGroupFilters
        if filterType == None:
            filterType = self.currTypeFilters
