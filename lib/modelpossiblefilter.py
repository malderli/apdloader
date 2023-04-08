from PyQt5.Qt import QAbstractTableModel, QModelIndex, QVariant, QHeaderView, QSortFilterProxyModel
from PyQt5.Qt import Qt
import typing

KKSCOL = 0
TAGCOL = 1
TEXTCOL = 2
TYPECOL = 3
GROUPCOL = 4

class ModelPossibleFilter(QSortFilterProxyModel):

    def __init__(self):
        super(ModelPossibleFilter, self).__init__()

        self.acceptedGroups = None
        self.acceptedTypes = None
        self.filteringString = None

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)

        if (self.acceptedTypes is not None) and \
                (self.sourceModel().baseData[index.row()]['TYPE'] not in self.acceptedTypes):
            return False

        if (self.acceptedGroups is not None) and \
                (self.sourceModel().baseData[index.row()]['GROUP'] not in self.acceptedGroups):
            return False

        return True

    def setAcceptedGroups(self, groups):
        self.acceptedGroups = groups

    def setAcceptedTypes(self, types):
        self.acceptedTypes = types

    def setFilteringString(self, filter):
        pass

