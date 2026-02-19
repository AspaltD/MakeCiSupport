import flet as ft
from typing import List

import enEnums as en


#*タブ変更欄でボタンの間に置く用のテキスト
class Left_txt_DownMark(ft.Text):
    def __init__(self, value:str="▼"):
        super().__init__(
            width=180,
            text_align=ft.TextAlign.CENTER,
            value=value
        )

#*タブ変更欄のタブとリンクするボタン
class Left_btn_TabChange(ft.FilledButton):
    def __init__(self, tab_idx:en.TabIdx):
        super().__init__(
            width=150,
            height=40
        )
        self.tabIdx = tab_idx
        self.text = self.tabIdx.get_tab_name()

#*タブ変更欄。ここで実装してるのは容器としての各パーツだけ。
class Left_box_TabChangeBar(ft.Container):
    def __init__(self):
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
            controls=self._add_controls()
        )

    def _add_controls(self) -> List[ft.Control]:
        controls:List[ft.Control] = []
        for _tabIdx in en.TabIdx:
            if _tabIdx.name == 'PLACE_HOLDER': continue
            controls.append(Left_btn_TabChange(_tabIdx))
            controls.append(Left_txt_DownMark())
        controls.pop()
        return controls

#*ボトムボタンの属性のうちタブに依存するものを抜き出したもの
class Btm_data_BtnProps():
    def __init__(self,
                btm_btn_idx:en.BtmBtnIdx,
                visible:bool=True,
                disabled:bool=True,
                text:str="None",
                on_click:ft.OptionalControlEventCallable=None
        ):
        self.BTMBTNIDX = btm_btn_idx
        self.VISIBLE = visible
        self.DISABLED = disabled
        if text == "None":
            _text = self.BTMBTNIDX.get_def_txt()
        else:
            _text = text
        self.TEXT = _text
        self.ON_CLICK = on_click

#*タブの下部に置く固有の機能を持たせるためのボタン。
class Btm_btn_TabFunc(ft.FilledButton):
    def __init__(self, btm_btn_idx:en.BtmBtnIdx):
        super().__init__(
            width=120
        )
        self.btmBtnIdx = btm_btn_idx
        self.text = self.btmBtnIdx.get_def_txt()

    def change_property(self, data_btn_props:Btm_data_BtnProps):
        props = data_btn_props
        if props.BTMBTNIDX != self.btmBtnIdx: raise ValueError("BtmBtnIdx is not match.")
        self.visible = props.VISIBLE
        self.disabled = props.DISABLED
        self.text = props.TEXT
        self.on_click = props.ON_CLICK