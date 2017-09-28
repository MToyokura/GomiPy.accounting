from datetime import datetime
class CustomerManager:

    '''
    顧客リストを管理するためのクラスです。
    '''

    def __init__(self):
        self.customers = []

    def add_customer(self):
        '''
        顧客リストに顧客を追加します。

        Return:
        追加された顧客の顧客番号(str)。
        '''

        customer_to_add = Customer()

        self.customers.append(customer_to_add)
        return len(self.customers) - 1

    def del_customer(self, customer):
        '''
        顧客番号で指定された顧客を削除します。
        '''
        self.customers.pop(customer)

    def get_


class Customer:

    '''
    顧客を表すクラスです。

    顧客番号は重複等を防ぐために CustomerManager クラスが管理します。
    本クラスは顧客番号の管理に関与しません。
    '''

    def __init__(self):
        self.items = []
        self.date = datetime.now()
        self.note = ''

    def put_into_cart(self, item):
        '''
        items 属性に商品を追加します。

        Arguments:
        item -- 追加される ItemProxy インスタンス。        
        '''

        # item 引数が ItemProxy のインスタンスであることを確かめます。
        # そうでない場合、TypeError を送出します。
        if not type(item) == ItemProxy:
            raise TypeError()

        self.items.append(item)

    def get_total(self):
        '''
        items 属性の商品の値段を合計します。

        Return:
        値段の合計を表す str。
        '''
        total = 0
        for item in self.items:
            total += item.get_price()

        return total

class ItemProxy:

    '''
    customers モジュール内において商品を表すクラスです。

    実際の商品情報は XXXX モジュールによって管理されます。
    そのため、customers モジュールが不用意に商品情報を
    書き換えるとXXXX モジュール内で整合性が採れなくなる
    恐れがあります。そこで、customers モジュール内では
    本クラスを使って商品情報を代替することにしました。

    本クラスは、書き換えを制限しつつ商品情報にアクセス
    するためのインターフェイスです。get_で始まるメソッドを
    使うことで XXXX が管理する商品情報を読むことはできますが
    書き換えることはできません。

    将来的に本クラスは XXXX モジュールに移すべきかも
    しれません。
    '''

    def __init__(self, item):
        '''
        Arguments:
        item -- XXXXモジュール内の商品情報の実体。
        '''
        self.entity = item
    
    def get_price(self):
        return self.entity.price

import pdb;pdb.set_trace()