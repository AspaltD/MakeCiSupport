import flet as ft
from pathlib import Path
from typing import Optional, Tuple
import os

import mdEnums as en
import frmAppWindow as frm

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

    def set_init(self, file_picker:ft.FilePicker, setting_data:frm.SettingData) -> Tuple[str, ...]:
        self.filePicker = file_picker
        self.filePicker.on_result = self._pick_event
        self.pathTxtf.on_blur = self._txtf_on_blur_event
        self.pickBtn.on_click = self._pick_btn_event
        label = self.pickIdx.get_setting_label()
        if label is None: self.path_change()
        else: self.path_change(setting_data[label])
        return (
            f'PickerBar_{self.pickIdx.value}_initialize -->',
            f'  fileType    -> {self.pickIdx.get_fileType()}',
            f'  pickedName  -> {self.get_path_name()}',
            f'  pickedPath  -> {str(self.get_path())}',
            "<--",
        )

    def get_path(self) -> Optional[Path]:
        if self.pickedPath is None: return None
        return Path(self.pickedPath)
    
    def get_path_name(self) -> str:
        if self.pickedPath is None: return "not file picked"
        return self.pickedPath.name
    
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