'''
model.pyの機能をチェックするunit testです。
'''

# unit test については https://docs.python.jp/3/library/unittest.html

import unittest
from itertools import product
import model
from openpyxl import Workbook

class TestConversionBetweenQtmodelAndOpenpyxl(unittest.TestCase):

    '''
    openpyxlのワークシート⇔Qtのモデルの変換が正しく行われるかチェックします。
    '''

    def test_convert_openpyxl_to_qtmodel(self):
        '''
        openpyxlのワークシートとして表現された2次元の表をqtのモデルに変換しても表の内容は変化しない。
        '''
        # ダミーの表データを{(row, column): value}形式のPython辞書として作る
        data = create_fruit_price_data()

        # ダミーの表データをopenpyxlのワークシートに変換
        px_worksheet = convert_index_value_pair_to_openpyxl(data)

        # openpyxlのワークシートをQtのモデルに変換
        qt_model = model.convert_openpyxl_to_qtmodel(px_worksheet)

        # Qtのモデルを{(row, column): value}形式のPython辞書に変換
        reversed_data = convert_qtmodel_to_index_value_pair(qt_model)

        # もとのデータと等しくない場合はテストを失敗させる
        self.assertEqual(data, reversed_data)

class TestRelationProxyModel(unittest.TestCase):

    '''
    途中
    '''

    def test_map_value_to_row(self):
        '''
        model.map_value_to_rowは、qt_modelの各行（row）に対して、{column列目の値: row}からなる辞書を返す。
        '''
        key_column = 0
        fruit_color =create_fruit_color_data()

        fruit_color_worksheet = convert_index_value_pair_to_openpyxl(fruit_color)
        fruit_color_model = model.convert_openpyxl_to_qtmodel(fruit_color_worksheet)

        actual_map = model.map_value_to_row(fruit_color_model, key_column)
        expected_map = make_value_row_map_for_dummy_table(fruit_color, key_column)

        self.assertEqual(actual_map, expected_map)

    def test_make_main_sub_map(self):
        '''
        model.RelationProxyModel.make_main_sub_map()は、main_modelの行:sub_modelの該当行 からなる辞書を返す。
        '''
        fruit_color = create_fruit_color_data()
        fruit_price = create_fruit_price_data()

        fruit_color_worksheet = convert_index_value_pair_to_openpyxl(fruit_color)
        fruit_price_worksheet = convert_index_value_pair_to_openpyxl(fruit_price)

        fruit_color_model = model.convert_openpyxl_to_qtmodel(fruit_color_worksheet)
        fruit_price_model = model.convert_openpyxl_to_qtmodel(fruit_price_worksheet)

        proxy = model.RelationProxyModel(fruit_color_model, 0, fruit_price_model, 0)

        actual_map = proxy.main_sub_map
        expected_map = {index - 1: value - 1 for index, value in create_fruit_price_color_map().items()}

        self.assertEqual(actual_map, expected_map)
    
    def test_index_with_reference_to_sub_model(self):
        '''
        model.RelationProxyModel は、連結された2つのモデルがあたかも1つのモデルであるかのようにふるまう。
        '''
        fruit_color = create_fruit_color_data()
        fruit_price = create_fruit_price_data()

        fruit_color_worksheet = convert_index_value_pair_to_openpyxl(fruit_color)
        fruit_price_worksheet = convert_index_value_pair_to_openpyxl(fruit_price)

        fruit_color_model = model.convert_openpyxl_to_qtmodel(fruit_color_worksheet)
        fruit_price_model = model.convert_openpyxl_to_qtmodel(fruit_price_worksheet)

        proxy = model.RelationProxyModel(fruit_color_model, 0, fruit_price_model, 0)

        actual = convert_qtmodel_to_index_value_pair(proxy, header=False)
        expected = remove_header(create_fruit_color_price_data())

        self.assertEqual(actual, expected)

def make_value_row_map_for_dummy_table(dummy_table, column, header=True):

    def is_column_of_interest(index):
        return index[1] == column

    is_header = make_header_finder(header)

    def is_index_of_interest(index):
        return is_column_of_interest(index) and not is_header(index)

    filtered_indexes = filter(is_index_of_interest, dummy_table.keys())

    value_row_map = {dummy_table[filtered_index]: filtered_index[0] - (1 if header else 0) for filtered_index in filtered_indexes}

    return value_row_map

def make_header_finder(header: bool):
    '''
    インデックスがヘッダかどうか判別する関数を返します。

    Parameter:
    header -- True（デフォルト）で、先頭行をヘッダとみなします。
    '''
    if header:
        def is_header(index):
            '''
            Parameter:
            index -- (row, column)のタプル。

            Return:
            bool型 indexが0行目ならTrue、違えばFalse
            '''
            return index[0] == 0
    else:
        def is_header(index):
            '''
            Parameter:
            index -- (row, column)のタプル。

            Return:
            bool型 つねにFalse
            '''
            return False
    
    return is_header


def convert_qtmodel_to_index_value_pair(qt_model, header=True):
    '''
    Qtのモデルをもとにindexとvalueのペアからなる辞書を作ります。
    現時点ではQtモデルとして2次元の表を想定しており、より深い木構造をもつモデルには対応しません。
    header=True（デフォルト）でQtモデルのヘッダもindex:valueペアに変換します。

    Parameters:
    qt_model -- QAbstractItemModelインタフェースをもつオブジェクト

    Return:
    表のインデックスをキーに、表の値を値にもつPython辞書。
    表のインデックスは(row, column)のtupleで、(0,0)から。
    '''
    rows = qt_model.rowCount()
    columns = qt_model.columnCount()

    ret = {}

    if header:
        for column in range(0, columns):
            header_item = qt_model.horizontalHeaderItem(column)
            if header_item is not None:
                header_string = header_item.text()
                ret[(0, column)] = header_string

    extra_row_index = 1 if header else 0
    for row, column in product(range(0, rows), range(0, columns)):
        index = qt_model.index(row, column)
        value = qt_model.data(index)
        ret[(row + extra_row_index, column)] = value

    return ret

def convert_index_value_pair_to_openpyxl(data):
    '''
    data引数をもとにopenpyxlのワークシートを作ります。

    Parameters:
    data -- セルのインデックスをキーに、セルの値を値にもつ辞書。
            セルのインデックスは(row, column)のtupleで、(0,0)から。

    Return:
    openpyxlのワークシート

    '''
    px_workbook = Workbook()
    px_worksheet = px_workbook.active

    for index, value in data.items():
        row    = index[0] + 1
        column = index[1] + 1
        px_worksheet.cell(row=row, column=column, value=value)

    return px_worksheet
    

def remove_header(data):
    '''
    index:value ぺアからなる辞書から、0行目を削除します。ヘッダの削除に使えます。

    Parameters:
    data -- セルのインデックスをキーに、セルの値を値にもつ辞書。
            セルのインデックスは(row, column)のtupleで、(0,0)から。

    Return:
    dataから0行目を削除し、n行目をn-1行目にした辞書。
    '''
    is_header = make_header_finder(header=True)
    ret = {}
    for index, value in data.items():
        if is_header(index):
            continue

        new_index = (index[0] - 1, index[1])
        ret[new_index] = value

    return ret



def create_fruit_price_data():
    '''
    ダミーデータを返します。

    果物の値段のテーブルを返します。
    '''
    data = {
        (0,0): 'Fruit', 
        (0,1): 'Price', 
        (1,0): 'Apple', 
        (1,1): '300', 
        (2,0): 'Berry', 
        (2,1): '400'
    }
    return data

def create_fruit_color_data():
    '''
    ダミーデータを返します。

    果物の色のテーブルを返します。
    '''
    data = {
        (0,0): 'Fruit', 
        (0,1): 'Color', 
        (1,0): 'Berry', 
        (1,1): 'Blue', 
        (2,0): 'Apple', 
        (2,1): 'Red'
    }
    return data


def create_fruit_color_price_data():
    '''
    ダミーデータを返します。

    果物の色と値段を結合したテーブルを返します。
    '''
    data = {
        (0,0): 'Fruit', 
        (0,1): 'Color', 
        (0,2): 'Fruit', 
        (0,3): 'Price', 
        (1,0): 'Berry', 
        (1,1): 'Blue', 
        (1,2): 'Berry', 
        (1,3): '400', 
        (2,0): 'Apple', 
        (2,1): 'Red', 
        (2,2): 'Apple', 
        (2,3): '300', 
    }
    return data


def create_fruit_price_color_map():
    '''
    fruit_priceの行:fruit_colorの該当行 からなる辞書
    '''
    data = {
        1:2, # Appleはpriceで1行目、colorで2行目
        2:1  # Berryはpriceで2行目、colorで1行目
    }
    return data

if __name__ == '__main__':
    unittest.main()
