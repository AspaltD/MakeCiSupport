import flet as ft
import mdEnums as en
from typing import List

class Btm_TabFuncBtn(ft.FilledButton):
    def __init__(self, work_place_idx:en.BtmBtnIdx):
        super().__init__(
            width=120
        )
        self.workPlaceIdx = work_place_idx
        self.text = self.workPlaceIdx.get_btn_def_text()

    def change_property(self, toTabIdx:en.TabIdx):
        self.disabled = True

class BtmBtn_EXit(Btm_TabFuncBtn):
    def __init__(self):
        super().__init__(
            work_place_idx=en.BtmBtnIdx.EXIT_APP
            )
        self.on_click = lambda: self.page.window.close()

    def change_property(self, toTabIdx: en.TabIdx):
        match toTabIdx.name:
            case 'BUILDER_LOG':
                self.disabled = True
            case _:
                self.disabled = False

class BtmBtn_Next(Btm_TabFuncBtn):
    def __init__(self):
        super().__init__(en.BtmBtnIdx.NEXT_TAB)

    def change_property(self, toTabIdx: en.TabIdx):
        match toTabIdx.name:
            case 'FILE_PATH_SELECT':
                self.text = "ReadCIF"
                self.disabled = False
            case 'READ_DATA':
                self.text = "Save&Go"
                self.disabled = False
            case 'BUILDER_LOG':
                self.text = "Stop"
                self.disabled = False
            case _:
                self.text = "Next"
                self.disabled = True
class BtmBtn_Func1(Btm_TabFuncBtn):
    def __init__(self):
        super().__init__(en.BtmBtnIdx.OTHER_FUNC1)

    def change_property(self, toTabIdx: en.TabIdx):
        match toTabIdx.name:
            case 'FILE_PATH_SELECT':
                self.text = "ReadTXT"
                self.visible = True
            case 'READ_DATA':
                self.text = "Save"
                self.visible = True
            case _:
                self.text = "Func1"
                self.visible = False

class BtmBtn_Func2(Btm_TabFuncBtn):
    def __init__(self):
        super().__init__(en.BtmBtnIdx.OTHER_FUNC2)

    def change_property(self, toTabIdx: en.TabIdx):
        match toTabIdx.name:
            case 'READ_DATA':
                self.text = "Remove"
                self.visible = True
            case _:
                self.text = "Func1"
                self.visible = False

#? 未使用。できれば組み込みたい。
class Btm_BtnBar(ft.Row):
    def __init__(self):
        super().__init__(
            expand=1,
            alignment=ft.MainAxisAlignment.END,
            controls=self._add_btn_def()
        )

    def _add_btn_def(self) -> List[Btm_TabFuncBtn]:
        controls:List[Btm_TabFuncBtn] = [
            BtmBtn_Next(),
            BtmBtn_EXit(),
            BtmBtn_Func1(),
            BtmBtn_Func2()
        ]
        return controls

