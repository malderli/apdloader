from PyQt5.Qt import QAbstractTableModel, QModelIndex, QVariant, QColor
from PyQt5.Qt import Qt
import typing

KKSCOL = 0
TAGCOL = 1
TEXTCOL = 2
TYPECOL = 3
GROUPCOL = 4

class ModelSignals(QAbstractTableModel):
    def __init__(self):
        super(ModelSignals, self).__init__()

        self.colorSelected = QColor('#8DDF8D')
        self.baseData = None

    def setBaseData(self, data):
        self.baseData = data

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.baseData)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 5

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return QVariant()

        if self.baseData is None:
            return QVariant()

        if role == Qt.DisplayRole:
            if index.column() == KKSCOL:
                return self.baseData[index.row()]['KKS']
            elif index.column() == TAGCOL:
                return self.baseData[index.row()]['TAG']
            elif index.column() == TEXTCOL:
                return self.baseData[index.row()]['TEXT']
            elif index.column() == TYPECOL:
                return self.baseData[index.row()]['TYPE']
            elif index.column() == GROUPCOL:
                return self.baseData[index.row()]['GROUP']
            else:
                return QVariant()

        elif role == Qt.BackgroundColorRole:
            if self.baseData[index.row()]['SELECTED']:
                return self.colorSelected
            else:
                return QVariant()

        elif role == Qt.ToolTipRole:
            if index.column() == TEXTCOL:
                return self.baseData[index.row()]['TEXT']
            else:
                return QVariant()

        else:
            return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return QVariant()

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | (not Qt.ItemIsEditable)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        headers = { KKSCOL: 'KKS', TAGCOL: 'Тег', TEXTCOL: 'Наименование', TYPECOL: 'Тип', GROUPCOL: 'Группа' }

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section in headers:
                    return headers[section]
                else:
                    return QVariant()
            # if role == QHeaderView.

        if orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                return section + 1

        return QVariant()
