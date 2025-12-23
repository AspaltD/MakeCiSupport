import flet as ft
import os
import re
from typing import Optional, Dict, List
#import mdAutoTest
import mdAutoTest

#? ファイルピッカーの宣言(コンテンツ内で使いたいのにPageでのOverlay作業が必要なためグローバル変数で宣言)
#! 改善案募集中：ﾌｧｲﾙﾋﾟｯｶｰの同一の機能を同じコンテナ内で使うにはそれぞれで個別のﾌｧｲﾙﾋﾟｯｶｰが必要っぽい。
filePickers: Dict[str,ft.FilePicker]        #*ファイルピッカーの辞書
fileData: List[List[str]] = [["FileData"]]  #*読み書きするファイルの中身を一時保持するための二次元リスト
settingData: Dict[str,str] = {}             #*Builderのパスの保存，バージョン情報などの保持情報を入れる辞書
outpuuuutPath:str = os.getcwd() + os.sep + "outpuuuut.txt"


#* アプリ各所でレイアウト維持のために使用するプレースホルダ。デフォルトの色指定をランダムで設定してる。
class PlaceHoldeeeer(ft.Placeholder):
    def __init__(self, expand:Optional[int]=None, color:Optional[ft.Colors]=ft.Colors.random()):
        super().__init__()
        self.data = 99      #* タブのインデックス番号に当たる。後で処理の回避用に使用。
        if expand is None:
            self.expand = True
        else:
            self.expand = expand
        self.color = color




class MakeCiApp(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True
        )
        self.content = ft.Row(
            expand=True,
            controls=[
                PlaceHoldeeeer(1),
                PlaceHoldeeeer(3)
            ]
        )


def main(page: ft.Page):
    page.title = "Make Ci App"
    page.window.width = 800
    page.window.height = 605
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER


    makeCi = MakeCiApp()

    page.add(makeCi)
    page.window.center()
    page.update()

ft.app(target=main)