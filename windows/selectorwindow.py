import PyQt5.Qt

from PyQt5.QtWidgets import QLabel, QPushButton, QGroupBox, QLineEdit, QRadioButton, QDateTimeEdit, \
    QTableView, QFrame, QTabWidget, QCheckBox, QSpacerItem, QHeaderView, QFileDialog, \
    QMessageBox, QGridLayout, QVBoxLayout, QWidget, QCalendarWidget, QComboBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import Qt
from datetime import datetime

from enum import Enum

from lib.modelsignals import ModelSignals
from lib.modelpossiblefilter import ModelPossibleFilter
from lib.modelselectedfilter import ModelSelectedFilter

from lib.ldatetimeedit import LDateTimeEdit


class Filters(Enum):
    fdefault = 0
    ftypes = 1
    fgroups = 2
    fstring = 3


class SelectorWindow(QWidget):
    signalStartUploading = pyqtSignal()
    signalImport = pyqtSignal()
    signalExport = pyqtSignal()

    signalClose = pyqtSignal()

    def __init__(self, title='None'):
        super(QWidget, self).__init__()

        self.selectedCounter = 0

        self.signals = None
        self.filteringMode = []
        self.columnsMode = []

        self.listRbGroups = []
        self.listRbTypes = []
        self.listChbTypes = []

        self.errCode = 0

        self.modelSelected = None
        self.modelPossible = None
        self.modelFilter = None

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Signals

        # ------------------------------------------------- Signals group box

        self.tbPossibleSig = QTableView()
        self.tbPossibleSig.setSortingEnabled(True)
        self.tbPossibleSig.setMaximumHeight(3000)
        self.tbPossibleSig.setAlternatingRowColors(True)
        self.tbPossibleSig.setWordWrap(True)
        self.tbPossibleSig.doubleClicked.connect(self._tbPossibleSigDoubleClicked)
        self.tbPossibleSig.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        self.tbSelectedSig = QTableView()
        self.tbSelectedSig.setSortingEnabled(True)
        self.tbSelectedSig.setMaximumHeight(3000)
        self.tbSelectedSig.setAlternatingRowColors(True)
        self.tbSelectedSig.setWordWrap(True)
        self.tbSelectedSig.doubleClicked.connect(self._tbSelectedSigDoubleClicked)
        self.tbSelectedSig.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        # -------------------------------------------------

        # ------------------------------------------------- Groups filters

        self.gbGroups = QGroupBox()
        self.gbGroups.setTitle('Технологическая группа')

        self.lytGroups = QGridLayout()
        self.lytGroups.setContentsMargins(6, 6, 6, 6)
        self.gbGroups.setLayout(self.lytGroups)

        frm = QFrame()
        frm.setFrameShape(QFrame.HLine)
        frm.setFrameShadow(QFrame.Sunken)

        # -------------------------------------------------

        # +++++++++++++++++++++++++++++++++++++++++++++++++ Types filters

        self.tabwTypes = QTabWidget()
        self.tabwTypes.setSizePolicy(PyQt5.Qt.QSizePolicy.Minimum, PyQt5.Qt.QSizePolicy.Minimum)
        self.tabwTypes.currentChanged.connect(self._tabTypesChanged)

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
        self.btnChbSelectAll.clicked.connect(self._btnChbSelectAllClicked)

        self.btnChbSelectNone = QPushButton('Сброс')
        self.btnChbSelectNone.clicked.connect(self._btnChbSelectNoneClicked)

        frmH = QFrame()
        frmH.setFrameShape(QFrame.HLine)
        frmH.setFrameShadow(QFrame.Sunken)

        self.lytTypesChb = QGridLayout()
        self.lytTypesChb.addWidget(self.btnChbSelectAll, 0, 0, 1, 2)
        self.lytTypesChb.addWidget(self.btnChbSelectNone, 1, 0, 1, 2)
        self.lytTypesChb.addWidget(frmH, 2, 0, 1, 2)
        self.wgtTypesChb.setLayout(self.lytTypesChb)

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
            self.listRbColumnsModes[row].clicked.connect(self._rbColumnsClicked)
            self.lytColumnsMode.addWidget(self.listRbColumnsModes[row], row, 0)

        self.gbColumnsMode.setLayout(self.lytColumnsMode)

        # -------------------------------------------------

        # ------------------------------------------------- Filters apply mode selection

        self.gbFiltersMode = QGroupBox('Фильтровать')

        self.listRbFiltersMode = [QRadioButton('Все'), QRadioButton('Доступные')]
        self.listRbFiltersMode[0].setChecked(True)

        self.lytFiltersMode = QGridLayout()

        for row, rb in enumerate(self.listRbFiltersMode):
            self.listRbFiltersMode[row].clicked.connect(self._rbFilterModesClicked)
            self.lytFiltersMode.addWidget(self.listRbFiltersMode[row], row, 0)

        self.gbFiltersMode.setLayout(self.lytFiltersMode)

        # -------------------------------------------------

        # ------------------------------------------------- Config import/export

        self.gbConfig = QGroupBox('Конфигурация')

        self.btnImport = QPushButton('Импорт')
        self.btnImport.clicked.connect(self._btnImportClicked)
        self.btnExport = QPushButton('Экспорт')
        self.btnExport.clicked.connect(self._btnExportClicked)

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

        self.btnAddSelected.clicked.connect(self._btnsMoveClicked)
        self.btnAddAll.clicked.connect(self._btnsMoveClicked)
        self.btnRemAll.clicked.connect(self._btnsMoveClicked)
        self.btnRemSelected.clicked.connect(self._btnsMoveClicked)

        self.lytMoveButtons = QVBoxLayout()
        self.lytMoveButtons.addWidget(self.btnAddSelected, 0)
        self.lytMoveButtons.addWidget(self.btnAddAll, 1)
        self.lytMoveButtons.addWidget(self.btnRemAll, 2)
        self.lytMoveButtons.addWidget(self.btnRemSelected, 3)

        # -------------------------------------------------

        self.lblTotalPossible = QLabel('[0/0]')
        self.lblTotalSelected = QLabel('[0/0]')

        # Filters fields
        self.leFiltersPos = QLineEdit()
        self.leFiltersPos.setClearButtonEnabled(True)
        self.leFiltersPos.setPlaceholderText('Введите фильтр...')
        self.leFiltersPos.textChanged.connect(self._leFiltersPosTextChanged)

        self.leFiltersSel = QLineEdit()
        self.leFiltersSel.setClearButtonEnabled(True)
        self.leFiltersSel.setPlaceholderText('Введите фильтр...')
        self.leFiltersSel.textChanged.connect(self._leFiltersSelTextChanged)

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

        #self.lytSignals.addWidget(QLabel('Технологическая группа:'), 0, 0, 1, 5)
        self.lytSignals.addWidget(self.gbGroups, 1, 0, 1, 5)
        #self.lytSignals.addWidget(frmH, 2, 0, 1, 5)

        self.lytSignals.addLayout(self.lytRight, 4, 6, 4, 1)
        self.lytSignals.addWidget(frmV, 4, 5, 4, 1)

        self.lytSignals.addWidget(self.leFiltersPos, 7, 0, 1, 2)
        self.lytSignals.addWidget(self.leFiltersSel, 7, 3, 1, 2)

        self.gbSignals.setLayout(self.lytSignals)

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        # ------------------------------------------------- Time

        self.gbTime = QGroupBox('Интервал выгрузки')
        self.layoutTime = QGridLayout()


        self.dteBegin = LDateTimeEdit()
        self.dteBegin.setMinimumWidth(140)
        self.dteBegin.setDateTime(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        self.dteBegin.setDisplayFormat('dd/MM/yyyy hh:mm')

        self.dteEnd = LDateTimeEdit()
        self.dteEnd.setMinimumWidth(140)
        self.dteEnd.setDateTime(datetime.now().replace(hour=23, minute=59, second=59, microsecond=0))
        self.dteEnd.setDisplayFormat('dd/MM/yyyy hh:mm')

        self.layoutTime.addWidget(QLabel('От:'), 0, 0)
        self.layoutTime.addWidget(self.dteBegin, 0, 1)

        self.layoutTime.addWidget(QLabel('До:'), 0, 2)
        self.layoutTime.addWidget(self.dteEnd, 0, 3)

        self.gbTime.setLayout(self.layoutTime)
        self.gbTime.setSizePolicy(PyQt5.Qt.QSizePolicy.Minimum, PyQt5.Qt.QSizePolicy.Minimum)

        # -------------------------------------------------

        # ------------------------------------------------- File path

        self.gbFolder = QGroupBox('Директория сохранения')

        self.btnSelectSaveDir = QPushButton('Выбрать')
        self.btnSelectSaveDir.clicked.connect(self._btnSelectSaveDirClicked)
        self.leSavePath = QLineEdit()

        self.lytFolder = QGridLayout()
        self.lytFolder.setColumnStretch(0, 1)
        self.lytFolder.addWidget(self.leSavePath, 0, 0)
        self.lytFolder.addWidget(self.btnSelectSaveDir, 0, 1)

        self.gbFolder.setLayout(self.lytFolder)

        # -------------------------------------------------

        # ------------------------------------------------- Main window

        self.setWindowTitle(title)

        self.btnStartUploading = QPushButton('Выполнить выгрузку')
        self.btnStartUploading.clicked.connect(self.signalStartUploading.emit)

        self.lblUploadStatus = QLabel('Начало выгрузки...')
        self.lblUploadStatus.hide()

        self.layoutMain = QGridLayout()
        self.layoutMain.addWidget(self.gbSignals, 0, 0, 1, 2)
        self.layoutMain.addWidget(self.gbFolder, 1, 1)
        self.layoutMain.addWidget(self.gbTime, 1, 0)
        self.layoutMain.addWidget(self.btnStartUploading, 3, 0, 1, 2)
        self.layoutMain.addWidget(self.lblUploadStatus, 4, 0, 1, 2)
        self.setLayout(self.layoutMain)

        self.setGeometry(100, 100, 700, 100)

        # -------------------------------------------------


    # +++++++++++++++++++++++++++++++++++++++ Public functions

    def setSignalsList(self, signals):
        self.signals = signals.copy()

        for signal in self.signals:
            signal['SELECTED'] = False

        self.modelPossible = ModelSignals()
        self.modelPossible.setBaseData(self.signals)

        self.modelFilterPossible = ModelPossibleFilter()
        self.modelFilterPossible.setSourceModel(self.modelPossible)
        self.tbPossibleSig.setModel(self.modelFilterPossible)

        self.modelFilterSelected = ModelSelectedFilter()
        self.modelFilterSelected.setSourceModel(self.modelPossible)
        self.tbSelectedSig.setModel(self.modelFilterSelected)

        # Content resizing
        self.tbPossibleSig.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbPossibleSig.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbPossibleSig.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tbPossibleSig.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tbPossibleSig.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.tbPossibleSig.setColumnHidden(1, True)
        self.tbPossibleSig.setColumnHidden(3, True)
        self.tbPossibleSig.setColumnHidden(4, True)

        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.tbSelectedSig.setColumnHidden(1, True)
        self.tbSelectedSig.setColumnHidden(3, True)
        self.tbSelectedSig.setColumnHidden(4, True)

        self._updateCounters()

    def setGroupsList(self, groups):
        self.listRbGroups.clear()

        for pos, group in enumerate(['Все'] + groups):
            self.listRbGroups.append(QRadioButton(group))
            self.listRbGroups[-1].clicked.connect(self._rbGroupsClicked)
            self.lytGroups.addWidget(self.listRbGroups[-1], 0, pos)

        self.listRbGroups[0].setChecked(True)

        self.lytGroups.addItem(QSpacerItem(1, 1, PyQt5.Qt.QSizePolicy.Expanding,
                                              PyQt5.Qt.QSizePolicy.Minimum), 0, len(groups) + 1)

    def setTypesList(self, sigtypes):
        for pos, sigtype in enumerate(['Все'] + sigtypes):
            # RadioButtons
            self.listRbTypes.append(QRadioButton(sigtype))
            self.listRbTypes[-1].clicked.connect(self._rbTypesClicked)

            if pos == 0:
                self.lytTypesRb.addWidget(self.listRbTypes[-1], pos, 0)
            else:
                self.lytTypesRb.addWidget(self.listRbTypes[-1],
                                             2 + (pos - 1) % ((len(sigtypes) + 1) // 2),
                                             (pos - 1) // ((len(sigtypes) + 1) // 2))

            self.listRbTypes[0].setChecked(True)

            # CheckBoxes
            if pos == 0:
                # Skip 'all' for checkboxes
                continue

            self.listChbTypes.append(QCheckBox(sigtype))
            self.listChbTypes[-1].clicked.connect(self._chbTypesClicked)
            self.listChbTypes[-1].setChecked(True)

            self.lytTypesChb.addWidget(self.listChbTypes[-1],
                                       3 + (pos - 1) % ((len(sigtypes) + 1) // 2),
                                       (pos - 1) // ((len(sigtypes) + 1) // 2))

    def setBeginEndTime(self):
        pass

    def toggleUploadMode(self, state):
        if state:
            self.btnStartUploading.hide()
            self.lblUploadStatus.show()
        else:
            self.btnStartUploading.show()
            self.lblUploadStatus.hide()

    def setUploadState(self, text):
        self.lblUploadStatus.setText(text)

    def setVisualConfig(self, config):
        self.myFont = QFont(config['font'], config['fontsize'])
        self.setFont(self.myFont)

        # No idea
        self.tbPossibleSig.horizontalHeader().setFont(self.font())

        self.leFiltersPos.setStyleSheet("color: " + config['searchtextcolor'])
        self.leFiltersSel.setStyleSheet("color: " + config['searchtextcolor'])

    def getUploadingData(self):
        selectedSignals = [signal['TAG'] for signal in self.signals if signal['SELECTED'] == True]

        return (self.leSavePath.text(),
                selectedSignals,
                (self.dteBegin.dateTime().toPyDateTime(), self.dteEnd.dateTime().toPyDateTime()))

    # +++++++++++++++++++++++++++++++++++++++ Private functions

    def _updateByFilters(self, toupdate = Filters.fdefault):
        if (toupdate == Filters.fgroups) or (toupdate == Filters.fdefault):
            filtersGroups = None

            if not len(self.listRbGroups):
                return

            if not self.listRbGroups[0].isChecked():
                filtersGroups = tuple([rb.text() for rb in self.listRbGroups if rb.isChecked()])

            self.modelFilterPossible.setAcceptedGroups(filtersGroups)
            self.modelFilterSelected.setAcceptedGroups(filtersGroups)

        if (toupdate == Filters.ftypes) or (toupdate == Filters.fdefault):
            filtersTypes = None

            if self.tabwTypes.currentWidget() is self.wgtTypesRb:
                if not len(self.listRbTypes):
                    return

                if not self.listRbTypes[0].isChecked():
                    filtersTypes = tuple([rb.text() for rb in self.listRbTypes if rb.isChecked()])

            elif self.tabwTypes.currentWidget() is self.wgtTypesChb:
                if not len(self.listChbTypes):
                    return

                filtersTypes = tuple([chb.text() for chb in self.listChbTypes if chb.isChecked()])

            else:
                return

            self.modelFilterPossible.setAcceptedTypes(filtersTypes)
            self.modelFilterSelected.setAcceptedTypes(filtersTypes)

        if (toupdate == Filters.fstring) or (toupdate == Filters.fdefault):
            pass

        # TODO: not proper way to redraw
        self.modelFilterPossible.setFilterRegExp("")
        self.modelFilterSelected.setFilterRegExp("")



        self.tbPossibleSig.scrollToTop()
        self.tbSelectedSig.scrollToTop()


        self._updateCounters()

    def _updateCounters(self):
        self.lblTotalPossible.setText('[{}/{}]'.format(self.modelFilterPossible.rowCount(), len(self.signals)))
        self.lblTotalSelected.setText('[{}/{}]'.format(self.modelFilterSelected.rowCount(), self.selectedCounter))

    def _setFilterSelected(self, state: bool):
        self.modelFilterSelected.setEnableGroupTypeFilters(state)

        # TODO: not proper way to redraw
        self.modelFilterSelected.setFilterRegExp("")

        self._updateCounters()

    def _selectSignal(self, row):
        pass

    def _unselectSignal(self, row):
        pass

    def _importConfig(self):
        path = QFileDialog.getOpenFileName(self, 'Save configuration', '', 'Text files (*.txt)')[0]

        if path == '':
            return

        self.selectedCounter = 0

        try:
            with open(path, 'r') as fs:
                tofind = fs.readlines()

                for i in range(len(tofind)):
                    tofind[i] = tofind[i].replace('\n', '')

                for signal in self.signals:
                    if signal['KKS'] in tofind:
                        signal['SELECTED'] = True
                        self.selectedCounter += 1
                        tofind.remove(signal['KKS'])
                    else:
                        signal['SELECTED'] = False

                if len(tofind) > 0:
                    QMessageBox.warning(None, 'Ошибка добавления сигнала', 'В процессе импорта конфигурации '
                                                                           'возникла ошибка при добавлении сигнала '
                                                                           'в категорию \'Выбранное\'. Данный сигнал(ы) отсутствует(ют) в общем перечне '
                                                                           'сигналов \n{signals}'.format(
                        signals=tofind),
                                        QMessageBox.Ok)
        except:
            QMessageBox.warning(None, 'Ошибка чтения', 'Возникла ошибка при чтении файла конфигурации.'
                                                       '\n[ {path} ]'.format(path=path),
                                QMessageBox.Ok)

        # TODO: not proper way to redraw
        self.modelFilterPossible.setFilterRegExp("")
        self.modelFilterSelected.setFilterRegExp("")

        self._updateByFilters()

    def _exportConfig(self):
        path = QFileDialog.getSaveFileName(self, 'Save configuration', 'configuration.txt', 'Text files (*.txt)')[0]

        if path == '':
            return

        try:
            with open(path, 'w') as fs:
                for signal in self.signals:
                    if signal['SELECTED']:
                        fs.write(signal['KKS'] + '\n')
        except:
            QMessageBox.warning(None, 'Ошибка записи', 'Возникла ошибка при записи файла конфигурации.'
                                                       '\n[ {path} ]'.format(path=path),
                                QMessageBox.Ok)

    # +++++++++++++++++++++++++++++++++++++++ RadioButtons and CheckBoxes events

    def _rbGroupsClicked(self):
        self._updateByFilters(Filters.fgroups)

    def _rbTypesClicked(self):
        self._updateByFilters(Filters.ftypes)

    def _chbTypesClicked(self):
        self._updateByFilters(Filters.ftypes)

    def _rbColumnsClicked(self):
        if self.sender() == self.listRbColumnsModes[0]:
            self.tbPossibleSig.setColumnHidden(0, False)
            self.tbPossibleSig.setColumnHidden(1, True)
            self.tbPossibleSig.setColumnHidden(2, False)

            self.tbSelectedSig.setColumnHidden(0, False)
            self.tbSelectedSig.setColumnHidden(1, True)
            self.tbSelectedSig.setColumnHidden(2, False)

        elif self.sender() == self.listRbColumnsModes[1]:
            self.tbPossibleSig.setColumnHidden(0, True)
            self.tbPossibleSig.setColumnHidden(1, False)
            self.tbPossibleSig.setColumnHidden(2, False)

            self.tbSelectedSig.setColumnHidden(0, True)
            self.tbSelectedSig.setColumnHidden(1, False)
            self.tbSelectedSig.setColumnHidden(2, False)

        elif self.sender() == self.listRbColumnsModes[2]:
            self.tbPossibleSig.setColumnHidden(0, False)
            self.tbPossibleSig.setColumnHidden(1, False)
            self.tbPossibleSig.setColumnHidden(2, False)

            self.tbSelectedSig.setColumnHidden(0, False)
            self.tbSelectedSig.setColumnHidden(1, False)
            self.tbSelectedSig.setColumnHidden(2, False)

    def _rbFilterModesClicked(self):
        if self.sender() is self.listRbFiltersMode[0]:
            self._setFilterSelected(True)
        else:
            self._setFilterSelected(False)

    # +++++++++++++++++++++++++++++++++++++++ Buttons events

    def _btnImportClicked(self):
        self._importConfig()

    def _btnExportClicked(self):
        self._exportConfig()

    def _btnSelectSaveDirClicked(self):
        path = QFileDialog.getSaveFileName(self,
                                           'Saving path',
                                           'data_{}.h5'.format(datetime.now().strftime('%d-%m-%Y_%H-%M')))[0]

        if path != ('', ''):
            self.leSavePath.setText(path)

    def _btnsMoveClicked(self):
        if self.sender() == self.btnAddSelected:
            for index in self.tbPossibleSig.selectedIndexes():
                mappedindex = self.modelFilterPossible.mapToSource(index)
                if not self.signals[mappedindex.row()]['SELECTED']:
                    self.signals[mappedindex.row()]['SELECTED'] = True
                    self.selectedCounter += 1

        elif self.sender() == self.btnAddAll:
            for row in range(self.modelFilterPossible.rowCount()):
                mappedindex = self.modelFilterPossible.mapToSource(self.modelFilterPossible.index(row, 0))
                if not self.signals[mappedindex.row()]['SELECTED']:
                    self.signals[mappedindex.row()]['SELECTED'] = True
                    self.selectedCounter += 1

        elif self.sender() == self.btnRemSelected:
            for index in self.tbSelectedSig.selectedIndexes():
                mappedindex = self.modelFilterSelected.mapToSource(index)
                if self.signals[mappedindex.row()]['SELECTED']:
                    self.signals[mappedindex.row()]['SELECTED'] = False
                    self.selectedCounter -= 1

        elif self.sender() == self.btnRemAll:
            for row in range(self.modelFilterSelected.rowCount()):
                mappedindex = self.modelFilterSelected.mapToSource(self.modelFilterSelected.index(row, 0))
                if self.signals[mappedindex.row()]['SELECTED']:
                    self.signals[mappedindex.row()]['SELECTED'] = False
                    self.selectedCounter -= 1

        self.modelFilterPossible.setFilterRegExp("")
        self.modelFilterSelected.setFilterRegExp("")

        # TODO: mby not proper way to update selection :)
        self.tbPossibleSig.selectAll()
        self.tbPossibleSig.clearSelection()
        self.tbSelectedSig.clearSelection()
        self._updateCounters()

    def _btnChbSelectAllClicked(self):
        for chb in self.listChbTypes:
            chb.setChecked(True)

        self._updateByFilters(Filters.ftypes)

    def _btnChbSelectNoneClicked(self):
        for chb in self.listChbTypes:
            chb.setChecked(False)

        self._updateByFilters(Filters.ftypes)

    def _btnStartUploadingClicked(self):
        pass

    # +++++++++++++++++++++++++++++++++++++++ Other events

    def _tbPossibleSigDoubleClicked(self):
        indexes = self.tbPossibleSig.selectedIndexes()

        if not len(indexes):
            return

        mappedindex = self.modelFilterPossible.mapToSource(indexes[0])

        self.signals[mappedindex.row()]['SELECTED'] = not self.signals[mappedindex.row()]['SELECTED']

        if self.signals[mappedindex.row()]['SELECTED']:
            self.selectedCounter += 1
        else:
            self.selectedCounter -= 1

        self.tbPossibleSig.clearSelection()
        # self.tbPossibleSig.horizontalHeader().setFont(self.font())
        self.modelPossible.dataChanged.emit(mappedindex, mappedindex)

        self.tbSelectedSig.resizeColumnsToContents()
        self.tbSelectedSig.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self._updateCounters()

    def _tbSelectedSigDoubleClicked(self):
        indexes = self.tbSelectedSig.selectedIndexes()

        if not len(indexes):
            return

        mappedindex_begin = self.modelFilterSelected.mapToSource(indexes[0])
        mappedindex_end = self.modelFilterSelected.mapToSource(indexes[-1])

        self.signals[mappedindex_begin.row()]['SELECTED'] = not self.signals[mappedindex_begin.row()]['SELECTED']

        if self.signals[mappedindex_begin.row()]['SELECTED']:
            self.selectedCounter += 1
        else:
            self.selectedCounter -= 1

        self.tbPossibleSig.clearSelection()
        self.modelPossible.dataChanged.emit(mappedindex_begin, mappedindex_end)

        self._updateCounters()

    def _leFiltersPosTextChanged(self):
        self.modelFilterPossible.setFilteringString(self.leFiltersPos.text())
        self.modelFilterPossible.setFilterRegExp("")
        self._updateCounters()

    def _leFiltersSelTextChanged(self):
        self.modelFilterSelected.setFilteringString(self.leFiltersSel.text())
        self.modelFilterSelected.setFilterRegExp("")
        self._updateCounters()

    def _tabTypesChanged(self):
        self._updateByFilters(Filters.ftypes)

    def throwMessageBox(self, title, text):
        QMessageBox.warning(None, title, text, QMessageBox.Ok)

    def closeEvent(self, event):
        super(SelectorWindow, self).closeEvent(event)
        self.signalClose.emit()
