import flet as ft
import mdEnums as en
from typing import List

#? このファイルはアプリ画面左部分に常駐するタブ変更用のボタン群のクラスです。
#? タブ変更用メソッドはほかの機能の兼ね合いで現状アプリ本体にあります。

#*TabChangeBar内でボタンの間に挟む「▼」文字。繰り返し構造のためクラス化してる。
class Left_DownMarkTxt(ft.Text):
    def __init__(self):
        super().__init__(
            width=180,
            text_align=ft.TextAlign.CENTER,
            value="▼"
        )

#*TabChangeBar内のタブを表すボタンの抽象クラスに当たるもの。
#*引数にタブ番号と動作設定(動作内容の関係でfrm本体に渡してもらう必要がある)，表示テキストを指定。
class Left_TabBtn(ft.FilledButton):
    #* tabIdx -> タブの列挙クラス，leftBtnClicked -> タブ変更用のメソッドを要求
    def __init__(self, tabIdx:en.TabIdx, leftBtnClicked:ft.ControlEvent):
        super().__init__(
            width=150,
            height=40
        )
        self.tabIdx = tabIdx
        self.on_click = leftBtnClicked
        self.text = self.tabIdx.get_tab_name()

#* 具象ボタンクラスを収納するコンテナ
#* 具象ボタンたちに与える動作メソッドはこのクラスの引数に要求
class Left_TabChangeBar(ft.Container):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(
            border=ft.border.all(1, ft.Colors.BLACK),
            padding=10,
            expand=1,
            bgcolor=ft.Colors.GREY_300
        )

        self.content = ft.Column(
            height=520,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            expand_loose=True,
            controls=self._add_contents(leftBtnClicked)
        )

    def _add_contents(self, left_btn_clicked:ft.ControlEvent) -> List[ft.Control]:
        controls:List[ft.Control] = []
        for tabIdx in en.TabIdx:
            if tabIdx.name == 'PLACE_HOLDER': continue
            controls.append(Left_TabBtn(tabIdx, left_btn_clicked))
            controls.append(Left_DownMarkTxt())
        controls.pop()
        return controls
