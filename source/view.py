import sys

from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QFrame, 
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QStyleFactory,
    QTableView, QTreeView, QWidget)
from PyQt5.QtGui import QIcon

class AbstractWindow(QWidget):

    '''
    このクラスはアプリ内の全ウィンドウに共通の設定を施します。
    （ただし今のところアイコンを設定するのみです）
    ウィンドウを作るときはこのクラスを継承してください。
    '''

    def __init__(self):
        '''
        アイコンを設定します。
        '''
        super().__init__()
        self.setWindowIcon(QIcon('エコエコちゃん icon colored3.jpg'))
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
class MainWindow(AbstractWindow):

    '''
    アプリのメインウィンドウです。
    新規会計ボタンを持っています。

    Parameters:
    items -- type: model.Items 全商品リスト
    cart  -- type: model.DataframeAsModel 購入済み商品リスト
    '''

    def __init__(self, items, cart):
        super().__init__()
        self.title = 'PyQt Test'
        self.left = 300
        self.top = 200
        self.width = 200
        self.height = 150
        self.accounting_window = None
        self.init_ui()
        self.items_model = items
        self.cart_model = cart

    def init_ui(self):
        '''
        メインウィンドウ内部にGUIウィジェットを配置します。
        '''
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        

        button = QPushButton('新規会計', self)
        button.move(50, 50)
        button.resize(100, 50)
        button.clicked.connect(self.on_click)
        
        # ウィンドウを表示します。
        self.show()

    def on_click(self):
        '''
        新規会計ボタンが押されたときに呼び出されます。
        '''
        self.accounting_window = AccountingWindow(self.items_model, self.cart_model)

class AccountingWindow(AbstractWindow):

    '''
    会計処理ウィンドウです。

    Parameters:
    items -- type: model.Items 全商品リスト
    cart  -- type: model.DataframeAsModel 購入済み商品リスト
    '''

    def __init__(self, items, cart):
        super().__init__()
        self.title = '会計'
        self.left = 320
        self.top = 220
        self.width = 500
        self.height = 300
        self.items_model = items
        self.cart_model = cart
        self.init_ui()
        

    def init_ui(self):
        '''
        会計処理ウィンドウ内部にGUIウィジェットを配置します。
        '''
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # はじめに、会計処理ウィンドウ全体のレイアウトを設定します。
        # QHBoxLayout は、一個以上の箱が水平に並んだレイアウトを作ります。
        self.wrapper = QHBoxLayout(self)

        # wrapper の 中身を作っていきます。
        # QFrameは、内部にレイアウトを持つことができるウィジェットです。
        self.left = QFrame(self)
        # wrapper の左側の箱に入れます。
        self.wrapper.addWidget(self.left)

        # 今作ったQFrameの中に、新たにレイアウトを作ります。
        # GridLayout は、一個以上の箱が格子状に並んだレイアウトです。
        self.item_request_wrapper = QGridLayout(self.left)

        # GridLayoutの中に入れるウィジェットを作っていきます。
        # 「商品番号」ラベル
        self.item_request_id_label = QLabel(self)
        self.item_request_id_label.setText('商品番号')
        # GridLayout に入れます。
        # なお、addWidget() の引数は、(嵌められるウィジェット, 嵌める行, 嵌める列) です。
        self.item_request_wrapper.addWidget(self.item_request_id_label, 0, 0)

        # 商品番号入力欄
        self.item_request_id_input = QLineEdit(self)
        # GridLayout に入れます。
        self.item_request_wrapper.addWidget(self.item_request_id_input, 0, 1)

        # 「検索」ボタン
        self.item_request_id_search = QPushButton(self)
        self.item_request_id_search.setText('検索')
        self.item_request_id_search.clicked.connect(self.put_item_in_cart)
        # GridLayout に入れます。
        self.item_request_wrapper.addWidget(self.item_request_id_search, 0, 2)

        # wrapper の左から2番目の箱に入れる予定のウィジェットを作ります。
        # カートの中身をあらわす表
        self.right = QTableView(self)
        self.right.setModel(self.cart_model)
        # wrapper の左から2番目の箱に入れます。
        self.wrapper.addWidget(self.right)

        # ウィンドウを表示します。
        self.show()

    def put_item_in_cart(self):
        item = self.search_item()
        self.cart_model.append(item)
        
    def search_item(self):
        '''
        商品番号入力欄の内容を取得し、該当商品を return します。
        '''
        query = int(self.item_request_id_input.text())
        item = self.items_model.get_item_by_id(query)
        return item


def main(items, cart):
    '''
    GUI を起動します。

    Parameters:
    items -- type: model.Items 全商品リスト
    cart  -- type: model.DataframeAsModel 購入済み商品リスト
    '''

    app = QApplication(sys.argv)
    main_window = MainWindow(items, cart)
    sys.exit(app.exec_())

