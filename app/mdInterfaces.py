import flet as ft
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import os
from logging import Logger

import mdEnums as en
import frmAppWindow as frm

class Data_BtmBtnProperties():
    def __init__(self,
                btm_btn_idx:en.BtmBtnIdx,
                visible:bool,
                disabled:bool,
                text:str,
                on_click:ft.OptionalControlEventCallable
        ):
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

class If_TabContainer(ft.Container):
    class Dict_BtmBtnProps(Dict[en.BtmBtnIdx, Data_BtmBtnProperties]):
        def __init__(self, parent_tab:If_TabContainer):
            tab = parent_tab
            self[en.BtmBtnIdx.EXIT_APP] = Data_BtmBtnProperties(
                btm_btn_idx=en.BtmBtnIdx.EXIT_APP,
                visible=True,
                disabled=True,
                text=en.BtmBtnIdx.EXIT_APP.get_btn_def_text(),
                on_click=tab._btmBtn_exit_event
            )
            self[en.BtmBtnIdx.NEXT_TAB] = Data_BtmBtnProperties(
                btm_btn_idx=en.BtmBtnIdx.NEXT_TAB,
                visible=True,
                disabled=False,
                text=en.BtmBtnIdx.NEXT_TAB.get_btn_def_text(),
                on_click=tab._btmBtn_dflt_event
            )
            self[en.BtmBtnIdx.OTHER_FUNC1] = Data_BtmBtnProperties(
                btm_btn_idx=en.BtmBtnIdx.OTHER_FUNC1,
                visible=True,
                disabled=False,
                text=en.BtmBtnIdx.OTHER_FUNC1.get_btn_def_text(),
                on_click=tab._btmBtn_dflt_event
            )
            self[en.BtmBtnIdx.OTHER_FUNC2] = Data_BtmBtnProperties(
                btm_btn_idx=en.BtmBtnIdx.OTHER_FUNC2,
                visible=True,
                disabled=False,
                text=en.BtmBtnIdx.OTHER_FUNC2.get_btn_def_text(),
                on_click=tab._btmBtn_dflt_event
            )

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
        self._appLogger:Logger
        self._dictProps:Dict[en.BtmBtnIdx, Data_BtmBtnProperties]

    def set_init(self, app_logger:Logger):
        self._appLogger = app_logger
        self._dictProps = self.Dict_BtmBtnProps(self)
        self._appLogger.info(f'{self.tabIdx.get_tab_name()} is initialized.')

    def _btmBtn_dflt_event(self, e:ft.ControlEvent):
        self._appLogger.error("This is BtmBtn's default event.")
        raise ValueError("ボタンに機能が付加されていないにもかかわらずクリックできる状態です")
    def _btmBtn_exit_event(self, e:ft.ControlEvent):
        self.page.window.close()

class Tab99_PlaceHoldeeeer(If_TabContainer):
    def __init__(self):
        super().__init__(en.TabIdx.PLACE_HOLDER, True)
        self.content = ft.Placeholder(color=ft.Colors.random())

class Tab0_BuilderPathSelect(If_TabContainer):
    def __init__(self):
        super().__init__(en.TabIdx.FILE_PATH_SELECT, True)
        self.pickBuilder = If_FilePickerBar(en.FilePickerIdx.BUILDER_PICK)
        self.pickCIF = If_FilePickerBar(en.FilePickerIdx.CIF_PICK)
        self.pickTXT = If_FilePickerBar(en.FilePickerIdx.OUTPUT_PICK)

        self.controls = [
            ft.Text("Builder Path"),
            self.pickBuilder,
            ft.Text("CIF File Path"),
            self.pickCIF,
            ft.Text("Text File Path"),
            self.pickTXT,
        ]
        self.content = ft.Column(controls=self.controls)

    def set_init(self, app_logger: Logger):
        super().set_init(app_logger)
        for cont in self.controls:
            if not isinstance(cont, If_FilePickerBar): continue
            cont.set_init()
        self._dictProps[]
