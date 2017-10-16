import pandas as pd
from openpyxl import load_workbook
from itertools import islice
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel

class Excel:

    '''
    Pandas と Openpyxl をつかい、エクセルファイルの読み込み/書き出しを行うクラスです。
    '''

    def open(self, file_name):

        # 特定のシートの書き込む方法は下記を参照。
        # https://stackoverflow.com/a/20221655

        px_workbook = load_workbook(file_name)
        writer = pd.ExcelWriter(file_name, engine='openpyxl')
        writer.book = px_workbook
        writer.sheets = dict((ws.title, ws) for ws in px_workbook.worksheets)

        self.px_workbook = px_workbook
        self.writer = writer

    def get_dataframe(self, name):
        return convert_openpyxl_to_pandas(self.px_workbook.get_sheet_by_name(name))

    def set_dataframe(self, dataframe, name):
        dataframe.to_excel(self.writer, name)

    def save(self):
        self.writer.save()

def convert_openpyxl_to_pandas(ws):
    '''
    openpyxl の worksheet を、pandas の dataframe に変換します。

    https://openpyxl.readthedocs.io/en/default/pandas.html
    のコピペです。
    '''
    data = ws.values
    cols = next(data)[1:]
    data = list(data)
    idx = [r[0] for r in data]
    data = (islice(r, 1, None) for r in data)
    df = pd.DataFrame(data, index=idx, columns=cols)
    return df

def convert_openpyxl_to_qtmodel(px_worksheet):
    '''
    openpyxl の worksheet を、Qt のモデルに変換します。
    '''
    qt_model = QStandardItemModel()

    rows = px_worksheet.rows

    for row_index, cells in enumerate(rows):
        for column_index, cell in enumerate(cells):
            # cell は openpyxl の worksheet のセル
            # cell.valueはそのセルの値を格納
            # cell を qt の model の item に変換
            # (qt の model の item = エクセルで言うところのセル)
            qt_item = QStandardItem()
            qt_item.setData(cell.value)
            #import pdb;pdb.set_trace()
            qt_model.setItem(row_index, column_index, qt_item)

    return qt_model

class DataframeAsModel(QAbstractItemModel):
    def __init__(self, parent=None):
        '''
        Parameters:
        dataframe -- Pandas の dataframe
        '''
        super().__init__(parent)
        self.dataframe = pd.DataFrame()

    def append(self, rows):
        number_of_rows_inserted = len(rows.index)
        number_of_existent_rows = self.rowCount()
        self.beginInsertRows(
            QModelIndex(),
            number_of_existent_rows,
            number_of_existent_rows + number_of_rows_inserted
        )
        self.dataframe = self.dataframe.append(rows)
        self.endInsertRows()

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, None)

    def parent(self, child):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return len(self.dataframe.index)

    def columnCount(self, parent=QModelIndex()):
        return 3#len(self.dataframe.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            try:
                df = self.dataframe
                rows = df.index
                columns = df.columns
                res = df.get_value(rows[index.row()], columns[index.column()])

                return str(res)

            except:
                return
        return

class Items:
    def __init__(self, dataframe):
        self.dataframe = dataframe
    
    def get_item_by_id(self, id):
        return self.dataframe[self.dataframe.index == id]
