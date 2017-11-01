'''
プログラムへのエントリポイント。
'''
import model
import view

def main():
    '''
    エクセルからデータを読み込みGUIを起動します。
    '''

    # エクセルファイルを開く。
    manager = model.Manager('Python リサイクル市 会計用.xlsx', 'raw', '会計録')

    # 商品情報のシートを取得。
    # qtのmodelが得られる。
    items_model = manager.init_all_item_model()
    items_model = manager.get_all_item_model()

    # カートとして使うためのモデルを作る。
    manager.init_purchased_item_model(0,1)
    cart_model = manager.get_purchased_item_model()

    # GUIを起動。
    view.main(items_model, cart_model)

main()