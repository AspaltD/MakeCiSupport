import flet as ft
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple
import os
import copy
import logging
import time

import mdEnums as en
import mdAutoRun as ar
import mdTabChangeBar as tcb
import mdBottomButtons as bb
import mdInterfaces as itf

filePickers: Dict[en.FilePickerIdx, ft.FilePicker] = {}
fileData:FileData
settingData:SettingData
gjfData:GjfData
appLogger:logging.Logger
OUTPUUUUT_PATH:Path = Path('./datatext/outpuuuut.txt')


class SettingData(Dict[en.SettingLabel, str]):
    def __init__(self):
        self.settingPath = Path('./datatext/makeci_setting.txt')
        self.appVerType = "beta"
        self.appVerNum = "6.0"
        self._allowVerNum = 6.0

        for label in en.SettingLabel:
            self[label] = "None"

        if self.settingPath.is_file():
            if self._check_version():
                appLogger.info("read setting_file")
                self.read_setting()
                self.print_self()
                return
            else:
                appLogger.info("setting_file is old version")
        appLogger.info("make new setting_file")
        self._make_setting()

    def print_self(self):
        appLogger.info("{")
        for line in self:
            line_str:str = f'  {line.value}:\t{self[line]}'
            appLogger.info(line_str)
        appLogger.info("}")

    def _check_version(self) -> bool:
        verType = "None"
        verNum = "None"
        with open(self.settingPath) as f:
            for lineS in f:
                lineP = lineS.rstrip().split(sep=';')
                match lineP[0]:
                    case en.SettingLabel.APP_VER_TYPE.value:
                        verType = lineP[1]
                    case en.SettingLabel.APP_VER_NUM.value:
                        verNum = lineP[1]
                    case _: continue
        if verType == "None": return False
        if verNum == "None": return False
        if verType is self.appVerType: return False
        if float(verNum) < self._allowVerNum: return False
        return True

    def _make_setting(self):
        if not Path('./datatext').is_dir():
            Path.mkdir(Path('./datatext'))
        if not self.settingPath.is_file():
            self.settingPath.touch()
        self[en.SettingLabel.FILE_NAME] = "makeci_setting"
        self[en.SettingLabel.APP_VER_TYPE] = self.appVerType
        self[en.SettingLabel.APP_VER_NUM] = self.appVerNum
        self.write_setting()

    def read_setting(self):
        with open(self.settingPath) as f:
            for lineS in f:
                lineP = lineS.rstrip().split(sep=';')
                if len(lineP) <= 1: continue
                lineP[1] = ';'.join(lineP[1:])
                for label in en.SettingLabel:
                    if label.value == lineP[0]:
                        self[label] = lineP[1]
                        break

    def write_setting(self):
        with open(self.settingPath, mode='w') as f:
            for line in self:
                outputLine = line.value + ";" + self[line] + '\n'
                f.write(outputLine)

class GjfData(List[str]):
    def __init__(self, def_gjf_path:Optional[Path]=None):
        self.defGjfPath = Path("./datatext/default.gjf")
        if not def_gjf_path is None:
            if self.read_gjf(def_gjf_path): return
        if self.defGjfPath.is_file(): self.read_gjf(self.defGjfPath)
        else: self.make_def_gjf()

    def print_self(self):
        for line in self:
            appLogger.info(line)

    def read_gjf(self, gjf_path:Path) -> bool:
        self.clear()
        appLogger.info("read_gjf -->")
        complete = True
        i = -1
        with open(gjf_path) as f:
            for lineS in f:
                i += 1
                line = lineS.rstrip()
                match i:
                    case 0:
                        if not re.match('%chk=.*', line):
                            complete = False
                            break
                    case _:
                        if i >= 6: break
                self.append(line)
        self.print_self()
        appLogger.info("<-- end")
        return complete

    def make_def_gjf(self):
        self.clear()
        appLogger.info("make_def_gjf")
        self.append("%chk=C:/Users/Owner/Desktop/Data/Yoshida/def/default.chk")
        self.append("# wb97xd/lanl2dz pop=full geom=connectivity")
        self.append("\n")
        self.append("Title Card Required")
        self.append("\n")
        self.append("0 1")
        self.print_self()
        self.save_gjf(self.defGjfPath)

    def save_gjf(self, gjf_path:Path):
        is_def = False
        if gjf_path == self.defGjfPath: is_def = True
        i = -1
        with open(gjf_path, mode="w") as f:
            for line in self:
                i += 1
                f.write(line.strip() + '\n')
                if is_def and i >= 5: break
    
    def read_mi(self, mi_path:Path):
        if len(self) >= 6: self = GjfData(self.defGjfPath)
        i = -1
        with open(mi_path) as f:
            for lineS in f:
                i += 1
                if not lineS.strip(): continue
                line = lineS.rstrip()
                if i >= 450:
                    appLogger.error("readline is over.(400 lines)")
                    break
                lineP = line.split()
                if lineP[0] != "POS": continue
                lineP[1] = lineP[1].split(sep='-')[0]
                if len(lineP[1]) < 2: lineP[1] += "_"
                for p in range(2, 5):
                    while len(lineP[p]) < 10: lineP[p] = "_" + lineP[p]
                outline = '  '.join(lineP[1:])
                self.append(outline.replace('_', ' '))
        self.print_self()

class FileData_Value():
    def __init__(self, cell_info_label:en.CellInfoLbl, value:Tuple[str, ...]):
        self._lbl = cell_info_label
        self._value = value
        if len(value) == 0: self.change_value(())

    def get_label(self) -> en.CellInfoLbl:
        return en.CellInfoLbl(self._lbl)
    
    def get_value(self) -> Tuple[str, ...]:
        return copy.deepcopy(self._value)
    
    def get_print(self) -> str:
        return f'{self._lbl.value} = {self._value}'
    
    def change_value(self, new_value:Tuple[str, ...]) -> Tuple[str, ...]:
        lastValue = self.get_value()
        if len(new_value) == 0: self._value = ("None",)
        else: self._value = new_value
        return lastValue
    
    def get_output_line(self) -> str:
        match self._lbl.value:
            case 'atoms':
                return '   '.join(self._value)
            case _:
                return self._lbl.value + "   " + self._value[0]

class FileData(List[FileData_Value]):
    def __init__(self):
        self.append_value(en.CellInfoLbl.STATE, ("Initialize",))

    def append_value(self, cell_info_label:en.CellInfoLbl, value:Tuple[str, ...]):
        self.append(FileData_Value(cell_info_label, value))

    def print_data(self):
        i = -1
        appLogger.info("idx: value")
        for value in self:
            i += 1
            appLogger.info(f'{i}: {value.get_print()}')

    def get_value(self, cell_info_label:en.CellInfoLbl) -> FileData_Value:
        for value in self:
            if value.get_label() == cell_info_label:
                return value
        raise IndexError("This label is not in this list.")

    def get_value_value(self, cell_info_label:en.CellInfoLbl) -> Tuple[str, ...]:
        for value in self:
            if value.get_label() == cell_info_label:
                return value.get_value()
        raise IndexError("This label is not in this list.")

    def read_cif_file(self, cifPath:Path):
        if not Path.is_file(cifPath): raise FileExistsError("指定されたパスのファイルが存在しません")
        if cifPath.suffix[1:] != 'cif': raise ValueError("ファイルの拡張子が正しくありません")
        self.clear()
        self.append_value(en.CellInfoLbl.STATE, ("FileData_CIF",))
        i:int = -1
        atoms:bool = False
        atom1stIdx:int = 0
        atom2ndIdx:int = 0
        with open(cifPath) as f:
            for lineS in f:
                i += 1
                line = lineS.rstrip()
                if i >= 450: raise ValueError("readline is over.(450 lines)")
                if i == 0:
                    if not cifPath.stem.lower() in line:
                        raise ValueError("file is not compleat by Olex2-1.5")
                    self.append_value(en.CellInfoLbl.DATA_NAME, (line,))
                    continue
                if "_space_group_IT_number" in line:
                    self.append_value(en.CellInfoLbl.SPACE_G_IT_NUM, (line.split()[1],))
                elif "_space_group_name_H-M_alt" in line:
                    stock = line.split("'")
                    self.append_value(en.CellInfoLbl.SPACE_G_NAME, ('_'.join(stock[1].split(' ')),))
                elif "_cell_" in line:
                    stock = line.split()
                    for lbl in en.CellInfoLbl:
                        #stock[インデックス][文字列の何番目か]
                        if lbl.value == stock[0][1:]:
                            self.append_value(lbl, (stock[1].split('(')[0],))
                            break
                    continue
                elif "_atom_site_disorder_group" in line:
                    atoms = True
                    atom1stIdx = 1
                    atom2ndIdx = 1
                    continue
                elif "loop_" in line:
                    if atoms:
                        appLogger.info("read finished")
                        appLogger.info("i: " + str(i))
                        break
                    else:
                        atoms = False
                        continue
                else:
                    pass
                if atoms:
                    #? 行が正しく原子情報を示しているか判定
                    atomParts = line.split()
                    if len(atomParts) < 5: continue
                    #? 第1，第2 インデックス番号の決定
                    atomName = atomParts[1]
                    if atom1stIdx == 1 and atom2ndIdx == 1:
                        pass
                    elif atomName == self[-1].get_value()[0]:
                        atom1stIdx = int(self[-1].get_value()[1])
                    else:
                        atom1stIdx = int(self[-1].get_value()[1]) + 1
                        atom2ndIdx = 1
                    #? リストへの追加。次も同じ種類の元素と仮定してatomSexIdxを+1して次へ。
                    #? また，occの有無を判別して混晶なら占有比の抜き出しも行う
                    self.append_value(en.CellInfoLbl.ATOMS, (atomName,str(atom1stIdx),str(atom2ndIdx),atomParts[2].split('(')[0],atomParts[3].split('(')[0],atomParts[4].split('(')[0]))
                    atom2ndIdx += 1
                    if not atomParts[7] == "1":
                        value = self[-1].get_value() + (atomParts[7].split('(')[0],)
                        self[-1].change_value(value)
        self.print_data()
        self.save_outpuuuut_file()

    def read_output_file(self, outputPath:Path):
        if not Path.is_file(outputPath): raise FileExistsError("指定されたパスのファイルが存在しません")
        if outputPath.suffix[1:] != 'txt': raise ValueError("ファイルの拡張子が正しくありません")
        self.clear()
        self.append_value(en.CellInfoLbl.STATE, ("FileData_Output",))
        i:int = -1
        with open(outputPath) as f:
            for lineS in f:
                i += 1
                line = lineS.strip()
                if i >= 200:
                    appLogger.info("readline is over.(200)")
                    raise ValueError("読み取り上限を超えました(200 lines)")
                if i == 0:
                    if not re.match('MakeCi_.*', line):
                        appLogger.info("This txt_file is not output_file.")
                        raise ValueError("読み取り可能なファイルではありません")
                    else: continue
                lineP = line.split()
                for label in en.CellInfoLbl:
                    if label.value == lineP[0]:
                        self.append_value(label, tuple(lineP))
                        break
            appLogger.info(f"end_line: {i}")
        self.print_data()
        self.save_outpuuuut_file()
        return True

    def save_outpuuuut_file(self):
        if not re.match('FileData_.*', self[0].get_value()[0]):
            appLogger.error("file_data is not true")
            self.clear()
            self.append_value(en.CellInfoLbl.STATE, ("Initialize",))
            raise ValueError("ファイルデータが正しくありません")
        with open(OUTPUUUUT_PATH, mode='w') as f:
            f.write("makeCi_output"+'\n')
            for line in self:
                if line.get_label().name == 'STATE': continue
                f.write(line.get_output_line() + '\n')
        appLogger.info("outpuuuut saved")

    def save_output_file(self, outputPath:Path):
        if outputPath.suffix[1:] == "": raise ValueError("ディレクトリは指定できません")
        if outputPath.suffix[1:] != "txt": raise ValueError("拡張子が不正です")
        if not outputPath.parent.exists(): raise ValueError("ディレクトリが存在しません")
        if not outputPath.is_file(): outputPath.touch()
        state = self.get_value_value(en.CellInfoLbl.STATE)
        if state[0] is "None": raise ValueError("ファイルデータが正しくありません")
        if not re.match('FileData_.*', state[0]): raise ValueError("ファイルデータが出力可能ではありません")
        with open(outputPath, mode='w') as f:
            f.write("MakeCi_output"+'\n')
            for line in self:
                if line.get_label().name == 'STATE': continue
                f.write(line.get_output_line() + '\n')
        appLogger.info(f'{outputPath.stem} saved')

    def change_file_name(self, newFileName:str) -> Optional[str]:
        if '\\' in newFileName: return None
        if '.' in newFileName: return None
        if ' ' in newFileName: return None
        if newFileName == "": return None
        value = self.get_value(en.CellInfoLbl.DATA_NAME)
        lastName = value.get_value()[0]
        value.change_value((newFileName,))
        appLogger.info(f"data_name changed to {newFileName}")
        return lastName

class Cn_Tab99_PlaceHoldeeeer(itf.Itf_TabContainer):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.PLACE_HOLDER, dflt_visible=True)
        self.content = ft.Placeholder(color=ft.Colors.random())

class Cn_Tab0_FilePathSelect(itf.Itf_TabContainer):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.FILE_PATH_SELECT, dflt_visible=True)
        self.pickBuilder = itf.If_FilePickerBar(en.FilePickerIdx.BUILDER_PICK)
        self.pickCIF = itf.If_FilePickerBar(en.FilePickerIdx.CIF_PICK)
        self.pickTXT = itf.If_FilePickerBar(en.FilePickerIdx.OUTPUT_PICK)

        self.controls = [
            ft.Text("Builder Path"),
            self.pickBuilder,
            ft.Text("CIF File Path"),
            self.pickCIF,
            ft.Text("Text File Path"),
            self.pickTXT,
        ]
        self.content = ft.Column(controls=self.controls)

    def set_init(self) -> Tuple[str, ...]:
        log = super().set_init()
        for cont in self.controls:
            if not isinstance(cont, itf.If_FilePickerBar): continue
            log += cont.set_init(
                file_picker=filePickers[cont.pickIdx],
                path_from_setting=settingData[cont.pickIdx.get_setting_label()]
            )
        return log
    
    def _set_btmBtn_prop(self) -> itf.Data_BtmBtnPropsDict:
        props = super()._set_btmBtn_prop()
        props[en.BtmBtnIdx.NEXT_TAB].change_props(
            disabled=False,
            text="ReadCIF",
        )
        props[en.BtmBtnIdx.OTHER_FUNC1].change_props(
            disabled=False,
            text="ReadTXT"
        )
        props[en.BtmBtnIdx.OTHER_FUNC2].change_props(
            visible=False
        )
        return props

    def readCIF_event(self):
        if self.pickBuilder.get_path() is None:
            appLogger.warning("selected file is not match suffix (.exe)")
            raise ValueError("選択されたファイルと指定の拡張子が合いません")
        if self.pickCIF.get_path() is None:
            appLogger.warning("selected file is not match suffix (.cif)")
            raise ValueError("選択されたファイルと指定の拡張子が合いません")
        appLogger.info("Read_CIF started -->")
        fileData.read_cif_file(self.pickCIF.get_path())
        appLogger.info("<-- end")
        self.update()

    def readTXT_event(self):
        if self.pickBuilder.get_path() is None:
            appLogger.warning("selected file is not match suffix (.exe)")
            raise ValueError("選択されたファイルと指定の拡張子が合いません")
        if self.pickTXT.get_path() is None:
            appLogger.warning("selected file is not match suffix (.cif)")
            raise ValueError("選択されたファイルと指定の拡張子が合いません")
        appLogger.info("Read_TXT started -->")
        fileData.read_output_file(self.pickTXT.get_path())
        appLogger.info("<-- end")
        self.update()

class Cn_Tab1_ReadData(itf.Itf_TabContainer):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.READ_DATA, dflt_visible=False)
        #* 格子定数用
            #*個別データ
        self.dataName = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.DATA_NAME, label="Data_Name", hint_text="fileName", read_only=False)
        self.spaceGItNum = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.SPACE_G_IT_NUM, label="SpaceG_IT_Num", hint_text="space_group_IT_number")
        self.spaceGName = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.SPACE_G_NAME, label="SpaceG_Name", hint_text="space_group_name_H-M_alt")
        self.cellLenA = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.CELL_LEN_A, label="Cell_Length_a", hint_text="cell_length_a")
        self.cellLenB = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.CELL_LEN_B, label="Cell_Length_b", hint_text="cell_length_b")
        self.cellLenC = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.CELL_LEN_C, label="Cell_Length_c", hint_text="cell_length_c")
        self.cellAngleA = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.CELL_ANGLE_A, label="Cell_Angle_alpha", hint_text="cell_angle_alpha")
        self.cellAngleB = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.CELL_ANGLE_B, label="Cell_Angle_beta", hint_text="cell_angle_beta")
        self.cellAngleC = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.CELL_ANGLE_C, label="Cell_Angle_gamma", hint_text="cell_angle_gamma")
        self.cellVolume = itf.If_Txtf_CellData(cell_info_label=en.CellInfoLbl.CELL_VOLUME, label="Cell_Volume", hint_text="cell_volume")
        self.txtfList:List[itf.If_Txtf_CellData] = [
            self.dataName, self.spaceGItNum, self.spaceGName,
            self.cellLenA, self.cellLenB, self.cellLenC,
            self.cellAngleA, self.cellAngleB, self.cellAngleC,
            self.cellVolume
        ]
            #* 格子定数コンテンツ全体
        self.cellDataGroup = ft.Column(
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
                )
            ]
        )
        #* 原子座標の表関連
        self.selectedRows:List[int] = []
        self.readTable = ft.DataTable(
            border = ft.border.all(1, ft.Colors.BLACK),
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

        #* コンテンツの配置
        self.content = ft.Column(
            controls=[
                self.cellDataGroup,
                ft.Column(
                    expand=3,
                    controls=[
                        self.readTable
                    ],
                    scroll=ft.ScrollMode.ALWAYS
                )
            ]
        )

        #* 保存機能用ファイルピッカー関連
        self.saveFilePicker:ft.FilePicker
        self.outputPath:Path

    def set_init(self) -> Tuple[str, ...]:
        log = super().set_init()
        self.dataName.on_blur = self.rename_event
        self.saveFilePicker = filePickers[en.FilePickerIdx.OUTPUT_SAVE]
        self.saveFilePicker.on_result = self.pick_files_result
        return log
    
    def _set_btmBtn_prop(self) -> itf.Data_BtmBtnPropsDict:
        props = super()._set_btmBtn_prop()
        props[en.BtmBtnIdx.NEXT_TAB].change_props(
            disabled=False,
            text="Save&Go"
        )
        props[en.BtmBtnIdx.OTHER_FUNC1].change_props(
            disabled=False,
            text="Save",
            on_click=self.event_func1_save
        )
        props[en.BtmBtnIdx.OTHER_FUNC2].change_props(
            disabled=False,
            text="Remove",
            on_click=self.dataTable_row_clear_event
        )
        return props

    def insert_cells(self):
        # txtf_idx -> 0:fileName, 1:SpaceGITNum, 2:SpaceGName,
        # 3:CellLen_a, 4:CellLen_b, 5:CellLen_c,
        # 6:CellAngle_a, 7:CellAngle_b, 8:CellAngle_c, 9:CellVolume
        #* read_row -> data = インデックス番号
        self.readTable.rows = list()
        read_row:ft.DataRow
        i:int = -1
        n:int = 0
        for inList in fileData:
            i += 1
            match inList.get_label().name:
                case 'STATE':
                    if re.match('FileData_.*',inList.get_value()[0]): continue
                    appLogger.error("this file_data is not true.")
                    raise ValueError("ファイルデータが正しくありません")
                case 'ATOMS':
                    read_row = ft.DataRow(cells=[], data=n, on_select_changed=self.row_CBox_clicked)
                    for value in inList.get_value():
                        read_row.cells.append(ft.DataCell(ft.Text(value=value)))
                    while len(inList.get_value()) <= 6:
                        read_row.cells.append(ft.DataCell(ft.Text("-")))
                    self.readTable.rows.append(read_row)
                    n += 1
                case x:
                    for txtf in self.txtfList:
                        if x == txtf.cellDataLbl.name:
                            txtf.value = inList.get_value()[0]
                            break

    def rename_event(self, e:ft.ControlEvent):
        #if fileData.get_value_value(en.CellInfoLbl.DATA_NAME)[0] == "None": raise ValueError("ファイルデータが不正です")
        if e.control.value is None: self.dataName.value = fileData.get_value_value(en.CellInfoLbl.DATA_NAME)[0]
        if not e.control.value.strip(): self.dataName.value = fileData.get_value_value(en.CellInfoLbl.DATA_NAME)[0]
        if fileData.change_file_name(e.control.value) is None: self.dataName.value = fileData.get_value_value(en.CellInfoLbl.DATA_NAME)[0]
        self.update()

    #* 行をクリックしたときに削除リストに追加したり消したりするイベント。
    def row_CBox_clicked(self,e:ft.ControlEvent):
        if e.control.selected:
            e.control.selected = False
            for idx in self.selectedRows:
                if idx == e.control.data:
                    self.selectedRows.remove(idx)
                else:
                    pass
        else:
            e.control.selected = True
            self.selectedRows.append(e.control.data)
        appLogger.info(self.selectedRows)
        self.update()

    def commit_fileData(self):
        tab1FileData:FileData = FileData()
        tab1FileData.clear()
        tab1FileData.append_value(en.CellInfoLbl.STATE, ("FileData_commit",))
        for txtf in self.txtfList:
            tab1FileData.append_value(txtf.cellDataLbl, (txtf.value,))
        if self.readTable.rows is None: raise ValueError("原子座標のデータが存在しません")
        for row in self.readTable.rows:
            tab1FileData.append_value(en.CellInfoLbl.ATOMS, ("init",))
            value:List[str] = list()
            for cell in row.cells:
                #? isinstanceで型チェックでエラー消せる？
                if cell.content.value == "-": continue
                else: value.append(str(cell.content.value))
            tab1FileData[-1].change_value(tuple(value))
        global fileData
        fileData = copy.deepcopy(tab1FileData)
        fileData.save_outpuuuut_file()

    def pick_files_result(self, e:ft.FilePickerResultEvent):
        if e.path:
            if re.match('.*txt',e.path):
                self.outputPath = Path(e.path)
            else:
                self.outputPath = Path(e.path+".txt")
            appLogger.info(self.outputPath)
            self.commit_fileData()
            fileData.save_output_file(self.outputPath)
        self.update()

    def dataTable_row_clear_event(self, e:ft.ControlEvent):
        if self.readTable.rows is None: return
        if len(self.readTable.rows) == 0: return
        for delIdx in self.selectedRows:
            for row in self.readTable.rows:
                if row.data == 404: continue
                if row.data == delIdx:
                    lastData = row.cells
                    self.readTable.rows.remove(row)
                    appLogger.info(lastData)
            lastIdx = self.selectedRows.remove(delIdx)
        self.update()
    
    def event_func1_save(self, e:ft.ControlEvent):
        if not re.match('FileData_.*', fileData.get_value_value(en.CellInfoLbl.STATE)[0]): return
        self.commit_fileData()
        self.saveFilePicker.save_file(
            allowed_extensions=['txt'],
            file_name=fileData.get_value_value(en.CellInfoLbl.DATA_NAME)[0]
        )
        self.update()

class Cn_Tab2_BuilderLog(itf.Itf_TabContainer):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.BUILDER_LOG, dflt_visible=True)
        self.bgcolor = ft.Colors.BLACK
        self.logView = itf.If_LogView()
        self.content = self.logView

    def _set_btmBtn_prop(self) -> itf.Data_BtmBtnPropsDict:
        props = super()._set_btmBtn_prop()
        props[en.BtmBtnIdx.NEXT_TAB].change_props(
            disabled=False,
            text="Stop",
        )
        props[en.BtmBtnIdx.EXIT_APP].change_props(
            disabled=True,
        )
        props[en.BtmBtnIdx.OTHER_FUNC1].change_props(
            visible=False,
        )
        props[en.BtmBtnIdx.OTHER_FUNC2].change_props(
            visible=False,
        )
        return props

class Cn_Tab3_BuilderResult(itf.Itf_TabContainer):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.BUILDER_RESULT, dflt_visible=False)
        self.txtf_sort = ft.TextField(dense=True, read_only=True, max_lines=3)
        self.txtf_fileName = ft.TextField(dense=True, read_only=True, max_lines=3)
        self.txtf_runtime = ft.TextField(dense=True, read_only=True)
        #!self.ins_txtf_sort(OUTPUUUUT_PATH)
        self.controls = [
            ft.Text("Run_file_name"),
            self.txtf_fileName,
            ft.Text("Sort_file path"),
            self.txtf_sort,
            ft.Text("Builder run time"),
            self.txtf_runtime,
        ]
        
        self.content = ft.Column(
            expand=True,
            controls=self.controls
        )

    def set_init(self) -> Tuple[str, ...]:
        log = super().set_init()
        return log
    
    def _set_btmBtn_prop(self) -> itf.Data_BtmBtnPropsDict:
        props = super()._set_btmBtn_prop()
        props[en.BtmBtnIdx.OTHER_FUNC1].change_props(
            visible=False,
        )
        props[en.BtmBtnIdx.OTHER_FUNC2].change_props(
            visible=False,
        )
        return props

    def ins_txtf_fileName(self):
        self.txtf_fileName.value = None
        fileName = fileData.get_value_value(en.CellInfoLbl.DATA_NAME)[0]
        if fileName == "None": pass
        else: self.txtf_fileName.value = fileName
    
    def ins_txtf_out(self, out_path:Path):
        self.txtf_sort.value = None
        path = Path(out_path)
        if not path.is_file(): raise ValueError("引数が不正です")
        if path.suffix[1:] != 'txt': raise ValueError("拡張子が合いません")
        self.txtf_sort.value = str(path.resolve())


class Cn_Tab4_MIPathSelect(itf.Itf_TabContainer):
    class PickGJF(itf.If_FilePickerBar):
        def __init__(self, tab4:Cn_Tab4_MIPathSelect):
            super().__init__(en.FilePickerIdx.GJF_PICK)
            self.tab4 = tab4

        def path_change(self, new_path_str: Optional[str]=None) -> Tuple[str, ...]:
            log = super().path_change(new_path_str)
            gjfData.read_gjf(self.get_path())
            self.tab4.ins_gjf_view()
            return log

    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.MI_PATH_SELECT, dflt_visible=False)
        self.pickMI = itf.If_FilePickerBar(en.FilePickerIdx.MI_PICK)
        self.pickGJF = self.PickGJF(self)
        self.viewDefGJF = ft.ListView(
            expand=True,
            auto_scroll=True,
            spacing=0,
            controls=[],
        )
        self.cont_viewBase = ft.Container(
            content=self.viewDefGJF,
            expand=True,
            bgcolor=ft.Colors.LIGHT_BLUE_50,
            padding=10,
            border=ft.border.all(1, ft.Colors.BLACK),
        )
        


        self.controls = [
            ft.Text("MI Path"),
            self.pickMI,
            ft.Text("Default GJF Path"),
            self.pickGJF,
            self.cont_viewBase,
        ]

        self.content = ft.Column(expand=True, controls=self.controls)

    def set_init(self) -> Tuple[str, ...]:
        log = super().set_init()
        for cont in self.controls:
            if not isinstance(cont, itf.If_FilePickerBar): continue
            log += cont.set_init(
                file_picker=filePickers[cont.pickIdx],
                path_from_setting=settingData[cont.pickIdx.get_setting_label()]
            )
        return log


    def ins_gjf_view(self):
        self.viewDefGJF.controls = list()
        for line in gjfData:
            self.viewDefGJF.controls.append(
                ft.TextField(
                    value=f'{line}',
                    read_only=True,
                    dense=True,
                    border=ft.InputBorder.NONE
                    )
            )
        self.update()

class Cn_Tab5_GJFPreview(itf.Itf_TabContainer):
    def __init__(self):
        super().__init__(tab_idx=en.TabIdx.MI_PREVIEW, dflt_visible=False)
        self.bgcolor = ft.Colors.LIGHT_BLUE_50
        self.viewGjf = ft.ListView(
            expand=True,
            auto_scroll=True,
            spacing=0,
            controls=[]
        )
        self.content = self.viewGjf

        self.savePicker_gjf:ft.FilePicker

    def set_init(self) -> Tuple[str, ...]:
        log = super().set_init()
        self.savePicker_gjf = filePickers[en.FilePickerIdx.GJF_SAVE]
        self.savePicker_gjf.on_result = self.pick_files_result
        return log

    def ins_view_gjf(self):
        self.viewGjf.controls.clear()
        for line in gjfData:
            self.viewGjf.controls.append(
                ft.TextField(
                    value=f'{line}',
                    read_only=True,
                    dense=True,
                    border=ft.InputBorder.NONE
                    )
            )

    def pick_files_result(self, e:ft.FilePickerResultEvent):
        if e.path:
            if re.match('.*gjf', e.path):
                gjfPath = Path(e.path)
            else:
                gjfPath = Path(e.path+".gjf")
            appLogger.info(gjfPath)
            gjfData.save_gjf(gjfPath)
        self.update()

class Btm_BtnBar(ft.Row):
    def __init__(self):
        super().__init__(
            expand=1,
            alignment=ft.MainAxisAlignment.END,
            controls=[],
        )
        for idx in en.BtmBtnIdx:
            self.controls.append(itf.If_BottomFuncBtn(idx))

    def set_init(self):
        pass
    
    def change_btn_properties(self, dict_properties:itf.Data_BtmBtnPropsDict):
        for prop in dict_properties.values():
            for btn in self.controls:
                if not isinstance(btn, itf.If_BottomFuncBtn): continue
                log = btn.change_property(prop)
                for msg in log: appLogger.debug(msg)
                break
class MakeCiSupApp(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
        )
        self.content = ft.Row(expand=True, controls=[])
        #左右を分ける一番大きな区分け
        self.left_tabChangeBar = itf.Itf_Left_TabChangeBar()
        self.right_tabBase = ft.Column(expand=3, spacing=2, controls=[])
        #右側部分の2番目の区分け
        self.cn_tabContents = ft.Stack(expand=10, controls=[])
        self.btmBtnContents = Btm_BtnBar()

        #タブたち
        self.cn_tab99 = Cn_Tab99_PlaceHoldeeeer()
        self.cn_tab0 = Cn_Tab0_FilePathSelect()
        self.cn_tab1 = Cn_Tab1_ReadData()
        self.cn_tab2 = Cn_Tab2_BuilderLog()
        self.cn_tab3 = Cn_Tab3_BuilderResult()
        self.cn_tab4 = Cn_Tab4_MIPathSelect()
        self.cn_tab5 = Cn_Tab5_GJFPreview()
        self.cn_tabContents.controls = [
                self.cn_tab99,
                self.cn_tab2,
                self.cn_tab0,
                self.cn_tab1,
                self.cn_tab3,
                self.cn_tab4,
                self.cn_tab5,
            ]
        self.right_tabBase.controls.append(self.cn_tabContents)
        #ボトムボタンたち
        self.right_tabBase.controls.append(self.btmBtnContents)
        #本体に配置
        self.content.controls = [
                self.left_tabChangeBar,
                self.right_tabBase
            ]

        #pywinautoを宣言してる自動化用クラスを実装
        self.ciAuto:ar.Ci_AutoRun

    def set_init(self):
        log = self.left_tabChangeBar.set_init(self.left_btn_event)
        for msg in log: appLogger.debug(msg=msg)
        for tab in self.cn_tabContents.controls:
            if not isinstance(tab, itf.Itf_TabContainer): continue
            log = tab.set_init()
            for msg in log: appLogger.debug(msg=msg)
            tab.update()
        self._set_btmBtn_func()
        self.ciAuto = ar.Ci_AutoRun()
        self.tab_change(en.TabIdx.FILE_PATH_SELECT)
        self.update()

    def tab_change(self, toTabIdx:en.TabIdx):
        appLogger.debug(f'tab_change -> {toTabIdx.get_tab_name()}')
        props = self.cn_tab99.get_dict_props()
        for tab in self.cn_tabContents.controls:
            if not isinstance(tab, itf.Itf_TabContainer): continue
            if tab.tabIdx == toTabIdx:
                tab.visible = True
                props = tab.get_dict_props()
            elif tab.tabIdx == 99: pass
            elif tab.tabIdx == 2: pass
            else: tab.visible = False
        self.btmBtnContents.change_btn_properties(props)
        self.update()

    def _set_btmBtn_func(self):
        for tab in self.cn_tabContents.controls:
            if not isinstance(tab, itf.Itf_TabContainer): continue
            props = self.cn_tab0.get_dict_props()
            match tab.tabIdx.name:
                case 'FILE_PATH_SELECT':
                    props[en.BtmBtnIdx.NEXT_TAB].change_prop_click(self.event_tab0_next_readCIF)
                    props[en.BtmBtnIdx.OTHER_FUNC1].change_prop_click(self.event_tab0_func1_readTXT)
                case 'READ_DATA':
                    props[en.BtmBtnIdx.NEXT_TAB].change_prop_click(self.event_tab1_next_save_go)
                case 'BUILDER_LOG':
                    props[en.BtmBtnIdx.NEXT_TAB].change_prop_click(self.event_tab2_next_stop)
                case _:
                    pass
        self.update()
    def _btmBtn_func_change(self, toTabIdx:en.TabIdx):
        match toTabIdx.name:
            case 'FILE_PATH_SELECT':
                self.btmBtn_Next.on_click = self.btmBtn_tab0_readCIF_event
                self.btmBtn_Func1.on_click = self.btmBtn_tab0_readTXT_event
            case 'READ_DATA':
                self.btmBtn_Next.on_click = self.btmBtn_tab1_save_go_event
                self.btmBtn_Func1.on_click = self.btmBtn_tab1_save_event
                self.btmBtn_Func2.on_click = self.cn_tab1.dataTable_row_clear_event
            case 'BUILDER_LOG':
                self.btmBtn_Next.on_click = self.btmBtn_tab2_stop_event
            case 'MI_PATH_SELECT':
                self.btmBtn_Next.on_click = self.btmBtn_tab4_preview_event
            case 'MI_PREVIEW':
                self.btmBtn_Func1.on_click = self.btmBtn_tab5_saveGJF_event
            case _:
                self.btmBtn_Next.on_click = self.btmBtn_def_event
                self.btmBtn_Func1.on_click = self.btmBtn_def_event
                self.btmBtn_Func2.on_click = self.btmBtn_def_event

    def left_btn_event(self, e:ft.ControlEvent):
        if not isinstance(e.control, tcb.Left_TabBtn): raise TypeError("タブ変更用のボタンではありません")
        self.tab_change(e.control.tabIdx)
        self.update()
    """
    def btmBtn_def_event(self, e:ft.ControlEvent):
        appLogger.error("This is BtmBtn's default event.")
        raise ValueError("ボタンに機能が付加されていないにもかかわらずクリックできる状態です")


    def btmBtn_exit_event(self, e:ft.ControlEvent):
        self.page.window.close()
    """

    def event_tab0_next_readCIF(self, e:ft.ControlEvent):
        self.cn_tab0.readCIF_event()
        self.tab_change(en.TabIdx.READ_DATA)
        self.cn_tab1.insert_cells()
        self.update()
    def event_tab0_func1_readTXT(self, e:ft.ControlEvent):
        self.cn_tab0.readTXT_event()
        self.tab_change(en.TabIdx.READ_DATA)
        self.cn_tab1.insert_cells()
        self.update()
    
    def event_tab1_next_save_go(self, e:ft.ControlEvent):
        if not re.match('FileData_.*', fileData.get_value_value(en.CellInfoLbl.STATE)[0]): return
        self.cn_tab1.commit_fileData()
        self.ciAuto.stopRun = False
        self.tab_change(en.TabIdx.BUILDER_LOG)
        self.update()
        self.ciAuto.auto_atom_info_insert(self.cn_tab0.pickBuilder.get_path(), fileData)
        self.page.window.to_front()
        self.cn_tab3.ins_txtf_fileName()
        self.tab_change(en.TabIdx.BUILDER_RESULT)
        self.update()
    """
    def btmBtn_tab1_save_event(self, e):
        if not re.match('FileData_.*', fileData[0][0]): return
        self.cn_tab1.commit_fileData()
        self.cn_tab1.saveFilePicker.save_file(allowed_extensions=['txt'], file_name=fileData.search_get_value_single(en.CellDataLabel.FILE_NAME)[-1])
        self.update()
    """
    def event_tab2_next_stop(self, e:ft.ControlEvent):
        self.ciAuto.stopRun = True
        self.update()

    def event_tab4_next_preview(self, e:ft.ControlEvent):
        if not self.cn_tab4.pickMI.get_path() is None: return
        gjfData.read_mi(self.cn_tab4.pickMI.get_path())
        self.cn_tab5.ins_view_gjf()
        self.tab_change(en.TabIdx.MI_PREVIEW)
        self.update()
    
    def btmBtn_tab5_saveGJF_event(self, e:ft.ControlEvent):
        if len(self.cn_tab5.viewGjf.controls) < 5: return
        self.cn_tab5.savePicker_gjf.save_file(
            allowed_extensions=['gjf'],
            file_name=self.cn_tab4.pickMI.get_path().stem,
            )

class ExitConfirmDialog(ft.AlertDialog):
    def __init__(self):
        super().__init__()
        self.modal = True
        self.title = ft.Text("終了確認")
        self.content = ft.Text("アプリを終了しますか？")
        self.actions = [
            ft.TextButton("Yes", on_click=self.yes_clicked),
            ft.TextButton("No", on_click=lambda e: self.page.close(self))
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def yes_clicked(self, e):
        self.page.close(self)
        settingData.write_setting()
        #!ここに終了時のsave動作などを追加
        self.page.window.destroy()

def create_app_logger(
        name:str, terminal_view:Tab2_LogView, log_file:str="app.log"
        ) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    #rootに流さないように
    logger.propagate = False
    #再代入できないように
    if logger.handlers: return logger

    #ログの書式設定
    formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )

    #GUI用のハンドラー
    view_handler = TabLogHandler(terminal_view)
    view_handler.setLevel(logging.DEBUG)
    view_handler.setFormatter(formatter)

    #File用のハンドラー
    file_handler = logging.FileHandler(log_file, mode='w', encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(view_handler)
    logger.addHandler(file_handler)

    return logger

def main(page: ft.Page):
    page.title = "Make Ci Support App"
    page.window.width = 800
    page.window.height = 605
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    #page.update()

    global filePickers
    for name in en.FilePickerIdx:
        filePickers[name] = ft.FilePicker()
        page.overlay.append(filePickers.get(name))
    


    makeCiSup = MakeCiSupApp()


    def window_close_event(e):
        if e.data == "close":
            page.open(ExitConfirmDialog())
            page.update()
    
    page.window.prevent_close = True
    page.window.on_event = window_close_event
    page.add(makeCiSup)
    page.window.center()
    #page.window.always_on_top = True
    page.update()
    
    global appLogger
    appLogger = create_app_logger(
        name="myapp",
        terminal_view=makeCiSup.cn_tab2.logView,
        log_file="./datatext/myapp.log",
        )
    appLogger.info("Application started")
    global settingData
    settingData = SettingData()
    global fileData
    fileData = FileData()
    global gjfData
    if settingData[en.SettingLabel.DEF_GJF_PATH] == "None":
        gjfData = GjfData()
    else:
        gjfData = GjfData(Path(settingData[en.SettingLabel.DEF_GJF_PATH]))
    
    makeCiSup.cn_tab0.set_txtf_init()
    makeCiSup.cn_tab4.set_txtf_init()
    makeCiSup.ciAuto.set_appLogger(appLogger)
    makeCiSup.tab_change(en.TabIdx.FILE_PATH_SELECT)
    page.update()
    


if __name__ == '__main__':
    ft.app(target=main)