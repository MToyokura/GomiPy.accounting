from openpyxl import load_workbook
from PyQt5.QtCore import QModelIndex
from itertools import product

'''
model.openpyxl_to_qtmodel() のためのテストツール

実行すると openpyxl の workbook を PyQt のQStandardItemModel に
変換し、内容を print() します。
'''
import model

def print_items(model):
    rows = model.rowCount()
    columns = model.columnCount()

    for row, column in product(range(0, rows), range(0, columns)):
        data = model.item(row, column).data()
        print(row, column, data)

def main():
    px_workbook = load_workbook('Python リサイクル市 会計用.xlsx')
    px_worksheet = px_workbook.get_sheet_by_name('raw')

    qt_model = model.convert_openpyxl_to_qtmodel(px_worksheet)
    print_items(qt_model)

main()
