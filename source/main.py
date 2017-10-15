'''
プログラムへのエントリポイント。
'''
import model, view

def main():
    '''
    エクセルからデータを読み込みGUIを起動します。
    '''

    # エクセルファイルを開く。
    excel = model.Excel()
    excel.open('Python リサイクル市 会計用.xlsx')

    # 商品情報のシートを取得。
    # pandasのdataframeが得られる。
    items = excel.get_dataframe('raw')

    # pandas の dataframeのままでは扱いづらいので
    # 商品の検索など、商品情報管理に必要なメソッドをもつ
    # Item モデル（modelモジュールで定義）のインスタンスにdataframeを渡す。
    items_model = model.Items(items)

    # カートとして使うためのモデルを作る。
    cart_model = model.DataframeAsModel()

    # GUIを起動。
    view.main(items_model, cart_model)

main()