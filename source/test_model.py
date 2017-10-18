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
        data = create_table_dummy_data()

        # ダミーの表データをopenpyxlのワークシートに変換
        px_worksheet = convert_index_value_pair_to_openpyxl(data)

        # openpyxlのワークシートをQtのモデルに変換
        qt_model = model.convert_openpyxl_to_qtmodel(px_worksheet)

        # Qtのモデルを{(row, column): value}形式のPython辞書に変換
        reversed_data = convert_qtmodel_to_index_value_pair(qt_model)

        # もとのデータと等しくない場合はテストを失敗させる
        self.assertEqual(data, reversed_data)


def convert_qtmodel_to_index_value_pair(qt_model):
    '''
    Qtのモデルをもとにindexとvalueのペアからなる辞書を作ります。
    現時点ではQtモデルとして2次元の表を想定しており、より深い木構造をもつモデルには対応しません。

    Parameters:
    qt_model -- QAbstractItemModelインタフェースをもつオブジェクト

    Return:
    表のインデックスをキーに、表の値を値にもつ辞書。
    表のインデックスは(row, column)のtupleで、(0,0)から。
    '''
    rows = qt_model.rowCount()
    columns = qt_model.columnCount()

    ret = {}

    for row, column in product(range(0, rows), range(0, columns)):
        value = qt_model.item(row, column).data()
        ret[(row, column)] = value

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

def create_table_dummy_data():
    '''
    ダミーデータを返します。
    '''
    data = {
        (0,0): 'Tomato', 
        (0,1): 'Banana', 
        (1,0): 'Berry', 
        (1,1): 'Cherry'
    }
    return data

if __name__ == '__main__':
    unittest.main()
