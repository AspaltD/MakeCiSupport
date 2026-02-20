import flet as ft
from typing import List,Dict
from pathlib import Path
import os

import enEnums as en


#*タブ変更欄でボタンの間に置く用のテキスト
class _Left_txt_DownMark(ft.Text):
    def __init__(self, value:str="▼"):
        super().__init__(
            width=180,
            text_align=ft.TextAlign.CENTER,
            value=value
        )

#?タブ変更欄のタブとリンクするボタン
class _Left_btn_TabChange(ft.FilledButton):
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
            controls.append(_Left_btn_TabChange(_tabIdx))
            controls.append(_Left_txt_DownMark())
        controls.pop()
        return controls

#?ボトムボタンの属性のうちタブに依存するものを抜き出したもの
#!ボトムボタンをタブコンテナの配下にするため使わない可能性大
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
class _Btm_btn_TabFunc(ft.FilledButton):
    def __init__(self, btm_btn_idx:en.BtmBtnIdx):
        super().__init__(
            width=120,
            disabled=True,
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

#?タブ固有ボタンたち。すべて変数として生成してるのでボタンに追加があったら任意で追加する。
class Btm_row_FuncBtns(ft.Row):
    def __init__(self):
        super().__init__(
            expand=1,
            alignment=ft.MainAxisAlignment.END,
        )
        self.btnFunc2 = _Btm_btn_TabFunc(en.BtmBtnIdx.OTHER_FUNC2)
        self.btnFunc1 = _Btm_btn_TabFunc(en.BtmBtnIdx.OTHER_FUNC1)
        self.btnExit = _Btm_btn_TabFunc(en.BtmBtnIdx.EXIT_APP)
        self.btnNext = _Btm_btn_TabFunc(en.BtmBtnIdx.NEXT_TAB)
        self.controls = [
            self.btnFunc2,
            self.btnFunc1,
            self.btnExit,
            self.btnNext
        ]

#*タブのコンテンツたちを配置するためのコンテナ。
#*以前の構造と違ってこいつには容器としての定義しか持たせてない。
class _Rgt_box_TabContainer(ft.Container):
    def __init__(self):
        super().__init__(
            expand=10,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.all(1, ft.Colors.random())
        )
        self.tabItems:List[ft.Control] = []

#?Beta6.0から新たにタブコンテンツと下部ボタンたちを包括した右側パーツとして定義。
#?タブごとに下部ボタンを持たせることで，オブジェクトの増加と引き換えに構造の簡略化を図る目的。
#?タブの固有機能はここに持たせる。
class _Rgt_col_TabBase(ft.Column):
    def __init__(self, tab_idx:en.TabIdx, dflt_visible:bool=False):
        super().__init__(
            expand=True,
            spacing=2,
            visible=dflt_visible
        )
        self.tabIdx = tab_idx
        self.tabCont = _Rgt_box_TabContainer()
        self.btmBtns = Btm_row_FuncBtns()
        self.controls = [
            self.tabCont,
            self.btmBtns
        ]

#*配置スペースを維持するためのダミータブ。常に最背面に表示。
class Rgt_tab_99_PlaceHolder(_Rgt_col_TabBase):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.PLACE_HOLDER, dflt_visible=True)
        self.tabCont.content = ft.Placeholder(color=ft.Colors.random())

#?ファイル選択用のコンテンツ群。
#?外部で定義が必要なFilePickerはセットメソッドで任意に指定が必要。FilePicker周りの機能以外は単独でも動く。
class Rgt_row_FilePickerBar(ft.Row):
    def __init__(self, file_picker_idx:en.FilePickerIdx):
        super().__init__(
            spacing=0
        )
        self.pickerIdx = file_picker_idx
        self._fileType = self.pickerIdx.get_file_type()
        self._filePicker:ft.FilePicker
        self.pickedPath:Path

        self.txtfPath = ft.TextField(
            expand=9,
            dense=True,
            hint_text=self.pickerIdx.value,
            on_blur=self._txtf_on_blur_event
        )
        self._btnPick = ft.FilledButton(
            expand=1,
            text="File",
        )
        self.controls = [
            self.txtfPath,
            self._btnPick,
        ]

    def set_picker_init(self, file_picker:ft.FilePicker):
        self._filePicker = file_picker
        self._filePicker.on_result = self._picked_event
        self._btnPick.on_click = self._btn_on_click_event

    def path_change(self, new_path_str:str):
        if not new_path_str.strip(): self._path_error_msg()
        newPath = Path(new_path_str.replace(os.sep, '/').strip().strip('"'))
        if newPath.is_file() and newPath.suffix[1:] == self._fileType:
            self.pickedPath = newPath
            self.txtfPath.value = str(newPath.resolve())
            self.txtfPath.error_text = None
        else:
            self._path_error_msg()
        self.update()

    def _path_error_msg(self):
        try:
            del self.pickedPath
        except:
            pass
        self.txtfPath.error_text = "is not file"

    def _picked_event(self, e:ft.FilePickerResultEvent):
        if e.files: self.path_change(e.files[0].path)
        self.update()

    def _txtf_on_blur_event(self, e:ft.ControlEvent):
        self.path_change(e.control.value)

    def _btn_on_click_event(self, e:ft.ControlEvent):
        self._filePicker.pick_files(allowed_extensions=[self._fileType])

class Rgt_tab_0_CIFSelect(_Rgt_col_TabBase):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.CIF_SELECT, dflt_visible=True)
        self.pickBuilder = Rgt_row_FilePickerBar(en.FilePickerIdx.PICK_BUILDER)
        self.pickCIF = Rgt_row_FilePickerBar(en.FilePickerIdx.PICK_CIF)
        self.pickTXT = Rgt_row_FilePickerBar(en.FilePickerIdx.PICK_TXT)

        self.tabCont.content = ft.Column(
            controls=[
                ft.Text("Builder Path"),
                self.pickBuilder,
                ft.Text("CIF File Path"),
                self.pickCIF,
                ft.Text("Text File Path"),
                self.pickTXT,
            ]
        )
        for _btmBtn in self.btmBtns.controls:
            if not isinstance(_btmBtn, _Btm_btn_TabFunc): continue
            match _btmBtn.btmBtnIdx.name:
                case 'EXIT_APP':
                    _btmBtn.visible = True
                    _btmBtn.disabled = False
                case 'NEXT_TAB':
                    _btmBtn.visible = True
                    _btmBtn.disabled = False
                    _btmBtn.text = "ReadCIF"
                case 'OTHER_FUNC1':
                    _btmBtn.visible = True
                    _btmBtn.disabled = False
                    _btmBtn.text = "ReadTXT"
                case 'OTHER_FUNC2':
                    _btmBtn.visible = False

