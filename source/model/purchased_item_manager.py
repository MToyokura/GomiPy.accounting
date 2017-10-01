import pandas as pd

class PurchasedItemManager:

    def __init__(self, worksheet):
        self.worksheet = worksheet

    def add_item(self, customer_id, item_id):
        d = {}
        new_item = pd.Series(
            (customer_id, item_id),
            index=('会計番号', '商品番号')
        )
        self.worksheet = self.worksheet.append(new_item, ignore_index=True)

    def filter_by_customer(self, customer_id):
        return self.worksheet[self.worksheet['会計番号'] == customer_id]

file = pd.ExcelFile('purchased_items.xlsx')
worksheet = file.parse('Sheet1')
purchased_item_manager = PurchasedItemManager(
    worksheet
)

print('読み込み完了')
print(purchased_item_manager.worksheet)
print('add_item()で商品追加')
purchased_item_manager.add_item(3,30001)
print(purchased_item_manager.worksheet)
print('filter_by_customer()で特定の会計番号の商品を絞り込み')
print(purchased_item_manager.filter_by_customer(1))
print('元のファイルに上書き保存')
purchased_item_manager.worksheet.to_excel('purchased_items.xlsx')
