from PyQt5.Qt import QAbstractTableModel, QModelIndex, QVariant, QHeaderView, QSortFilterProxyModel
from PyQt5.Qt import Qt
import typing

KKSCOL = 0
TAGCOL = 1
TEXTCOL = 2
TYPECOL = 3
GROUPCOL = 4

class ModelSelectedFilter(QSortFilterProxyModel):

    def __init__(self):
        super(ModelSelectedFilter, self).__init__()

        self.enableGroupTypeFilters = True

        self.acceptedGroups = None
        self.acceptedTypes = None
        self.filteringString = None

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)

        if not index.isValid():
            return QVariant()

        if not self.sourceModel().baseData[index.row()]['SELECTED']:
            return False

        if (self.acceptedTypes is not None) and \
                (self.sourceModel().baseData[index.row()]['TYPE'] not in self.acceptedTypes) and \
                self.enableGroupTypeFilters:
            return False

        if (self.acceptedGroups is not None) and \
                (self.sourceModel().baseData[index.row()]['GROUP'] not in self.acceptedGroups) and \
                self.enableGroupTypeFilters:
            return False

        if (self.filteringString is not None) and \
            (self.sourceModel().baseData[index.row()]['TEXT'].upper().find(self.filteringString) == -1) and \
            (self.sourceModel().baseData[index.row()]['KKS'].upper().find(self.filteringString) == -1) and \
            (self.sourceModel().baseData[index.row()]['TAG'].upper().find(self.filteringString) == -1):
            return False

        return True

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return QVariant()

        mappedindex = self.mapToSource(index)

        if role == Qt.BackgroundColorRole:
            return QVariant()

        else:
            return self.sourceModel().data(mappedindex, role)

    def setEnableGroupTypeFilters(self, state):
        self.enableGroupTypeFilters = state

    def setAcceptedGroups(self, groups):
        self.acceptedGroups = groups

    def setAcceptedTypes(self, types):
        self.acceptedTypes = types

    def setFilteringString(self, filter):
        self.filteringString = filter.upper()
