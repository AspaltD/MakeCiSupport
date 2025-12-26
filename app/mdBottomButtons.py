import flet as ft
import mdEnums as en
from typing import List, Tuple, Dict, Union, Optional

class Dict_BtmBtnProperties():
    def __init__(self,
                btm_btn_idx:en.BtmBtnIdx,
                visible:bool,
                disabled:bool,
                text:str,
                on_click:ft.ControlEvent):
        self.BTMBTNIDX = btm_btn_idx
        self.VISIBLE = visible
        self.DISABLED = disabled
        self.TEXT = text
        self.ON_CLICK = on_click

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
    
class If_BottomFuncBtn(ft.FilledButton):
    def __init__(self, btm_btn_idx:en.BtmBtnIdx):
        super().__init__(
            width=120,
        )
        self.btmBtnIdx = btm_btn_idx
        self.text = self.btmBtnIdx.get_btn_def_text()

    def change_property(self, dict_properties:Dict_BtmBtnProperties) -> Tuple[str, ...]:
        prop = dict_properties
        self.visible = prop.VISIBLE
        self.disabled = prop.DISABLED
        self.text = prop.TEXT
        self.on_click = prop.ON_CLICK
        return (
            f'BtmBtn_{self.btmBtnIdx.get_btn_def_text()}_properties -->'
            f'  visible  -> {self.visible}',
            f'  disabled -> {self.disabled}',
            f'  text     -> {self.text}',
            f'  on_click -> {self.on_click.__qualname__}',
            "<--",
        )

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
            case 'MI_PATH_SELECT':
                self.text = "Preview"
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
            case 'MI_PREVIEW':
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
            controls=self._add_btn()
        )

    def _add_btn(self) -> List[If_BottomFuncBtn]:
        controls:List[If_BottomFuncBtn] = []
        for btnIdx in en.BtmBtnIdx:
            controls.append(If_BottomFuncBtn(btnIdx))
        return controls
    
    def change_btn_properties(self, *dict_properties:Dict_BtmBtnProperties):
        for prop in dict_properties:
            for btn in self.controls:
                if not isinstance(btn, If_BottomFuncBtn): continue
                if btn.btmBtnIdx == prop.BTMBTNIDX:
                    log = btn.change_property(prop)
                    break


