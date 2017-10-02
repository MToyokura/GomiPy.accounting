import pandas as pd

class PurchasedItemManager:

    '''
    購入済み商品のリストを管理するクラスです。
    '''

    def __init__(self, dataframe):
        '''
        Parameters:
        dataframe -- Pandas の dataframe
        '''
        self.dataframe = dataframe

    def add_item(self, customer_id, item_id):
        '''
        購入済み商品リストに商品を追加します。

        Parameters:
        customer_id -- int 商品を購入した顧客の会計番号
        item_id     -- int 追加する商品の商品番号 
        '''
        d = {}
        new_item = pd.Series(
            (customer_id, item_id),
            index=('会計番号', '商品番号')
        )
        self.dataframe = self.dataframe.append(new_item, ignore_index=True)

    def how_much(self, row):
        '''
        商品の値段を返します。まだ実装していません。

        Parameters:
        row -- int 購入済み商品リストの中で、値段を知りたい商品が記録されてる行の行名

        Return:
        int 値段
        '''
        pass

    def remove_item(self, row):
        '''
        購入済み商品リストから、商品を削除します。

        Parameters:
        row -- int 購入済み商品リストの中で、削除したい商品が記録されている行の行名
        '''
        self.dataframe = self.dataframe.drop(row)

    def filter_by_customer(self, customer_id):
        '''
        購入済み商品リストから、特定の会計番号の商品を抜き出します。

        Parameters:
        customer_id -- int 抜き出す会計番号
        '''
        return self.dataframe[self.dataframe['会計番号'] == customer_id]

if __name__ == '__main__':
    '''
    このファイルが単体で実行されている場合は、if文内のスクリプトが実行されます。

    逆に他のスクリプトから import されている場合は、以下のコードは実行されません。
    '''
    file = pd.ExcelFile('purchased_items.xlsx')
    worksheet = file.parse('Sheet1')
    purchased_item_manager = PurchasedItemManager(worksheet)

    print('読み込み完了')
    print(purchased_item_manager.dataframe)
    print('add_item()で商品追加')
    purchased_item_manager.add_item(3,30001)
    print(purchased_item_manager.dataframe)
    print('filter_by_customer()で特定の会計番号の商品を絞り込み')
    print(purchased_item_manager.filter_by_customer(1))
    print('元のファイルに上書き保存')
    purchased_item_manager.dataframe.to_excel('purchased_items.xlsx')
