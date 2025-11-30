import flet as ft
from pathlib import Path
import re
from typing import Final, Dict, List, Optional
from enum import Enum, IntEnum
import os

filePickers: Dict[Enum_FilePickerIdx, ft.FilePicker]
fileData: List[List[str]] = []
settingData: Dict[str, str] = {}
OUTPUUUUT_PATH:Path = Path('MakeCiSupportApp/outpuuuut.txt')

class Enum_TabIdx(IntEnum):
    FILE_PATH_SELECT = 0
    READ_DATA = 1
    BUILDER_LOG = 2
    BUILDER_RESULT = 3
    PLACE_HOLDER = 99
    #TAB_404 = 404



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
    def __init__(self, tabIdx:Enum_TabIdx, leftBtnClicked:ft.ControlEvent, text:str):
        super().__init__(
            width=150,
            height=40
        )
        self.workIdx = tabIdx
        self.on_click = leftBtnClicked

class Left_TabBtn_Tab0(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(Enum_TabIdx.FILE_PATH_SELECT, leftBtnClicked, "ファイル設定")
class Left_TabBtn_Tab1(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(Enum_TabIdx.READ_DATA, leftBtnClicked, "読取結果")
class Left_TabBtn_Tab2(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(Enum_TabIdx.BUILDER_LOG, leftBtnClicked, "Builderログ")
class Left_TabBtn_Tab3(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(Enum_TabIdx.BUILDER_RESULT, leftBtnClicked, "Builder動作完了")

#*ウィンドウ左側のタブ切り替え用のボタンを配置したコンテナ
#*引数にボタン動作を要求
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


class Enum_BtmBtnIdx(IntEnum):
    NEXT_TAB = 0
    EXIT_APP = 1
    OTHER_FUNC1 = 2
    OTHER_FUNC2 = 3
class Btm_TabFuncBtn(ft.FilledButton):
    def __init__(self, btmBtnClicked:ft.ControlEvent, text:str, workPlaceIdx:Enum_BtmBtnIdx):
        super().__init__(
            width=120,
            text=text
        )
        self.on_click = btmBtnClicked
        self.workPlaceIdx = workPlaceIdx

class BtmBtn_EXit(Btm_TabFuncBtn):
    def __init__(self):
        super().__init__(
            btmBtnClicked=lambda _: self.page.window.close(),
            text="ExitApp",
            workPlaceIdx=Enum_BtmBtnIdx.EXIT_APP
            )

class BtmBtn_Tab0_ReadCIF(Btm_TabFuncBtn):
    def __init__(self, btmBtnClicked: ft.ControlEvent):
        super().__init__(btmBtnClicked, "ReadCif", Enum_BtmBtnIdx.NEXT_TAB)
class BtmBtn_Tab0_ReadTXT(Btm_TabFuncBtn):
    def __init__(self, btmBtnClicked: ft.ControlEvent):
        super().__init__(btmBtnClicked, "ReadTXT", Enum_BtmBtnIdx.OTHER_FUNC1)
class BtmBtn_Tab1_SaveRun(Btm_TabFuncBtn):
    def __init__(self, btmBtnClicked: ft.ControlEvent):
        super().__init__(btmBtnClicked, "Save&Run", Enum_BtmBtnIdx.NEXT_TAB)
class BtmBtn_Tab1_Save(Btm_TabFuncBtn):
    def __init__(self, btmBtnClicked: ft.ControlEvent):
        super().__init__(btmBtnClicked, "Save", Enum_BtmBtnIdx.OTHER_FUNC1)
class BtmBtn_Tab1_Remove(Btm_TabFuncBtn):
    def __init__(self, btmBtnClicked: ft.ControlEvent):
        super().__init__(btmBtnClicked, "Remove", Enum_BtmBtnIdx.OTHER_FUNC2)
class BtmBtn_Tab2_Next(Btm_TabFuncBtn):
    def __init__(self, btmBtnClicked: ft.ControlEvent):
        super().__init__(btmBtnClicked, "Next", Enum_BtmBtnIdx.NEXT_TAB)
class BtmBtn_Tab2_Stop(Btm_TabFuncBtn):
    def __init__(self, btmBtnClicked: ft.ControlEvent):
        super().__init__(btmBtnClicked, "Stop", Enum_BtmBtnIdx.OTHER_FUNC1)

class Btm_BtnBar(ft.Row):
    def __init__(self, tabIdx:Enum_TabIdx):
        super().__init__(
            expand=1,
            alignment=ft.MainAxisAlignment.END
        )
        self.tabIdx = tabIdx
        self.controls:List[Btm_TabFuncBtn] = []

    def add_btmBtn(self, btmBtn:Btm_TabFuncBtn):
        newBtnList:List[Btm_TabFuncBtn] = []
        for btn in self.controls:
            if btmBtn.workPlaceIdx == btn.workPlaceIdx: continue
            elif btmBtn.workPlaceIdx < btn.workPlaceIdx:
                newBtnList.append(btmBtn)
            newBtnList.append(btn)
        self.controls = newBtnList


class Enum_FilePickerIdx(IntEnum):
    BUILDER_PICK = 0
    CIF_PICK = 1
    OUTPUT_PICK = 2
    OUTPUT_SAVE = 3

    def get_fileType(self)->str:
        match self.name:
            case 'BUILDER_PICK':
                return "exe"
            case 'CIF_PICK':
                return "cif"
            case 'OUTPUT_PICK':
                return "txt"
            case 'OUTPUT_SAVE':
                return "txt"

class Tab_FilePicker_Bar(ft.Row):
    def __init__(self, filePickerIdx:Enum_FilePickerIdx):
        super().__init__(
            spacing=0
        )
        self.filePickerIdx = filePickerIdx
        self.filePickeeeer = filePickers[self.filePickerIdx]
        self.filePickeeeer.on_result = self.filePicker_event
        self.filePath:Path

        self.pathTxtf = ft.TextField(expand=9, dense=True, on_blur=self.txtf_onBlur_event)
        self.controls = [
            self.pathTxtf,
            ft.FilledButton(
                expand=1,
                text="File",
                on_click=lambda _: self.filePickeeeer.pick_files(allowed_extensions=[self.filePickerIdx.get_fileType()])
            )
        ]

    def path_change(self, changedStr:Optional[str]=None):
        if changedStr is None:
            self.pathTxtf.value = ""
        else:
            self.pathTxtf.value = changedStr.replace(os.sep, '/').strip('"')
        value = Path(self.pathTxtf.value)
        if Path.exists(value):
            print(f"Selected files:name={value.name}")
            print(f"Selected files:{value.resolve()}")
        else:
            print("is not filePath")

    def txtf_onBlur_event(self, e:ft.ControlEvent):
        self.path_change(e.control.value)
        self.update()
    def filePicker_event(self,e: ft.FilePickerResultEvent):
        if e.files:
            self.path_change(e.files[0].path)
        self.update()

class Tab0_FPBar_Builder(Tab_FilePicker_Bar):
    def __init__(self):
        super().__init__(filePickerIdx=Enum_FilePickerIdx.BUILDER_PICK)
        self.pathTxtf.hint_text = "Builder.exe Path"
class Tab0_FPBar_CIF(Tab_FilePicker_Bar):
    def __init__(self):
        super().__init__(filePickerIdx=Enum_FilePickerIdx.CIF_PICK)
        self.pathTxtf.hint_text = "CIF File Path"
class Tab0_FPBar_Output(Tab_FilePicker_Bar):
    def __init__(self):
        super().__init__(filePickerIdx=Enum_FilePickerIdx.OUTPUT_PICK)
        self.pathTxtf.hint_text = "Output File Path"


class Cn_TabContainer(ft.Container):
    def __init__(self, tabIdx:Enum_TabIdx, defVisible:bool):
        super().__init__(
            expand=10,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            visible=defVisible
        )
        self.tabIdx = tabIdx

class Cn_Tab99_PlaceHoldeeeer(Cn_TabContainer):
    def __init__(self):
        super().__init__(tabIdx=Enum_TabIdx.PLACE_HOLDER, defVisible=True)
        self.content = ft.Placeholder(color=ft.Colors.random())

class Cn_Tab0_FilePathSelect(Cn_TabContainer):
    def __init__(self):
        super().__init__(tabIdx=Enum_TabIdx.FILE_PATH_SELECT, defVisible=True)
        self.pickBuilder = Tab0_FPBar_Builder()
        self.pickCIF = Tab0_FPBar_CIF()
        self.pickOutput = Tab0_FPBar_Output()

        self.content = ft.Column([
            ft.Text("Builder Path"),
            self.pickBuilder,
            ft.Text("CIF File Path"),
            self.pickCIF,
            ft.Text("Output File Path"),
            self.pickOutput
        ])

        if "builder_path" in settingData:
            self.pickBuilder.path_change(settingData['builder_path'])





