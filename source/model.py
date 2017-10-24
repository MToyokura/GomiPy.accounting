import pandas as pd
from openpyxl import load_workbook
from itertools import islice
from PyQt5.QtCore import QAbstractItemModel,  QAbstractProxyModel, QModelIndex, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel

class ModelException(Exception):
    '''
    model モジュールにおける例外の基底クラスです。
    '''
    pass

class ExcelQtConverter:

    '''
    ExcelのシートとQtモデルの変換を担います。

    Parameters:
    file_name -- Excelファイルのファイル名
    '''
    # IO は Input/Output の略

    def __init__(self, file_name):

        # 特定のシートの書き込む方法は下記を参照。
        # https://stackoverflow.com/a/20221655

        self.file_name = file_name
        self.px_workbook = load_workbook(file_name)

    def to_model(self, name, model_type=QStandardItemModel, header=True):
        '''
        ExcelのシートをQtのモデルに変換します。

        Parameters:
        name -- str型 Excelのシート名
        model_type -- type型 変換後に生成されるQtモデルの型を指定
                      （未指定の場合QStandardItemModel）
        header -- bool型 Trueの場合エクセルの1行目をヘッダとして扱う
                  （未指定の場合True）
        '''
        return convert_openpyxl_to_qtmodel(
            self.px_workbook.get_sheet_by_name(name),
            model_type=model_type,
            header=True
        )

    def from_model(self, qt_model, name):
        raise ModelException('未実装です')

    def save(self):
        self.px_workbook.save(self.file_name)

def convert_openpyxl_to_qtmodel(px_worksheet, model_type=QStandardItemModel, header=True):
    '''
    openpyxl の worksheet を、Qt のモデルに変換します。

    Parameters:
    name -- str型 Excelのシート名
    model_type -- type型 変換後に生成されるQtモデルの型を指定
                    （未指定の場合QStandardItemModel）
    header -- bool型 Trueの場合エクセルの1行目をヘッダとして扱う
                （未指定の場合True）
    '''
    qt_model = model_type()

    rows = px_worksheet.rows

    # 1行目をheaderとして扱う場合の処理
    if header:

        # 1行目のセルたちのタプルを取得
        header_cells = next(rows)

        # セルたちの値を取り出しリストに格納（リスト内包表記を使う）
        header_strings = [header_cell.value for header_cell in header_cells]

        # 取り出した値をqtのモデルのヘッダにする
        qt_model.setHorizontalHeaderLabels(header_strings)

    # すべてのセルを反復して値をqtのモデルに格納
    for row_index, cells in enumerate(rows):
        for column_index, cell in enumerate(cells):
            # cell は openpyxl の worksheet のセル
            # cell.valueはそのセルの値を格納

            # cell を qt の model の item に変換
            # (qt の model の item = エクセルで言うところのセル)
            qt_item = QStandardItem()
            qt_item.setText(str(cell.value))

            # 作成した item を model に登録
            qt_model.setItem(row_index, column_index, qt_item)

    return qt_model

class RelationProxyModel(QAbstractItemModel):

    '''
    主モデルに副モデルを結合し、それらが1つのモデルであるかのように表示されるようにします。

    Parameters:
    main_model -- QAbstractItemModel型 主モデルとして使うモデル。
    main_column -- int型 主モデルにおける、結合に利用するキーが入っている列の番号。
    sub_model -- QAbstractItemModel型 副モデルとして使うモデル。
    main_column -- int型 副モデルにおける、結合に利用するキーが入っている列の番号。
    '''

    def __init__(self, main_model, main_column, sub_model, sub_column):
        super().__init__()
        self.main_model = main_model
        self.sub_model = sub_model
        self.main_column = main_column
        self.sub_column = sub_column

        self.main_sub_map = None
        self.number_of_main_columns = None

        self.make_main_sub_map()
        self.count_main_columns()

        # メインモデルの発するシグナルを捕捉し自分自身から対応するシグナルを発します。
        self.main_model.dataChanged.connect(self.main_data_changed)
        self.main_model.rowsAboutToBeInserted.connect(self.beginInsertRows)
        self.main_model.rowsInserted.connect(self.endInsertRows)

        # メインモデルのデータに変更があった場合に、メイン・サブ対応表を作り直します。
        self.main_model.dataChanged.connect(self.make_main_sub_map)


    def __getattr__(self, name):
        return getattr(self.main_model, name)

    def make_main_sub_map(self):
        '''
        self.main_sub_mapを作ります。
        main_sub_mapはmain_modelの行:sub_modelの該当行 からなる辞書です。
        '''
        number_of_rows_for_main_model = self.main_model.rowCount()

        value_row_map = map_value_to_row(self.sub_model, self.sub_column)

        self.main_sub_map = {}

        for main_row in range(0, number_of_rows_for_main_model):
            main_index = self.main_model.index(main_row, self.main_column)
            main_value = self.main_model.data(main_index)
            if main_value:
                sub_row = value_row_map[main_value]
                self.main_sub_map[main_row] = sub_row

    def count_main_columns(self):
        '''
        self.number_of_main_columnsの値を更新します。
        '''
        self.number_of_main_columns = self.main_model.columnCount()

    def main_data_changed(self, topleft, bottomright):
        '''
        self.main_model.dataChanged シグナルが放出された場合に呼び出され、self.dataChanged シグナルを放出します。

        self.__init__内でself.main_model.dataChangedシグナルにconnectされる必要があります。
        '''
        redirected_topleft = self.index(topleft.row(), topleft.column())
        redirected_bottomright = self.index(bottomright.row(), bottomright.column())
        self.dataChanged.emit(redirected_topleft, redirected_bottomright, (Qt.DisplayRole,))

    def index(self, row, column, parent=QModelIndex()):
        '''
        QAbstractItemModel.index()の実装です。
        '''
        if column < self.columnCount():
            return self.createIndex(row, column, None)

        else:
            return QModelIndex()

    def columnCount(self, parent=QModelIndex()):
        '''
        QAbstractItemModel.index()の実装です。
        '''
        return self.main_model.columnCount() + self.sub_model.columnCount()

    def rowCount(self, parent=QModelIndex()):
        '''
        QAbstractItemModel.index()の実装です。
        '''
        return self.main_model.rowCount()

    def parent(self, child):
        '''
        QAbstractItemModel.index()の実装です。
        '''
        return QModelIndex()

    def data(self, index, role=Qt.DisplayRole):
        '''
        メインモデルの範囲外のインデックスをもつアイテムへの参照をサブモデルにリダイレクトします。
        QAbstractItemModel.data()の実装です。
        '''
        proxy_column = index.column()
        proxy_row = index.row()
        main_columns = self.number_of_main_columns

        # index がメインモデルの範囲外の場合
        if proxy_column >= main_columns:
            try:
                sub_row = self.main_sub_map[proxy_row]
            except KeyError:
                return None

            sub_column = proxy_column - main_columns
            redirected_index = self.sub_model.index(sub_row, sub_column)
            return self.sub_model.data(redirected_index, role)

        # index がメインモデルの範囲内の場合
        else:
            main_index = self.main_model.index(proxy_row, proxy_column)
            return self.main_model.data(main_index, role)



def map_value_to_row(qt_model: QAbstractItemModel, column):
    '''
    qt_modelの各行（row）に対して、{column列目の値: row}からなる辞書を返します。
    '''
    number_of_rows = qt_model.rowCount()
    value_row_pair = {}

    for row in range(number_of_rows):
        index = qt_model.index(row, column)
        value = qt_model.data(index)

        if not value in value_row_pair.keys():
            value_row_pair[value] = row

    return value_row_pair

class PurchasedItemModelWrapper:

    '''
    購入済み商品に対するラッパです。

    Parameters:
    qt_model -- QAbstructItemModel型 購入済み商品のモデル
    column_for_customer_id -- int型 顧客番号を格納する列
    column_for_item_id -- int型 商品番号を格納する列
    '''

    def __init__(self, qt_model, column_for_customer_id, column_for_item_id):
        self.qt_model = qt_model
        self.column_for_customer_id = column_for_customer_id
        self.column_for_item_id = column_for_item_id
    
    def add_item(self, customer_id, item_id):
        '''
        購入済み商品一覧に商品を追加します。

        Parameters:
        customer_id -- str型 購入者の顧客番号
        item_id -- str型 商品番号
        '''
        if not isinstance(customer_id, str):
            raise TypeError(
                'Customer ID must be in str, not' + str(type(customer_id))
            )

        if not isinstance(item_id, str):
            raise TypeError(
                'Item ID must be in str, not' + str(type(item_id))
            )

        row_at_end = self.qt_model.rowCount()

        qt_customer_id = QStandardItem(customer_id)
        qt_item_id = QStandardItem(item_id)
        self.qt_model.setItem(row_at_end, self.column_for_customer_id, qt_customer_id)
        self.qt_model.setItem(row_at_end, self.column_for_item_id, qt_item_id)

class Manager:

    '''
    全商品一覧と購入済み商品一覧を持っています。

    このクラスはExcelQtConverterに対するラッパです。ExcelQtConverterに
    一般性を持たせるために、会計簿管理に特化した機能はManagerクラスに分離されています。

    Parameters:
    file_name -- str型 エクセルファイルのファイル名
    sheet_name_for_all_items -- str型 全商品一覧を格納したシートの名前
    sheet_name_for_purchased_items -- str型 購入済み商品一覧を格納したシートの名前
    '''

    def __init__(self, file_name, sheet_name_for_all_items, sheet_name_for_purchased_items):
        self.excel_handler = ExcelQtConverter(file_name)
        self.sheet_name_for_all_items = sheet_name_for_all_items
        self.sheet_name_for_purchased_items = sheet_name_for_purchased_items
        self.all_item_model = None
        self.purchased_item_model = None

    def init_purchased_item_model(self, column_for_customer_id, column_for_item_id):
        '''
        購入済み商品一覧をExcelファイルからQtモデルに変換します。

        Parameters:
        column_for_customer_id -- int型 顧客番号を格納する列
        column_for_item_id -- int型 商品番号を格納する列
        '''
        purchased_model = self.excel_handler.to_model(self.sheet_name_for_purchased_items)

        all_model = self.all_item_model

        joined_model = RelationProxyModel(purchased_model, 1, all_model, 0)

        self.purchased_item_model = PurchasedItemModelWrapper(
            joined_model, 
            column_for_customer_id, 
            column_for_item_id
        )

    def init_all_item_model(self):
        '''
        全商品一覧をExcelファイルからQtモデルに変換します。
        '''
        self.all_item_model = self.excel_handler.to_model(self.sheet_name_for_all_items)

    def get_purchased_item_model(self):
        '''
        購入済み商品の一覧を返します。
        '''
        return self.purchased_item_model

    def get_all_item_model(self):
        '''
        全商品一覧を返します。
        '''
        return self.all_item_model