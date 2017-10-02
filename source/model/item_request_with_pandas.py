import pandas as pd

file = pd.ExcelFile('Python リサイクル市 会計用.xlsx')
worksheet = file.parse('raw')
item_num = int(input('商品番号を入力してください: '))
item_info = worksheet[worksheet['商品番号'] == item_num]

print(item_info)