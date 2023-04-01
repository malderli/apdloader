from PyQt5.Qt import QAbstractTableModel, QModelIndex, QVariant, QHeaderView, QSortFilterProxyModel
from PyQt5.Qt import Qt
import typing

KKSCOL = 0
TAGCOL = 1
TEXTCOL = 2
TYPECOL = 3
GROUPCOL = 4

class ModelFilter(QSortFilterProxyModel):

    def __init__(self):
        super(ModelFilter, self).__init__()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)

        if self.sourceModel().baseData[index.row()]['TAG'].find('AT') == 0:
            return True
        else:
            return False

        # return True

    # def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
    #     pass
