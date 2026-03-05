import flet as ft
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import os
from logging import LogRecord, Logger, Handler

import mdEnums as en

class Data_BtmBtnProperties():
    def __init__(self,
                btm_btn_idx:en.BtmBtnIdx,
                visible:bool=True,
                disabled:bool=True,
                text:Optional[str]=None,
                on_click:ft.OptionalControlEventCallable=None
        ):
        self.BTMBTNIDX = btm_btn_idx
        self.VISIBLE = visible
        self.DISABLED = disabled
        if text is None: newTxt = self.BTMBTNIDX.get_btn_def_text()
        else: newTxt = text
        self.TEXT = newTxt
        if on_click is None: new_click = self._btmBtn_dflt_event
        else: new_click = on_click
        self.ON_CLICK = new_click
    
    def change_props(self,
                    btn_idx:Optional[en.BtmBtnIdx]=None,
                    visible:bool=True,
                    disabled:bool=True,
                    text:Optional[str]=None,
                    on_click:ft.OptionalControlEventCallable=None,
                ) -> Data_BtmBtnProperties:
        if btn_idx is None: newIdx = self.BTMBTNIDX
        else: newIdx = btn_idx
        if text is None: newText = self.BTMBTNIDX.get_btn_def_text()
        else: newText = text
        if on_click is None: new_click = self._btmBtn_dflt_event
        else: new_click = on_click
        return Data_BtmBtnProperties(
            btm_btn_idx=newIdx,
            visible=visible,
            disabled=disabled,
            text=newText,
            on_click=new_click
        )

    def change_prop_click(self, on_click:ft.OptionalControlEventCallable=None) -> Data_BtmBtnProperties:
        new_click = on_click
        if new_click is None: new_click = self._btmBtn_dflt_event
        return Data_BtmBtnProperties(
            self.BTMBTNIDX,
            self.VISIBLE,
            self.DISABLED,
            self.TEXT,
            new_click
        )

    def _btmBtn_dflt_event(self, e:ft.ControlEvent):
        raise ValueError("ボタンに機能が付加されていないにもかかわらずクリックできる状態です")


class If_BottomFuncBtn(ft.FilledButton):
    def __init__(self, btm_btn_idx:en.BtmBtnIdx):
        super().__init__(
            width=120,
        )
        self.btmBtnIdx = btm_btn_idx
        self.text = self.btmBtnIdx.get_btn_def_text()

    def change_property(self, data_properties:Data_BtmBtnProperties) -> Tuple[str, ...]:
        prop = data_properties
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

class If_FilePickerBar(ft.Row):
    def __init__(self, filePickerIdx:en.FilePickerIdx):
        super().__init__(
            spacing=0
        )
        self._pickIdx = filePickerIdx
        self._fileType = self._pickIdx.get_fileType()
        self._filePicker:ft.FilePicker
        self._pickedPath:Optional[Path] = None

        self._pathTxtf = ft.TextField(
            expand=9,
            dense=True,
            hint_text=self._pickIdx.value,
        )
        self._pickBtn = ft.FilledButton(
            expand=1,
            text="File",
        )
        self.controls = [
            self._pathTxtf,
            self._pickBtn,
        ]

    def set_init(self) -> None:
        raise ValueError("this method is interface. please override.")

    def get_path(self) -> Optional[Path]:
        if self._pickedPath is None: return None
        return Path(self._pickedPath)

    def path_change(self, new_path_str:str) -> None:
        raise ValueError("this method is interface. please override.")

    def _pick_event(self, e:ft.FilePickerResultEvent):
        if e.files: self.path_change(e.files[0].path)
        self.update()
    def _txtf_on_blur_event(self, e:ft.ControlEvent):
        self.path_change(e.control.value)
        self.update()
    def _pick_btn_event(self, e:ft.ControlEvent):
        self._filePicker.pick_files(allowed_extensions=[self._fileType])

class Data_BtmBtnPropsDict(Dict[en.BtmBtnIdx, Data_BtmBtnProperties]):
    def __init__(self):
        super().__init__()
class Itf_TabContainer(ft.Container):
    def __init__(self, tab_idx:en.TabIdx, dflt_visible:bool):
        super().__init__(
            expand=True,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.all(1, ft.Colors.random()),
            visible=dflt_visible
        )
        self.tabIdx = tab_idx
        self.controls:List[ft.Control] = []
        #self._mainFrame: ft.Container
        self._dictProps:Data_BtmBtnPropsDict

    def set_init(self) -> Tuple[str, ...]:
        self._dictProps = self._set_btmBtn_prop()
        #self._mainFrame = main_frame
        self.update()
        return (
            f'{self.tabIdx.get_tab_name()} is initialized.',
        )

    def _set_btmBtn_prop(self) -> Data_BtmBtnPropsDict:
        props = Data_BtmBtnPropsDict()
        for btnLabel in en.BtmBtnIdx:
            props[btnLabel] = Data_BtmBtnProperties(
                btm_btn_idx=btnLabel
            )
        props[en.BtmBtnIdx.EXIT_APP] = props[en.BtmBtnIdx.EXIT_APP].change_props(
            disabled=False,
            on_click=self._btmBtn_exit_event
        )
        return props

    def _btmBtn_exit_event(self, e:ft.ControlEvent):
        self.page.window.close()

    def get_dict_props(self) -> Data_BtmBtnPropsDict:
        return self._dictProps
class If_LogView(ft.ListView):
    def __init__(self):
        super().__init__(
            expand=True,
            auto_scroll=True,
            spacing=0
        )
    
    def log_write(self, message:str, level:str):
        if not message.strip(): return

        colorMap = {
            "DEBUG": ft.Colors.GREY,
            "INFO": ft.Colors.GREY_300,
            "WARNING": ft.Colors.YELLOW,
            "ERROR": ft.Colors.RED,
            "CRITICAL": ft.Colors.RED_400,
        }

        self.controls.append(
            ft.Text(
                value=message.rstrip(),
                font_family='Consoals',
                size=14,
                color=colorMap.get(level, ft.Colors.BLUE_50),
                selectable=True,
            )
        )
        self.update()

class If_ViewLogHandler(Handler):
    def __init__(self, terminal_view:If_LogView):
        super().__init__()
        self.terminalView = terminal_view

    def emit(self, record: LogRecord):
        msg = self.format(record)
        self.terminalView.log_write(msg, record.levelname)

class If_Txtf_CellData(ft.TextField):
    def __init__(self, cell_info_label:en.CellInfoLbl, label:str, hint_text:str, read_only:bool=True):
        super().__init__(
            expand=1,
            dense=True,
            label=label,
            hint_text=hint_text,
            read_only=read_only
        )
        self.cellDataLbl = cell_info_label


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
class Itf_Left_TabBtn(ft.FilledButton):
    #* tabIdx -> タブの列挙クラス，leftBtnClicked -> タブ変更用のメソッドを要求
    def __init__(self, tabIdx:en.TabIdx):
        super().__init__(
            width=150,
            height=40
        )
        self.tabIdx = tabIdx
        self.text = self.tabIdx.get_tab_name()

    def set_init(self, on_click:ft.OptionalControlEventCallable) -> Tuple[str, ...]:
        self.on_click = on_click
        return (f'TabBtn({self.text}) is initialized.',)

#* 具象ボタンクラスを収納するコンテナ
#* 具象ボタンたちに与える動作メソッドはこのクラスの引数に要求
class Itf_Left_TabChangeBar(ft.Container):
    def __init__(self):
        super().__init__(
            border=ft.border.all(1, ft.Colors.BLACK),
            padding=10,
            expand=1,
            bgcolor=ft.Colors.GREY_300
        )

        self.controls = self._add_contents()
        self.content = ft.Column(
            height=520,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            expand_loose=True,
            controls=self.controls
        )

    def _add_contents(self) -> List[ft.Control]:
        controls:List[ft.Control] = []
        for tabIdx in en.TabIdx:
            if tabIdx.name == 'PLACE_HOLDER': continue
            controls.append(Itf_Left_TabBtn(tabIdx))
            controls.append(Left_DownMarkTxt())
        controls.pop()
        return controls
    
    def set_init(self, left_btn_clicked:ft.OptionalControlEventCallable) -> Tuple[str, ...]:
        log = ("Left_TabChangeBar init -->",)
        for cont in self.controls:
            if not isinstance(cont, Itf_Left_TabBtn): continue
            log += cont.set_init(left_btn_clicked)
        log += ("<-- end",)
        return log

