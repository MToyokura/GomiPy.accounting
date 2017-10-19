import pandas as pd
from openpyxl import load_workbook
from itertools import islice
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
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



class GomiPurchasedItemModel(QStandardItemModel):

    '''
    購入済み商品のモデルです。

    QStandardItemModelを継承しています。
    購入済み商品の管理の特化したメソッドが追加されています。
    ほとんどの挙動は継承元と変わりません。
    '''

    def configure(self, column_for_customer_id, column_for_item_id):
        '''
        顧客番号、商品番号を格納する列を指定します。

        Parameters:
        column_for_customer_id -- int型 顧客番号を格納する列
        column_for_item_id -- int型 商品番号を格納する列
        '''
        self.column_for_customer_id = column_for_customer_id
        self.column_for_item_id = column_for_item_id
    
    def add_item(self, customer_id, item_id):
        '''
        購入済み商品一覧に商品を追加します。

        Parameters:
        customer_id -- str型 購入者の顧客番号
        item_id -- str型 商品番号
        '''
        if type(customer_id) is not str:
            raise TypeError(
                'Customer ID must be in str, not' + str(type(customer_id))
            )

        if type(item_id) is not str:
            raise TypeError(
                'Item ID must be in str, not' + str(type(item_id))
            )

        row_at_end = self.rowCount()

        qt_customer_id = QStandardItem(customer_id)
        qt_item_id = QStandardItem(item_id)
        self.setItem(row_at_end, self.column_for_customer_id, qt_customer_id)
        self.setItem(row_at_end, self.column_for_item_id, qt_item_id)

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

    def init_purchased_item_model(self, column_for_customer_id, column_for_item_id):
        '''
        購入済み商品一覧をExcelファイルからQtモデルに変換します。

        Parameters:
        column_for_customer_id -- int型 顧客番号を格納する列
        column_for_item_id -- int型 商品番号を格納する列
        '''
        self.purchased_item_model = self.excel_handler.to_model(
            self.sheet_name_for_purchased_items,
            model_type=GomiPurchasedItemModel
        )
        self.purchased_item_model.configure(column_for_customer_id, column_for_item_id)

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