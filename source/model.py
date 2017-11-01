from excelio import ExcelQtConverter
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from relation_proxy_model import RelationProxyModel

class ModelException(Exception):
    '''
    model モジュールにおける例外の基底クラスです。
    '''
    pass

class PurchasedItemModelWrapper:

    '''
    購入済み商品に対するラッパです。

    Parameters:
    qt_model -- QAbstractItemModel型 購入済み商品のモデル
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

        # 型チェック
        if not isinstance(customer_id, str):
            raise TypeError(
                'Customer ID must be in str, not' + str(type(customer_id))
            )

        # 型チェック
        if not isinstance(item_id, str):
            raise TypeError(
                'Item ID must be in str, not' + str(type(item_id))
            )

        # モデルの行数を取得
        row_at_end = self.qt_model.rowCount()

        # 顧客番号セルを作成
        qt_customer_id = QStandardItem(customer_id)
        # 商品番号セルを作成
        qt_item_id = QStandardItem(item_id)
        # セルをモデルに組み込む
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