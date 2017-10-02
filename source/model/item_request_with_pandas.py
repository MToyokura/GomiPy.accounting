import pandas as pd

file = pd.ExcelFile('Python リサイクル市 会計用.xlsx')
worksheet = file.parse('raw')

def get_ID(index):
    return worksheet.get_value(index, '商品番号')

def get_name(index):
    return worksheet.get_value(index, '商品名')

def get_initPrice(index):
    return worksheet.get_value(index, '初期価格')

def get_altPrice(index):
    return worksheet.get_value(index, '値引き価格(空白)')


item_num = int(input('商品番号を入力してください: '))
item_info = worksheet[worksheet['商品番号'] == item_num]
print(item_info)
item_index = item_info.index[0]
print(item_index)
print(get_ID(item_index))
print(get_name(item_index))
print(get_initPrice(item_index))
print(get_altPrice(item_index))