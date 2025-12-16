import flet as ft
import mdEnums as en

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
    def __init__(self, tabIdx:en.TabIdx, leftBtnClicked:ft.ControlEvent, text:str):
        super().__init__(
            width=150,
            height=40
        )
        self.tabIdx = tabIdx
        self.on_click = leftBtnClicked
        self.text = text

#? ここからボタンの具象クラス。新規タブの追加時にはここへ追加
class Left_TabBtn_Tab0(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(tabIdx=en.TabIdx.FILE_PATH_SELECT, leftBtnClicked=leftBtnClicked, text="ファイル設定")
class Left_TabBtn_Tab1(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(en.TabIdx.READ_DATA, leftBtnClicked, "読取結果")
class Left_TabBtn_Tab2(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(en.TabIdx.BUILDER_LOG, leftBtnClicked, "Builderログ")
class Left_TabBtn_Tab3(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(en.TabIdx.BUILDER_RESULT, leftBtnClicked, "Builder動作完了")

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
            controls=[
                Left_TabBtn_Tab0(leftBtnClicked),
                Left_DownMarkTxt(),
                Left_TabBtn_Tab1(leftBtnClicked),
                Left_DownMarkTxt(),
                Left_TabBtn_Tab2(leftBtnClicked),
                Left_DownMarkTxt(),
                Left_TabBtn_Tab3(leftBtnClicked),
            ]
        )
