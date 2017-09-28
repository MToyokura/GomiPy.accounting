# http://openpyxl.readthedocs.io/en/default/tutorial.html


from openpyxl import load_workbook

wb = load_workbook('Python リサイクル市 会計用.xlsx')
ws2 = wb["raw"]


#item_num = int(input())

item_num = 17004

item_num_col = ws2['A']


for i in item_num_col:
    if i.value == item_num:
        item_cell_string = str(i)
        item_cell_coordinate = item_cell_string[12:-1]
        item_cell_row = item_cell_string[13:-1]


tuple1 = ws2['A' + item_cell_row:'E' + item_cell_row]

for j in tuple1:
    for k in j:
        print (k.value)
    
