import flet as ft
import mdEnums as en
from typing import List, Tuple

class Btm_TabFuncBtn(ft.FilledButton):
    def __init__(self, work_place_idx:en.BtmBtnIdx, def_click_event:ft.ControlEvent):
        super().__init__(
            width=120,
            on_click=def_click_event,
        )
        self.workPlaceIdx = work_place_idx
        self.text = self.workPlaceIdx.get_btn_def_text()

    def change_property(self, toTabIdx:en.TabIdx) -> Tuple[str, ...]:
        self.disabled = True
        return ("self_disabled -> True",)

class BtmBtn_EXit(Btm_TabFuncBtn):
    def __init__(self, exit_event:ft.ControlEvent):
        super().__init__(
            work_place_idx=en.BtmBtnIdx.EXIT_APP,
            def_click_event=exit_event
            )

    def change_property(self, toTabIdx: en.TabIdx) -> Tuple[str, ...]:
        match toTabIdx.name:
            case 'BUILDER_LOG':
                self.disabled = True
            case _:
                self.disabled = False
        return (f'BtmBtn_Exit_disabled  -> {self.disabled}',
                f'BtmBtn_Exit_event     -> {self.on_click.__qualname__}',
                )

class BtmBtn_Next(Btm_TabFuncBtn):
    def __init__(self, def_click_event:ft.ControlEvent):
        super().__init__(en.BtmBtnIdx.NEXT_TAB, def_click_event)

    def change_property(self, toTabIdx: en.TabIdx) -> Tuple[str, ...]:
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
        return (f'BtmBtn_Next_disabled  -> {self.disabled}',
                f'BtmBtn_Next_text      -> {self.text}',
                f'BtmBtn_Next_event     -> {self.on_click.__qualname__}',
                )
class BtmBtn_Func1(Btm_TabFuncBtn):
    def __init__(self, def_click_event:ft.ControlEvent):
        super().__init__(en.BtmBtnIdx.OTHER_FUNC1, def_click_event)

    def change_property(self, toTabIdx: en.TabIdx) -> Tuple[str, ...]:
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
        return (f'BtmBtn_Func1_disabled -> {self.disabled}',
                f'BtmBtn_Func1_text     -> {self.text}',
                f'BtmBtn_Func1_event    -> {self.on_click.__qualname__}',
                )

class BtmBtn_Func2(Btm_TabFuncBtn):
    def __init__(self, def_click_event:ft.ControlEvent):
        super().__init__(en.BtmBtnIdx.OTHER_FUNC2, def_click_event)

    def change_property(self, toTabIdx: en.TabIdx) -> Tuple[str, ...]:
        match toTabIdx.name:
            case 'READ_DATA':
                self.text = "Remove"
                self.visible = True
            case _:
                self.text = "Func1"
                self.visible = False
        return (f'BtmBtn_Func2_disabled -> {self.disabled}',
                f'BtmBtn_Func2_text     -> {self.text}',
                f'BtmBtn_Func2_event    -> {self.on_click.__qualname__}',
                )

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

