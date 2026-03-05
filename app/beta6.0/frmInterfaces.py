import flet as ft
from typing import List,Dict,Optional
from pathlib import Path
import os
from logging import LogRecord, Handler

import enEnums as en


#*タブ変更欄でボタンの間に置く用のテキスト
class _Left_txt_DownMark(ft.Text):
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
        self.tanBtns = self._add_controls()
        self.content = ft.Column(
            height=520,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            expand_loose=True,
            controls=self.tanBtns
        )

    def _add_controls(self) -> List[ft.Control]:
        controls:List[ft.Control] = []
        for _tabIdx in en.TabIdx:
            if _tabIdx.name == 'PLACE_HOLDER': continue
            controls.append(Left_btn_TabChange(_tabIdx))
            controls.append(_Left_txt_DownMark())
        controls.pop()
        return controls

    def set_tabBtn_on_click(self, left_tabBtn_on_click_event:ft.OptionalControlEventCallable):
        for _tabBtn in self.tanBtns:
            if not isinstance(_tabBtn, Left_btn_TabChange): continue
            _tabBtn.on_click = left_tabBtn_on_click_event


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

#?タブの下部に置く固有の機能を持たせるためのボタン。
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
        self.btnExit.on_click = self.exit_event

    def exit_event(self, e:ft.ControlEvent):
        self.page.window.close()

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
        #self.tabItems:List[ft.Control] = []

#*Beta6.0から新たにタブコンテンツと下部ボタンたちを包括した右側パーツとして定義。
#*タブごとに下部ボタンを持たせることで，オブジェクトの増加と引き換えに構造の簡略化を図る目的。
#*タブの固有機能はここに持たせる。
class Rgt_col_TabBase(ft.Column):
    def __init__(self, tab_idx:en.TabIdx, dflt_visible:bool=False):
        super().__init__(
            expand=True,
            spacing=2,
            visible=dflt_visible
        )
        self.tabIdx = tab_idx
        self.tabItems:List[ft.Control] = []
        self.tabCont = _Rgt_box_TabContainer()
        self.btmBtns = Btm_row_FuncBtns()
        self.controls = [
            self.tabCont,
            self.btmBtns
        ]

#?配置スペースを維持するためのダミータブ。常に最背面に表示。
class Rgt_tab_99_PlaceHolder(Rgt_col_TabBase):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.PLACE_HOLDER, dflt_visible=True)
        self.tabCont.content = ft.Placeholder(color=ft.Colors.random())
        for _btmBtn in self.btmBtns.controls:
            if not isinstance(_btmBtn, _Btm_btn_TabFunc): continue
            match _btmBtn.btmBtnIdx.name:
                case _:
                    _btmBtn.visible = False


#*ファイル選択用のコンテンツ群。
#*外部で定義が必要なFilePickerはセットメソッドで任意に指定が必要。FilePicker周りの機能以外は単独でも動く。
class Tab_row_FilePickerBar(ft.Row):
    def __init__(self, file_picker_idx:en.FilePickerIdx):
        super().__init__(
            spacing=0
        )
        self.pickerIdx = file_picker_idx
        self._fileType = self.pickerIdx.get_file_type()
        self._filePicker:ft.FilePicker
        self.pickedPath:Optional[Path] = None

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
        self.pickedPath = None
        self.txtfPath.error_text = "is not file"

    def _picked_event(self, e:ft.FilePickerResultEvent):
        if e.files: self.path_change(e.files[0].path)
        self.update()

    def _txtf_on_blur_event(self, e:ft.ControlEvent):
        self.path_change(e.control.value)

    def _btn_on_click_event(self, e:ft.ControlEvent):
        self._filePicker.pick_files(allowed_extensions=[self._fileType])

#*タブ0。CIFファイル等を選ぶ。
class Rgt_tab_0_CIFSelect(Rgt_col_TabBase):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.CIF_SELECT, dflt_visible=True)
        self.pickBuilder = Tab_row_FilePickerBar(en.FilePickerIdx.PICK_BUILDER)
        self.pickCIF = Tab_row_FilePickerBar(en.FilePickerIdx.PICK_CIF)
        self.pickTXT = Tab_row_FilePickerBar(en.FilePickerIdx.PICK_TXT)

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

#?タブ1の格子情報用のテキストフィールド。
class Tab_txtf_CellData(ft.TextField):
    def __init__(self, cell_data_lbl:en.CellDataLbl, expand:int=1, read_only:bool=True):
        super().__init__(
            expand=expand,
            dense=True,
            read_only=read_only,
        )
        self.cellDataLbl = cell_data_lbl
        self.label = self.cellDataLbl.value

#?タブ1。読み取った結晶の情報のプレビュー。
class Rgt_tab_1_CIFPreview(Rgt_col_TabBase):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.CIF_PREVIEW)
        self.dataName = Tab_txtf_CellData(en.CellDataLbl.DATA_NAME, read_only=False)
        self.spaceGItNum = Tab_txtf_CellData(en.CellDataLbl.SPACE_G_IT_NUM)
        self.spaceGName = Tab_txtf_CellData(en.CellDataLbl.SPACE_G_NAME)
        self.cellLenA = Tab_txtf_CellData(en.CellDataLbl.CELL_LEN_A)
        self.cellLenB = Tab_txtf_CellData(en.CellDataLbl.CELL_LEN_B)
        self.cellLenC = Tab_txtf_CellData(en.CellDataLbl.CELL_LEN_C)
        self.cellAngleA = Tab_txtf_CellData(en.CellDataLbl.CELL_ANGLE_A)
        self.cellAngleB = Tab_txtf_CellData(en.CellDataLbl.CELL_ANGLE_B)
        self.cellAngleC = Tab_txtf_CellData(en.CellDataLbl.CELL_ANGLE_C)
        self.cellVolume = Tab_txtf_CellData(en.CellDataLbl.CELL_VOLUME)
        self.tabItems = [
            self.dataName, self.spaceGItNum, self.spaceGName, self.cellLenA,
            self.cellLenB, self.cellLenC, self.cellAngleA, self.cellAngleB,
            self.cellAngleC, self.cellVolume,
        ]
        self._cellDataTxtfBase = ft.Column(
            expand=2,
            controls=[
                self.dataName,
                ft.Row(
                    spacing=0,
                    controls=[self.cellLenA, self.cellLenB, self.cellLenC]
                ),
                ft.Row(
                    spacing=0,
                    controls=[self.cellAngleA, self.cellAngleB, self.cellAngleC]
                ),
                ft.Row(
                    spacing=0,
                    controls=[self.spaceGItNum, self.spaceGName, self.cellVolume]
                ),
            ]
        )

        self.atomsTable = ft.DataTable(
            border=ft.border.all(1, ft.Colors.BLACK),
            show_checkbox_column=True,
            column_spacing=24,
            columns=[
                ft.DataColumn(ft.Text("Atom")),
                ft.DataColumn(ft.Text(" Idx1 "),heading_row_alignment=ft.MainAxisAlignment.CENTER,numeric=True),
                ft.DataColumn(ft.Text(" Idx2 "),heading_row_alignment=ft.MainAxisAlignment.CENTER,numeric=True),
                ft.DataColumn(ft.Text("  X  "),heading_row_alignment=ft.MainAxisAlignment.CENTER,numeric=True),
                ft.DataColumn(ft.Text("  Y  "),heading_row_alignment=ft.MainAxisAlignment.CENTER,numeric=True),
                ft.DataColumn(ft.Text("  Z  "),heading_row_alignment=ft.MainAxisAlignment.CENTER,numeric=True),
                ft.DataColumn(ft.Text("Occ."),numeric=True)
            ],
            rows=[]
        )
        self._atomsTableBase = ft.Column(
            expand=3,
            controls=[self.atomsTable],
            scroll=ft.ScrollMode.ALWAYS
        )

        self.tabCont.content = ft.Column(
            controls=[
                self._cellDataTxtfBase,
                self._atomsTableBase
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
                    _btmBtn.text = "Save&Go"
                case 'OTHER_FUNC1':
                    _btmBtn.visible = True
                    _btmBtn.disabled = False
                    _btmBtn.text = "Save"
                case 'OTHER_FUNC2':
                    _btmBtn.visible = True
                    _btmBtn.disabled = False
                    _btmBtn.text = "Remove"

#*タブ2のアプリログを表示するリストビュー
class Tab_listV_AppLog(ft.ListView):
    def __init__(self):
        super().__init__(
            expand=True,
            auto_scroll=True,
            spacing=0,
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

#*リストビュー用のログハンドラー。
class Tab_ViewLogHandler(Handler):
    def __init__(self, terminal_view:Tab_listV_AppLog):
        super().__init__()
        self.terminalView = terminal_view

    def emit(self, record: LogRecord):
        msg = self.format(record)
        self.terminalView.log_write(msg, record.levelname)

#*タブ2。アプリのログの表示先。
class Rgt_tab_2_AppLogs(Rgt_col_TabBase):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.APP_LOG, dflt_visible=True)
        self.tabCont.bgcolor = ft.Colors.BLACK
        self.listV_appLog = Tab_listV_AppLog()
        self.tabCont.content = self.listV_appLog

        for _btmBtn in self.btmBtns.controls:
            if not isinstance(_btmBtn, _Btm_btn_TabFunc): continue
            match _btmBtn.btmBtnIdx.name:
                case 'EXIT_APP':
                    _btmBtn.visible = False
                    _btmBtn.disabled = True
                case 'NEXT_TAB':
                    _btmBtn.visible = False
                    _btmBtn.disabled = False
                    _btmBtn.text = "Stop"
                case 'OTHER_FUNC1':
                    _btmBtn.visible = False
                case 'OTHER_FUNC2':
                    _btmBtn.visible = False

#?タブ3。Builderの実行終了後画面。
class Rgt_tab_3_BuilderResult(Rgt_col_TabBase):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.BUILDER_RESULT)
        self.txtf_cifName = ft.TextField(dense=True, read_only=True, max_lines=3)
        self.txtf_savePath = ft.TextField(dense=True, read_only=True, max_lines=3)
        self.txtf_runtime = ft.TextField(dense=True, read_only=True)

        self.tabCont.content = ft.Column(
            expand=True,
            controls=[
                ft.Text("CellData_file_name"),
                self.txtf_cifName,
                ft.Text("Saved_file_path"),
                self.txtf_savePath,
                ft.Text("Builder_run_time"),
                self.txtf_runtime,
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
                    _btmBtn.disabled = True
                case 'OTHER_FUNC1':
                    _btmBtn.visible = False
                case 'OTHER_FUNC2':
                    _btmBtn.visible = False

    def txtf_value_clear(self):
        self.txtf_cifName.value = ''
        self.txtf_savePath.value = ''
        self.txtf_runtime.value = ''


#*タブ4。GJF作成用のMIファイル選択と基礎となるGJFの選択
class Rgt_tab_4_MISelect(Rgt_col_TabBase):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.MI_SELECT)
        self.pickMI = Tab_row_FilePickerBar(en.FilePickerIdx.PICK_MI)
        self.pickGJF = Tab_row_FilePickerBar(en.FilePickerIdx.PICK_GJF)
        self.listV_baseGJF = ft.ListView(
            expand=True,
            auto_scroll=True,
            spacing=0,
            controls=[],
        )
        self.cont_viewBase = ft.Container(
            expand=True,
            bgcolor=ft.Colors.LIGHT_BLUE_50,
            padding=10,
            border=ft.border.all(1, ft.Colors.BLACK),
            content=self.listV_baseGJF,
        )

        self.tabCont.content = ft.Column(
            expand=True,
            controls=[
                ft.Text("MI Path"),
                self.pickMI,
                ft.Text("Base GJF Path"),
                self.pickGJF,
                self.cont_viewBase,
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
                    _btmBtn.text = "Preview"
                case 'OTHER_FUNC1':
                    _btmBtn.visible = True
                    _btmBtn.disabled = False
                    _btmBtn.text = "Read_Base"
                case 'OTHER_FUNC2':
                    _btmBtn.visible = False

#?タブ5。作成するGJFのプレビュー
class Rgt_tab_5_GJFPreview(Rgt_col_TabBase):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.GJF_PREVIEW)
        self.listV_GJFPre = ft.ListView(
            expand=True,
            auto_scroll=True,
            spacing=0,
            controls=[]
        )
        self.tabCont.bgcolor = ft.Colors.LIGHT_BLUE_50
        self.tabCont.content = self.listV_GJFPre

        for _btmBtn in self.btmBtns.controls:
            if not isinstance(_btmBtn, _Btm_btn_TabFunc): continue
            match _btmBtn.btmBtnIdx.name:
                case 'EXIT_APP':
                    _btmBtn.visible = True
                    _btmBtn.disabled = False
                case 'NEXT_TAB':
                    _btmBtn.visible = True
                    _btmBtn.disabled = False
                    _btmBtn.text = "Save"
                case 'OTHER_FUNC1':
                    _btmBtn.visible = False
                case 'OTHER_FUNC2':
                    _btmBtn.visible = False



#?アプリ終了時の確認ダイアログ。終了時動作はダミー。実装時に上書き必須。
class App_ExitConfirmDlg(ft.AlertDialog):
    def __init__(self):
        super().__init__(
            modal=True,
            title=ft.Text("終了確認"),
            content=ft.Text("アプリを終了しますか？"),
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.actions = [
            ft.TextButton("Yes", on_click=self.yes_clicked),
            ft.TextButton("No", on_click=lambda e: self.page.close(self))
        ]

    def yes_clicked(self, e):
        raise NameError("このメソッドは実装時に上書きが必須です。")


class App_list_CellData_Value():
    def __init__(self, cell_data_label:en.CellDataLbl, value:str):
        self.LABEL = cell_data_label
        self.VALUE = value

class App_dict_CellData(Dict[str, str]):
    def __init__(self):
        super().__init__()
        self.atomsNum = 0
        self[en.CellDataLbl.STATE.value] = 'initialized'

    def __setitem__(self, key: str, value: str):
        if key == en.CellDataLbl.ATOMS.value or 'atoms' in key:
            self.atomsNum += 1
            super().__setitem__(f'{en.CellDataLbl.ATOMS.value}#{self.atomsNum}', value)
        else:
            if not key in en.CellDataLbl: raise ValueError(f'{key} is not in Enum_CellDataLbl.')
            super().__setitem__(key, value)


    def clear(self):
        super().clear()
        self.__init__()

    def get_last_atom(self) -> Optional[str]:
        for _n in range(self.atomsNum, -1, -1):
            if self.atomsNum <= 0: return None
            ifLbl = f'atoms#{_n}'
            if ifLbl in self.keys():
                #self.atomsNum = _n + 1
                return self[ifLbl]


class App_list_CellData(List[App_list_CellData_Value]):
    def __init__(self):
        pass

    def append(self, object: App_list_CellData_Value):
        for _data in self:
            if object.LABEL == _data.LABEL:
                if object.LABEL == en.CellDataLbl.ATOMS:
                    if object.VALUE == _data.VALUE:
                        self.remove(_data)
                        break
                else:
                    self.remove(_data)
                    break
        super().append(object)

    def append_value(self, cell_data_label:en.CellDataLbl, value:str):
        self.append(App_list_CellData_Value(cell_data_label, value))

    def get_value(self, cell_data_label:en.CellDataLbl) -> App_list_CellData_Value:
        for _value in self:
            if _value.LABEL == cell_data_label:
                return _value
        raise IndexError(f'{cell_data_label} is not in this list.')

class App_dict_Setting(Dict[en.SettingLabel, str]):
    def __init__(self):
        for _lbl in en.SettingLabel:
            self[_lbl] = "None"

    def __delitem__(self, key: en.SettingLabel):
        super().__setitem__(key, "None")

    def clear(self):
        self.__init__()


if __name__ == '__main__':
    #test_filedata = App_dict_CellData()
    #test_filedata[en.CellDataLbl.CELL_VOLUME.value] = "1990.3"
    #test_filedata['atoms'] = "C--0.001"
    #print(test_filedata)
    #if "atoms" == en.CellDataLbl.ATOMS.value: print("atoms_here")

    test_setting = App_dict_Setting()
    print(test_setting)
    test_setting[en.SettingLabel.APP_VER_NUM] = "6.0"
    print(test_setting)
    test_setting.clear()
    print(test_setting)
