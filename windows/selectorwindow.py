import PyQt5.Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QDateEdit, QTimeEdit, QTableWidget, QLineEdit, QRadioButton
from PyQt5.QtWidgets import QFrame, QTabWidget, QWidget, QCheckBox, QSpacerItem, QHeaderView, QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QColor, QCloseEvent, QMovie
from PyQt5.QtCore import pyqtSignal

from datetime import datetime

class SelectorWindow(QtWidgets.QWidget):
    signalDo = pyqtSignal()

    def __init__(self, sigData = None):
        super(QtWidgets.QWidget, self).__init__()

        self.errCode = 0
        self.colorSelected = QColor('#8DDF8D')

        self.jobDone = False

        # Data
        self.signalGroups = []
        self.signalTypes = []
        self.signals = {}

        self.selectedSignals = []
        self.sortHelper = {}

        self.viewMode = 0

        if sigData != None:
            self.signalGroups = sigData['SIGNALGROUPS']
            self.signalTypes = sigData['SIGNALTYPES']
            self.signals = sigData['SIGNALS']

        self.currTypeFilters = self.signalTypes.copy()
        self.currGroupFilters = self.signalGroups.copy()

        for tag in self.signals.keys():
            # Adding feild 'selected' to each signal
            self.signals[tag]['SELECTED'] = False

            # Forming sort dict
            if (self.signals[tag]['GROUP'], self.signals[tag]['TYPE']) not in self.sortHelper:
                self.sortHelper[(self.signals[tag]['GROUP'], self.signals[tag]['TYPE'])] = []

            self.sortHelper[(self.signals[tag]['GROUP'], self.signals[tag]['TYPE'])].append(tag)

        # Time selecting part
        self.gbTime = QGroupBox('Выбор интервала выгрузки')
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
        self.layoutTime.addWidget(QLabel('До:'), 1, 0)
        self.layoutTime.addWidget(self.dteEndDate, 1, 1)
        self.layoutTime.addWidget(self.dteEndTime, 1, 2)

        self.gbTime.setLayout(self.layoutTime)
        self.gbTime.setSizePolicy(PyQt5.Qt.QSizePolicy.Minimum, PyQt5.Qt.QSizePolicy.Minimum)

        # Signals selecting part
        self.gbSignals = QGroupBox('Выбор выгружаемых сигналов')
        self.layoutSignals = QGridLayout()
        self.layoutSignals.setRowStretch(4, 1)
        self.layoutSignals.setColumnStretch(0, 1)
        self.layoutSignals.setColumnStretch(1, 1)
        self.layoutSignals.setColumnStretch(3, 1)
        self.layoutSignals.setColumnStretch(4, 1)

        # Signals group box
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

        self.layoutSignals.addWidget(QLabel('Доступные сигналы:'), 3, 0)
        self.layoutSignals.addWidget(self.tbPossibleSig, 4, 0, 3, 2)

        self.lblTotalPossible = QLabel('[{}]'.format(len(self.signals.keys())))
        self.layoutSignals.addWidget(self.lblTotalPossible, 3, 1, PyQt5.QtCore.Qt.AlignRight)

        self.layoutSignals.addWidget(QLabel('Выбранные сигналы:'), 3, 3)
        self.layoutSignals.addWidget(self.tbSelectedSig, 4, 3, 3, 2)

        self.lblTotalSelected = QLabel('[0]')
        self.layoutSignals.addWidget(self.lblTotalSelected, 3, 4, PyQt5.QtCore.Qt.AlignRight)

        self.btnAddSelected = QPushButton('>')
        self.btnAddSelected.clicked.connect(self.addPossible)
        self.btnAddAll = QPushButton('>>')
        self.btnAddAll.clicked.connect(self.addPossible)
        self.btnRemAll = QPushButton('<<')
        self.btnRemAll.clicked.connect(self.remSelected)
        self.btnRemSelected = QPushButton('<')
        self.btnRemSelected.clicked.connect(self.remSelected)

        self.subLayout = QVBoxLayout()
        # !!!!!!!!!!!!!!!! Make align center
        # self.subLayout.setAlignment(PyQt5.Qt.Qt.AlignCenter)
        # self.subLayout.addWidget(self.btnAddSelected, 0, PyQt5.QtCore.Qt.AlignCenter)
        # self.subLayout.addWidget(self.btnAddAll, 1, PyQt5.QtCore.Qt.AlignBottom)
        # self.subLayout.addWidget(self.btnAddAll, 1, PyQt5.QtCore.Qt.AlignBottom)
        # self.subLayout.addWidget(self.btnRemAll, 2, PyQt5.QtCore.Qt.AlignBottom)
        # self.subLayout.addWidget(self.btnRemSelected, 3, PyQt5.QtCore.Qt.AlignBottom)

        self.subLayout.addWidget(self.btnAddSelected, 0)
        self.subLayout.addWidget(self.btnAddAll, 1)
        self.subLayout.addWidget(self.btnRemAll, 2)
        self.subLayout.addWidget(self.btnRemSelected, 3)

        self.layoutSignals.addLayout(self.subLayout, 4, 2, 1, 1)
        self.layoutSignals.addItem(QSpacerItem(1, 3000, PyQt5.Qt.QSizePolicy.Minimum,
                                               PyQt5.Qt.QSizePolicy.Expanding), 5, 1)

        # - Groups
        self.layoutSignals.addWidget(QLabel('Выборка по технологической группе:'), 0, 0, 1, 5)

        self.layoutGroups = QGridLayout()
        self.listRbGroups = []

        for pos, group in enumerate(['Все'] + self.signalGroups):
            self.listRbGroups.append(QRadioButton(group))
            self.listRbGroups[-1].clicked.connect(self.rbGroupsClicked)
            self.layoutGroups.addWidget(self.listRbGroups[-1], 0, pos)

        self.layoutGroups.addItem(QSpacerItem(1, 1, PyQt5.Qt.QSizePolicy.Expanding,
                                             PyQt5.Qt.QSizePolicy.Minimum), 0, len(self.signalGroups) + 1)

        self.listRbGroups[0].setChecked(True)

        self.layoutSignals.addLayout(self.layoutGroups, 1, 0, 1, 5)

        frm = QFrame(); frm.setFrameShape(QFrame.HLine); frm.setFrameShadow(QFrame.Sunken)
        self.layoutSignals.addWidget(frm, 2, 0, 1, 5)

        # - Types
        self.twTypes = QTabWidget()
        self.twTypes.setSizePolicy(PyQt5.Qt.QSizePolicy.Minimum, PyQt5.Qt.QSizePolicy.Minimum)
        self.twTypes.currentChanged.connect(self.typesTabChanged)

        self.layoutRight = QGridLayout()

        self.wgtTypesRb = QWidget()
        self.wgtTypesChb = QWidget()

        # -- Rbs
        self.layoutRbTypes = QGridLayout()
        self.listRbTypes = []

        frm = QFrame(); frm.setFrameShape(QFrame.HLine); frm.setFrameShadow(QFrame.Sunken)
        self.layoutRbTypes.addWidget(frm, 1, 0, 1, 2)

        for pos, TYPE in enumerate(['Все'] + self.signalTypes):
            self.listRbTypes.append(QRadioButton(TYPE))
            self.listRbTypes[-1].clicked.connect(self.rbTypesClicked)

            if pos == 0:
                self.layoutRbTypes.addWidget(self.listRbTypes[-1], pos, 0)
            else:
                self.layoutRbTypes.addWidget(self.listRbTypes[-1],
                                             2 + (pos - 1) % ((len(self.signalTypes) + 1) // 2),
                                             (pos - 1) // ((len(self.signalTypes) + 1) // 2))

        self.listRbTypes[0].setChecked(True)

        # -- Chbs
        self.layoutChbTypes = QGridLayout()
        self.listChbTypes = []

        self.btnChbSelectAll = QPushButton('Все')
        self.btnChbSelectAll.clicked.connect(self.btnChbStateClicked)
        self.layoutChbTypes.addWidget(self.btnChbSelectAll, 0, 0, 1, 2)

        self.btnChbSelectNone = QPushButton('Сброс')
        self.btnChbSelectNone.clicked.connect(self.btnChbStateClicked)
        self.layoutChbTypes.addWidget(self.btnChbSelectNone, 1, 0, 1, 2)

        frm = QFrame();
        frm.setFrameShape(QFrame.HLine);
        frm.setFrameShadow(QFrame.Sunken)
        self.layoutChbTypes.addWidget(frm, 2, 0, 1, 2)

        for pos, TYPE in enumerate(self.signalTypes):
            self.listChbTypes.append(QCheckBox(TYPE))
            self.listChbTypes[-1].clicked.connect(self.chbTypesClicked)
            self.listChbTypes[-1].setChecked(True)

            self.layoutChbTypes.addWidget(self.listChbTypes[-1],
                                          3 + pos % ((len(self.signalTypes) + 1) // 2),
                                          pos // ((len(self.signalTypes) + 1) // 2))

        # View mode selection
        self.layoutView = QGridLayout()
        self.gbView = QGroupBox('Колонки')

        self.listRbView = [QRadioButton('KKS'), QRadioButton('Тег'), QRadioButton('KKS + Тег')]
        self.listRbView[0].setChecked(True)

        for row, rb in enumerate(self.listRbView):
            self.listRbView[row].clicked.connect(self.rbViewClicked)
            self.layoutView.addWidget(self.listRbView[row], row, 0)

        self.gbView.setLayout(self.layoutView)

        # Config import/export
        self.gbConfig = QGroupBox('Конфигурация')
        self.layoutConfig = QGridLayout()

        self.btnImport = QPushButton('Импорт')
        self.btnImport.clicked.connect(self.btnConfigClicked)
        self.btnExport = QPushButton('Экспорт')
        self.btnExport.clicked.connect(self.btnConfigClicked)

        self.layoutConfig.addWidget(self.btnImport, 0, 0)
        self.layoutConfig.addWidget(self.btnExport, 1, 0)

        self.gbConfig.setLayout(self.layoutConfig)

        # Right layout filling
        self.wgtTypesRb.setLayout(self.layoutRbTypes)
        self.wgtTypesChb.setLayout(self.layoutChbTypes)

        self.twTypes.addTab(self.wgtTypesRb, 'ИЛИ')
        self.twTypes.addTab(self.wgtTypesChb, 'И')
        self.layoutRight.addWidget(self.twTypes, 0, 0)
        self.layoutRight.addWidget(self.gbView, 1, 0)
        self.layoutRight.addWidget(self.gbConfig, 2, 0)
        self.layoutRight.addItem(QSpacerItem(1, 1, PyQt5.Qt.QSizePolicy.Minimum,
                                             PyQt5.Qt.QSizePolicy.Expanding), 3, 0)

        self.layoutSignals.addLayout(self.layoutRight, 4, 6, 3, 1)

        frm = QFrame();
        frm.setFrameShape(QFrame.VLine);
        frm.setFrameShadow(QFrame.Sunken)
        self.layoutSignals.addWidget(frm, 4, 5, 3, 1)

        self.gbSignals.setLayout(self.layoutSignals)
        self.gbSignals.setSizePolicy(PyQt5.Qt.QSizePolicy.Expanding, PyQt5.Qt.QSizePolicy.Expanding)

        # Files path
        self.gbFolder = QGroupBox('Выбор директории сохранения')
        self.layoutFolder = QGridLayout()
        self.layoutFolder.setColumnStretch(1, 1)

        self.leDataPath = QLineEdit()
        self.btnSelectDataSP = QPushButton('Выбрать')
        self.btnSelectDataSP.clicked.connect(self.btnSavePathClicked)

        self.leNamesPath = QLineEdit()
        self.btnSelectNamesSP = QPushButton('Выбрать')
        self.btnSelectNamesSP.clicked.connect(self.btnSavePathClicked)

        self.layoutFolder.addWidget(QLabel('Данные:'), 0, 0)
        self.layoutFolder.addWidget(self.leDataPath, 0, 1)
        self.layoutFolder.addWidget(self.btnSelectDataSP, 0, 2)

        self.layoutFolder.addWidget(QLabel('Имена:'), 1, 0)
        self.layoutFolder.addWidget(self.leNamesPath, 1, 1)
        self.layoutFolder.addWidget(self.btnSelectNamesSP, 1, 2)

        self.gbFolder.setLayout(self.layoutFolder)

        # Filling signal tables with data
        self.applyFiltersTPossible(self.currGroupFilters, self.currTypeFilters)

        # Main window
        self.setWindowTitle('Утилита выгрузки трендов САУ ПТУ ПТ-150/160-12,8. Версия 1.06.04, 2022-02-20 @INTAY')
        self.mainLayout = QGridLayout()

        self.btnDo = QPushButton('Выполнить выгрузку')
        self.btnDo.clicked.connect(self.btnDoClicked)

        self.mainLayout.addWidget(self.gbSignals, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.gbFolder, 1, 1)
        self.mainLayout.addWidget(self.gbTime, 1, 0)
        self.mainLayout.addWidget(self.btnDo, 3, 0, 1, 2)

        self.setGeometry(100, 100, 700, 100)
        self.setLayout(self.mainLayout)

    def setBeginEndTime(self, beginTime, endTime):
        pass

    def addPossible(self):
        if self.sender() == self.btnAddAll:
            self.tbPossibleSig.selectAll()

        for index in self.tbPossibleSig.selectedIndexes():
            self.tbPossibleSig.item(index.row(), 0).setBackground(self.colorSelected)
            self.tbPossibleSig.item(index.row(), 1).setBackground(self.colorSelected)
            self.tbPossibleSig.item(index.row(), 2).setBackground(self.colorSelected)

            self.signals[self.tbPossibleSig.item(index.row(), 1).text()]['SELECTED'] = True
            if self.tbPossibleSig.item(index.row(), 1).text() not in self.selectedSignals:
                self.selectedSignals.append(self.tbPossibleSig.item(index.row(), 1).text())

        self.lblTotalSelected.setText('[{}]'.format(len(self.selectedSignals)))

        self.tbPossibleSig.clearSelection()
        self.applyFiltersTSelected()

    def remSelected(self):
        if self.sender() == self.btnRemAll:
            self.tbSelectedSig.selectAll()

        for index in self.tbSelectedSig.selectedIndexes():
            self.signals[self.tbSelectedSig.item(index.row(), 1).text()]['SELECTED'] = False

            if self.tbSelectedSig.item(index.row(), 1).text() in self.selectedSignals:
                self.selectedSignals.remove(self.tbSelectedSig.item(index.row(), 1).text())

        self.lblTotalSelected.setText('[{}]'.format(len(self.selectedSignals)))

        self.tbSelectedSig.clearSelection()
        self.applyFiltersTPossible()
        self.applyFiltersTSelected()

    # Add signal to selected after double click
    def tbPossibleItemDClicked(self, index):
        self.tbPossibleSig.item(index.row(), 0).setBackground(self.colorSelected)
        self.tbPossibleSig.item(index.row(), 1).setBackground(self.colorSelected)
        self.tbPossibleSig.item(index.row(), 2).setBackground(self.colorSelected)

        self.signals[self.tbPossibleSig.item(index.row(), 1).text()]['SELECTED'] = True
        if self.tbPossibleSig.item(index.row(), 1).text() not in self.selectedSignals:
            self.selectedSignals.append(self.tbPossibleSig.item(index.row(), 1).text())

        self.lblTotalSelected.setText('[{}]'.format(len(self.selectedSignals)))

        self.tbPossibleSig.clearSelection()
        self.applyFiltersTSelected()

    # Remove signal from selected after double click
    def tbSelectedItemDClicked(self, index):
        self.signals[self.tbSelectedSig.item(index.row(), 1).text()]['SELECTED'] = False

        if self.tbSelectedSig.item(index.row(), 1).text() in self.selectedSignals:
            self.selectedSignals.remove(self.tbSelectedSig.item(index.row(), 1).text())

        self.lblTotalSelected.setText('[{}]'.format(len(self.selectedSignals)))

        self.tbSelectedSig.clearSelection()
        self.applyFiltersTPossible()
        self.applyFiltersTSelected()

    # Changing shown group after rb click
    def rbGroupsClicked(self):
        if self.sender() == self.listRbGroups[0]:
            self.currGroupFilters = self.signalGroups.copy()
        else:
            self.currGroupFilters = [self.sender().text()]

        self.applyFiltersTPossible()
        self.applyFiltersTSelected()

    # Type filtering mode(tab of twTypes) changed
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
            self.applyFiltersTSelected()

    def rbViewClicked(self):
        self.viewMode = self.listRbView.index(self.sender())

        if self.viewMode == 0:
            self.tbPossibleSig.setColumnHidden(0, False)
            self.tbPossibleSig.setColumnHidden(1, True)
            self.tbSelectedSig.setColumnHidden(0, False)
            self.tbSelectedSig.setColumnHidden(1, True)
        elif self.viewMode == 1:
            self.tbPossibleSig.setColumnHidden(0, True)
            self.tbPossibleSig.setColumnHidden(1, False)
            self.tbSelectedSig.setColumnHidden(0, True)
            self.tbSelectedSig.setColumnHidden(1, False)
        else:
            self.tbPossibleSig.setColumnHidden(0, False)
            self.tbPossibleSig.setColumnHidden(1, False)
            self.tbSelectedSig.setColumnHidden(0, False)
            self.tbSelectedSig.setColumnHidden(1, False)

        self.applyFiltersTSelected()
        self.applyFiltersTPossible()

    # Type radiobutton state changed -> type filters update
    def rbTypesClicked(self):
        if self.sender() == self.listRbTypes[0]:
            self.currTypeFilters = self.signalTypes.copy()
        else:
            self.currTypeFilters = [self.sender().text()]

        self.applyFiltersTPossible()
        self.applyFiltersTSelected()

    # Type checkbox state changed -> type filters update
    def chbTypesClicked(self):
        if self.sender().isChecked():
            self.currTypeFilters.append(self.sender().text())
            self.currTypeFilters.sort()
        else:
            self.currTypeFilters.remove(self.sender().text())

        self.applyFiltersTPossible()
        self.applyFiltersTSelected()

    # All and None selecting buttons for checkboxes
    def btnChbStateClicked(self):
        if self.sender() == self.btnChbSelectAll:
            for chb in self.listChbTypes:
                chb.setChecked(True)
            self.currTypeFilters = self.signalTypes.copy()

        elif self.sender() == self.btnChbSelectNone:
            for chb in self.listChbTypes:
                chb.setChecked(False)
            self.currTypeFilters = []

        self.applyFiltersTPossible()
        self.applyFiltersTSelected()

    # Applying current group and type filters state to data in table with possible signals
    def applyFiltersTPossible(self, filterGroup = None, filterType = None):
        row = 0

        if filterGroup == None:
            filterGroup = self.currGroupFilters
        if filterType == None:
            filterType = self.currTypeFilters

        self.tbPossibleSig.setRowCount(0)
        self.tbPossibleSig.clear()

        self.tbPossibleSig.setHorizontalHeaderLabels(['KKS', 'Тег', 'Наименование'])

        for group in filterGroup:
            for TYPE in filterType:
                if (group, TYPE) in self.sortHelper:
                    self.tbPossibleSig.setRowCount(self.tbPossibleSig.rowCount() + len(self.sortHelper[(group, TYPE)]))

                    for tag in self.sortHelper[(group, TYPE)]:
                        self.tbPossibleSig.setItem(row, 0, QTableWidgetItem(self.signals[tag]['KKS']))
                        self.tbPossibleSig.setItem(row, 1, QTableWidgetItem(tag))
                        self.tbPossibleSig.setItem(row, 2, QTableWidgetItem(self.signals[tag]['TEXT']))

                        if self.viewMode == 2:
                            self.tbPossibleSig.setRowHeight(row, 50)
                        else:
                            self.tbPossibleSig.setRowHeight(row, 35)

                        if self.signals[tag]['SELECTED']:
                            self.tbPossibleSig.item(row, 0).setBackground(self.colorSelected)
                            self.tbPossibleSig.item(row, 1).setBackground(self.colorSelected)
                            self.tbPossibleSig.item(row, 2).setBackground(self.colorSelected)
                        row += 1

    # Applying current group and type filters state to data in table with selected signals
    def applyFiltersTSelected(self, filterGroup = None, filterType = None):
        row = 0

        if filterGroup == None:
            filterGroup = self.currGroupFilters
        if filterType == None:
            filterType = self.currTypeFilters

        self.tbSelectedSig.setRowCount(0)
        self.tbSelectedSig.clear()

        self.tbSelectedSig.setHorizontalHeaderLabels(['KKS', 'Тег', 'Наименование'])

        for group in filterGroup:
            for TYPE in filterType:
                if (group, TYPE) in self.sortHelper:
                    for tag in self.sortHelper[(group, TYPE)]:
                        if tag in self.selectedSignals:
                            self.tbSelectedSig.setRowCount(self.tbSelectedSig.rowCount() + 1)

                            self.tbSelectedSig.setItem(row, 0, QTableWidgetItem(self.signals[tag]['KKS']))
                            self.tbSelectedSig.setItem(row, 1, QTableWidgetItem(tag))
                            self.tbSelectedSig.setItem(row, 2, QTableWidgetItem(self.signals[tag]['TEXT']))

                            if self.viewMode == 2:
                                self.tbSelectedSig.setRowHeight(row, 50)
                            else:
                                self.tbSelectedSig.setRowHeight(row, 35)

                            row += 1

    def btnConfigClicked(self):
        if self.sender() == self.btnExport:
            path = QFileDialog.getSaveFileName(self, 'Save configuration', 'configuration.txt', 'Text files (*.txt)')[0]

            if path == '':
                return

            try:
                with open(path, 'w') as fs:
                    for code in self.selectedSignals:
                        fs.write(code + '\n')
            except:
                QMessageBox.warning(None, 'Ошибка записи', 'Возникла ошибка при записи файла конфигурации.'
                                                           '\n[ {path} ]'.format( path=path),
                                    QMessageBox.Ok)
        else:
            path = QFileDialog.getOpenFileName(self, 'Save configuration', '', 'Text files (*.txt)')[0]

            if path == '':
                return

            self.selectedSignals.clear()

            missed = []

            with open(path, 'r') as fs:
                for tag in self.signals.keys():
                    self.signals[tag]['SELECTED'] = False

                for line in fs.readlines():
                    tag = line[:-1]

                    if tag in self.signals:
                        self.selectedSignals.append(tag)
                        self.signals[tag]['SELECTED'] = True
                    else:
                        missed.append(tag)

                if len(missed) > 0:
                    QMessageBox.warning(None, 'Ошибка добавления сигнала', 'В процессе импорта конфигурации '
                                        'возникла ошибка при добавлении сигнала '
                                        'в категорию \'Выбранное\'. Данный сигнал(ы) отсутствует(ют) в общем перечне '
                                        'сигналов \n{signals}'.format(signals=missed),
                                        QMessageBox.Ok)

                self.lblTotalSelected.setText('[{}]'.format(len(self.selectedSignals)))

                self.applyFiltersTSelected()
                self.applyFiltersTPossible()

    def btnSavePathClicked(self):
        if self.sender() == self.btnSelectNamesSP:
            path = QFileDialog.getSaveFileName(self,
                                               'Names saving path',
                                               'names_{}.csv'.format(datetime.now().strftime('%d-%m-%Y_%H-%M')))[0]
            if path != ('', ''):
                self.leNamesPath.setText(path)
        else:
            path = QFileDialog.getSaveFileName(self,
                                               'Data saving path',
                                               'data_{}.csv'.format(datetime.now().strftime('%d-%m-%Y_%H-%M')))[0]
            if path != ('', ''):
                self.leDataPath.setText(path)

    def setBeginEndTime(self, timeBeginEnd):
        self.dteBeginTime.setDateTime(timeBeginEnd[0])
        self.dteEndTime.setDateTime(timeBeginEnd[1])

    def btnDoClicked(self):
        self.jobDone = True
        self.signalDo.emit()
        self.jobDone = False

    def closeEvent(self, event):
        if not self.jobDone:
            self.errCode = -1

        self.signalDo.emit()

        super(SelectorWindow, self).closeEvent(event)

    def getData(self):
        return ((self.leNamesPath.text(), self.leDataPath.text()),
                self.selectedSignals,
                (datetime.combine(self.dteBeginDate.dateTime().toPyDateTime().date(),
                                  self.dteBeginTime.dateTime().toPyDateTime().time()),
                 datetime.combine(self.dteEndDate.dateTime().toPyDateTime().date(),
                                  self.dteEndTime.dateTime().toPyDateTime().time())))

    def checkErr(self):
        return self.errCode
