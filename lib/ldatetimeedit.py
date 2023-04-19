from PyQt5.QtWidgets import QDateTimeEdit, QCalendarWidget, QLabel, QComboBox, QPushButton, QFrame
from PyQt5.Qt import QGridLayout, QHBoxLayout, QRect
from datetime import datetime


class LDateTimeEdit(QDateTimeEdit):
    def __init__(self):
        super(QDateTimeEdit, self).__init__()

        self.dateTimeChanged.connect(self._dtChanged)

        self.cw = QCalendarWidget()
        self.cw.setGridVisible(True)

        self.cbHours = QComboBox()
        self.cbHours.addItems(('0' + str(hour) if hour < 10 else str(hour)) for hour in range(24))
        self.cbHours.currentTextChanged.connect(self._cbHoursChanged)

        self.cbMinutes = QComboBox()
        self.cbMinutes.addItems(('0' + str(minute) if minute < 10 else str(minute)) for minute in range(60))
        self.cbMinutes.currentTextChanged.connect(self._cbMinutesChanged)

        self.lytSub = QHBoxLayout()
        self.lytSub.addWidget(QLabel('ВРЕМЯ:'))
        self.lytSub.addWidget(self.cbHours)
        self.lytSub.addWidget(self.cbMinutes)
        self.lytSub.setContentsMargins(5, 5, 5, 5)
        self.lytSub.setSpacing(5)

        frm = QFrame()
        frm.setFrameShape(QFrame.StyledPanel)
        frm.setLayout(self.lytSub)

        self.cw.layout().insertWidget(0, frm, 1)

        rect = self.cw.layout().itemAt(2).geometry()
        rect.setHeight(rect.height() + 100)

        self.cw.setMinimumHeight(250)
        self.cw.setMinimumWidth(250)
        self.cw.setGeometry(QRect(0, 0, 1000, 1000))

        self.setCalendarPopup(True)
        self.setCalendarWidget(self.cw)

        # rect = self.cw.layout().itemAt(2).geometry()
        # rect.setHeight(rect.height() + self.lytSub.geometry().height())

        # self.cw.setGeometry(rect.height() - self.lytSub.geometry().height())
        # self.cw.layout().itemAt(0).setGeometry(self.cw.layout().geometry())

    def _cbHoursChanged(self, text):
        self.setDateTime(self.dateTime().toPyDateTime().replace(hour=int(text)))

    def _cbMinutesChanged(self, text):
        self.setDateTime(self.dateTime().toPyDateTime().replace(minute=int(text)))

    def _dtChanged(self):
        self.cbHours.currentTextChanged.disconnect(self._cbHoursChanged)
        self.cbMinutes.currentTextChanged.disconnect(self._cbMinutesChanged)

        self.cbHours.setCurrentIndex(self.time().hour())
        self.cbMinutes.setCurrentIndex(self.time().minute())

        self.cbHours.currentTextChanged.connect(self._cbHoursChanged)
        self.cbMinutes.currentTextChanged.connect(self._cbMinutesChanged)
