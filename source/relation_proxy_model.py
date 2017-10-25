'''
PyQtで2つのQAbstractItemModelを結合するためのモジュールです。
'''

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt

class RelationProxyModel(QAbstractItemModel):

    '''
    主モデルに副モデルを結合し、それらが1つのモデルであるかのように表示されるようにします。

    属性の探索は、このクラス→継承元（QAbstractItemModel）→主モデルの順に行われます。

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

        self.mapper = Mapper(main_model, main_column, sub_model, sub_column, self)

        # メインモデルの発するシグナルを捕捉し自分自身から対応するシグナルを発します。
        self.main_model.rowsAboutToBeInserted.connect(self.beginInsertRows)
        self.main_model.rowsInserted.connect(self.endInsertRows)
        self.main_model.dataChanged.connect(self.emit_data_changed)


        # サブモデルの発するシグナルを補足し自分自身から対応するシグナルを発します。
        self.sub_model.dataChanged.connect(self.emit_data_changed)


    def __getattr__(self, name):
        '''
        存在しない属性が呼び出された場合に呼び出されるメソッドです。
        
        主モデルの属性を探索します。
        '''
        return getattr(self.main_model, name)

    def emit_data_changed(self, topleft, bottomright):
        '''
        ソースモデルの dataChanged シグナルが放出された場合に呼び出され、self.dataChanged シグナルを放出します。

        self.__init__内でソースモデルの dataChanged シグナルにconnectされる必要があります。

        Parameters:
        topleft -- QAbstractItemModel.dataChanged() のtopLeft引数を参照。
        bottomright -- QAbstractItemModel.dataChanged() のbottomRight引数を参照。
        '''
        redirected_topleft = self.mapper.from_source(topleft)
        redirected_bottomright = self.mapper.from_source(bottomright)
        self.dataChanged.emit(redirected_topleft, redirected_bottomright)

    def index(self, row, column, parent=QModelIndex()):
        '''
        QAbstractItemModel.index()の実装です。
        '''
        # 引数が範囲内ならば有効なインデックスを返す
        if column < self.columnCount() and row < self.rowCount():
            return self.createIndex(row, column, None)

        # 範囲外なら無効なインデックスを返す
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

        redirected_index = self.mapper.to_source(index)
        if not redirected_index.isValid():
            return None

        if redirected_index.model() == self.main_model:
            return self.main_model.data(redirected_index, role)
        else:
            return self.sub_model.data(redirected_index, role)


class MapperException(Exception):
    '''
    Mapperクラスにおける例外の基底クラスです。
    '''
    pass

class NoCorrespondingRowError(MapperException):
    pass

class Mapper:
    def __init__(self, main_model, main_column, sub_model, sub_column, proxy_model):
        self.main_model = main_model
        self.sub_model = sub_model
        self.main_column = main_column
        self.sub_column = sub_column
        self.proxy_model = proxy_model

        self.main_sub_map = None
        self.sub_main_map = None
        self.number_of_main_columns = None

        self.make_main_sub_map()
        self.count_main_columns()
        self.sub_main_map = self.get_reversed_map()

        # メインモデルのデータに変更があった場合に、メイン・サブ対応表を作り直します。
        self.main_model.dataChanged.connect(self.make_main_sub_map)

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
        

    def get_reversed_map(self):
        '''
        self.main_sub_mapの値とキーを逆にします。

        subの行番号からメインの該当行の番号を知りたいときに使ってください。
        Return: dict型
        '''
        return {value: key for key, value in self.main_sub_map.items()}

    def from_source(self, index: QModelIndex):
        '''
        ソースモデル（mainモデルかsubモデルのどちらか）のインデックスをプロキシモデルのインデックスに変換します。
        '''

        if index.model() == self.main_model:
            return self.proxy_model.index(index.row(), index.column())

        else:
            try:
                redirected_index = self.proxy_model.index(
                    self.sub_main_map[index.row()],
                    index.column() + self.number_of_main_columns
                )
                return redirected_index
            except KeyError:
                return QModelIndex()

    def to_source(self, index: QModelIndex):
        '''
        プロキシモデルのインデックスをソースモデルのインデックスに変換します。
        '''
        proxy_column = index.column()
        proxy_row = index.row()
        main_columns = self.number_of_main_columns

        # index がメインモデルの範囲外の場合
        if proxy_column >= main_columns:
            # サブモデルの該当行の行番号を取得
            try:
                sub_row = self.main_sub_map[proxy_row]
            # 該当行がない場合、無効なインデックスを返す
            except KeyError:
                return QModelIndex()

            # サブモデルの該当列の列番号を取得
            sub_column = proxy_column - main_columns
            # サブモデルにアクセス
            redirected_index = self.sub_model.index(sub_row, sub_column)

        # index がメインモデルの範囲内の場合
        else:
            # メインモデルにアクセス
            redirected_index = self.main_model.index(proxy_row, proxy_column)

        return redirected_index

    def count_main_columns(self):
        '''
        self.number_of_main_columnsの値を更新します。
        '''
        self.number_of_main_columns = self.main_model.columnCount()

def map_value_to_row(qt_model: QAbstractItemModel, column):
    '''
    qt_modelの各行（row）に対して、{引数column列目の値: row}からなる辞書を返します。

    Parameters:
    qt_model -- QAbstractItemModel型
        e.g.
            Fruit |  Color
            ------+------
        0   Apple |  Red
        1   Berry |  Blue
    
    column -- int型 列番号
        e.g. 0

    return: dict型
        e.g. {'Apple': 0, 'Berry': 1}

    '''
    number_of_rows = qt_model.rowCount()
    value_row_pair = {}

    for row in range(number_of_rows):
        index = qt_model.index(row, column)
        value = qt_model.data(index)

        if not value in value_row_pair.keys():
            value_row_pair[value] = row

    return value_row_pair

