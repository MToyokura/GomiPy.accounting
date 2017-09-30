## openpyxlに関する情報 http://openpyxl.readthedocs.io/en/default/tutorial.html
## このコードは各商品データを辞書型に格納する場合を想定したもの


from openpyxl import load_workbook

wb = load_workbook('Python リサイクル市 会計用.xlsx')
ws2 = wb["raw"]

info_keys = ['serialNum', 'name', 'initPrice', 'altPrice', 'remaining',
             'height', 'width', 'depth', 'company', 'model',
             'year', 'notes', 'web']

item_num = int(input('商品番号を入力してください: '))
item_num_col = ws2['A']

for i in item_num_col:
    # i は <Cell 'raw'.A204> のような値を取る
    if i.value == item_num:
        item_cell_string = str(i)
        item_cell_coordinate = item_cell_string[12:-1]
        item_cell_row = item_cell_string[13:-1]
        # item_cell_coordinate は 'A204' のような文字と数字を用いたセルの名前
        # item_cell_row は '204' のような行の名前

info_values = []
for j in ws2[item_cell_row]:
    info_values.append(j.value)

item_info_dict = dict(zip(info_keys, info_values))
item_dict = {item_num: item_info_dict}
print(item_dict)

'''
## クラス利用の想定
## 大量のクラスインスタンスを作るより辞書に格納するほうが好ましいらしい
class item:
    def __init__(self, serialNum, name, initPrice, altPrice, remaining,
                 height, width, depth, company, model, year, notes, web):
        self.serialNum = serialNum
        self.name = name
        self.initPrice = initPrice
        self.altPrice = altPrice
        self.remaining = remaining
        self.height = height
        self.width = width
        self.depth = depth
        self.company = company
        self.model = model
        self.year = year
        self.notes = notes
        self.web = web
'''