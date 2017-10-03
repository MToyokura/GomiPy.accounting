import sys
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QPushButton, QStyleFactory, QWidget
from PyQt5.QtGui import QIcon

class AbstractWindow(QWidget):

    '''
    ウィンドウを作るときはこのクラスを継承してください。
    このクラスはアプリ内の全ウィンドウに共通の設定を施します。
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
    '''

    def __init__(self):
        '''
        メインウィンドウの設定を行います。
        '''
        super().__init__()
        self.title = 'PyQt Test'
        self.left = 300
        self.top = 200
        self.width = 200
        self.height = 150
        self.accounting_window = None
        self.init_ui()

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
        self.accounting_window = AccountingWindow()

class AccountingWindow(AbstractWindow):

    '''
    会計処理ウィンドウです。
    '''

    def __init__(self):
        '''
        会計処理ウィンドウの設定を行います。
        '''
        super().__init__()
        self.title = '会計'
        self.left = 320
        self.top = 220
        self.width = 500
        self.height = 300
        self.init_ui()
        

    def init_ui(self):
        '''
        会計処理ウィンドウ内部にGUIウィジェットを配置します。
        '''
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 「商品番号」ラベル
        item_request_item_id_label = QLabel(self)
        item_request_item_id_label.setText('商品番号')

        # 商品番号入力欄
        item_request_item_id_input = QLineEdit(self)

        # 「検索」ボタン
        item_request_item_id_search = QPushButton(self)
        item_request_item_id_search.setText('検索')

        # 商品説明文表示欄
        # 検索ボタンが押されるとここに該当商品の概要が表示されます（未実装）。
        item_request_item_description = QLabel(self)

        # レイアウト用の枠を作成します
        # ここで呼び出している GridLayout は、格子状の枠を作成します。
        item_request_layout = QGridLayout(self)

        # 枠にGUIウィジェットを嵌めていきます。
        # addWidget()の引数は、(嵌められるウィジェット, 嵌める行, 嵌める列) です。
        item_request_layout.addWidget(item_request_item_id_label, 0, 0)
        item_request_layout.addWidget(item_request_item_id_input, 0, 1)
        item_request_layout.addWidget(item_request_item_id_search, 0, 2)
        item_request_layout.addWidget(item_request_item_description, 1, 0)

        # ウィンドウを表示します。
        self.show()

        # 商品説明文表示欄を操作するための関数を作ります。
        # 関数内で定義される関数はクロージャと呼ばれます。
        # クロージャに関しては以下のサイトが分かりやすいと思います。
        # http://tomoprog.hatenablog.com/entry/2016/02/05/213056
        def refresh_item_description(text):
            '''
            商品説明文表示欄に指定された文字列を表示します。
            '''
            item_request_item_description.setText(text)
        
        # refresh_item_description() を self の属性として登録します。
        self.refresh_item_description = refresh_item_description
        


app = QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec_())
