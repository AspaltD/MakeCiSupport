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
                ):
        if btn_idx is None: newIdx = self.BTMBTNIDX
        else: newIdx = btn_idx
        if text is None: newText = self.BTMBTNIDX.get_btn_def_text()
        else: newText = text
        if on_click is None: new_click = self._btmBtn_dflt_event
        else: new_click = on_click
        self = Data_BtmBtnProperties(
            btm_btn_idx=newIdx,
            visible=visible,
            disabled=disabled,
            text=newText,
            on_click=new_click
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
        self.pickIdx = filePickerIdx
        self.filePicker:ft.FilePicker
        self.pickedPath:Optional[Path] = None

        self.pathTxtf = ft.TextField(
            expand=9,
            dense=True,
            hint_text=self.pickIdx.value,
        )
        self.pickBtn = ft.FilledButton(
            expand=1,
            text="File",
        )
        self.controls = [
            self.pathTxtf,
            self.pickBtn,
        ]

    def set_init(self, file_picker:ft.FilePicker, path_from_setting:Optional[str]) -> Tuple[str, ...]:
        self.filePicker = file_picker
        self.filePicker.on_result = self._pick_event
        self.pathTxtf.on_blur = self._txtf_on_blur_event
        self.pickBtn.on_click = self._pick_btn_event
        self.path_change(path_from_setting)
        return (
            f'PickerBar_{self.pickIdx.value}_initialize -->',
            f'  fileType    -> {self.pickIdx.get_fileType()}',
            f'  pickedName  -> {self.get_path_name()}',
            f'  pickedPath  -> {str(self.get_path())}',
            "<--",
        )

    def get_path(self) -> Optional[Path]:
        if self.pickedPath is None: return None
        if not self._check_txtf_path(): return None
        return Path(self.pickedPath)
    
    def get_path_name(self) -> str:
        if self.pickedPath is None: return "not file picked"
        return self.pickedPath.name
    
    def _check_txtf_path(self) -> bool:
        path = self.pickedPath
        if path is None: return False
        if not path.is_file(): return False
        if path.suffix[1:] != self.pickIdx.get_fileType(): return False
        return True

    def path_change(self, new_path_str:Optional[str]=None) -> Tuple[str, ...]:
        newPathStr = new_path_str
        if newPathStr is None: newPathStr = "None"
        newPathStr = newPathStr.replace(os.sep, '/').strip('"')
        newPath = Path(newPathStr)
        if newPath.is_file():
            self.pathTxtf.value = str(newPath.resolve())
            self.pathTxtf.error_text = None
            self.pickedPath = newPath
        else:
            self.pathTxtf.value = ""
            self.pathTxtf.error_text = "is not true path"
            self.pickedPath = None
        return (
            f'PickerBar_{self.pickIdx.value}_path_changed -->',
            f'  pickedName  -> {self.get_path_name()}',
            f'  pickedPath  -> {str(self.get_path())}',
            "<--",
        )

    def _pick_event(self, e:ft.FilePickerResultEvent):
        if e.files: self.path_change(e.files[0].path)
        self.update()
    def _txtf_on_blur_event(self, e:ft.ControlEvent):
        self.path_change(e.control.value)
        self.update()
    def _pick_btn_event(self, e:ft.ControlEvent):
        self.filePicker.pick_files(allowed_extensions=[self.pickIdx.get_fileType()])

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
        props[en.BtmBtnIdx.EXIT_APP].change_props(
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
