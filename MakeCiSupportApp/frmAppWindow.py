import flet as ft
from pathlib import Path
import re
from typing import Dict, List, Optional
import os
import copy
import mdEnumClass as en
import mdAutoRun as ar

filePickers: Dict[en.FilePickerIdx, ft.FilePicker] = {}
fileData:FileData
settingData: Dict[str, str] = {}
OUTPUUUUT_PATH:Path = Path('MakeCiSupportApp/outpuuuut.txt')


class FileData_Value(List[str]):
    def __init__(self, data_label:en.CellDataLabel, *value:str):
        self.dataLabel = data_label
        if len(value) > self.dataLabel.get_label_max_len():
            self = ["Invalid value"]
            return
        for v in value:
            self.append(v)

    def check_label_len(self)->bool:
        if len(self) >= self.dataLabel.get_label_max_len(): return False
        return True

    def append(self, object: str) -> None:
        if not self.check_label_len():
            print("This value is max length.")
            return
        return super().append(object)
    
    def get_self(self) -> FileData_Value:
        return copy.deepcopy(self)


class FileData(List[FileData_Value]):
    def __init__(self):
        self.append_value(en.CellDataLabel.STATE, "Initialize")

    def append_value(self, cell_data_label:en.CellDataLabel, *value:str) -> None:
        return self.append(FileData_Value(cell_data_label, *value))

    def print_data(self):
        i = -1
        print("idx: value")
        for value in self:
            i += 1
            print(f'{i}: {value}')

    def search_get_value_single(self, cell_data_label:en.CellDataLabel) -> Optional[FileData_Value]:
        if cell_data_label == en.CellDataLabel.ATOM: return None
        if cell_data_label == en.CellDataLabel.CELL_LENGTH: return None
        if cell_data_label == en.CellDataLabel.CELL_ANGLE: return None
        for value in self:
            if value.dataLabel == cell_data_label: return value.get_self()
        return None
    
    def search_get_value_branch(self, cell_data_label:en.CellDataLabel, branch:str) -> Optional[FileData_Value]:
        #if cell_data_label != (en.CellDataLabel.CELL_LENGTH or en.CellDataLabel.CELL_ANGLE): return None
        for value in self:
            if value[0] == (value.dataLabel.get_label_str() + branch): return value.get_self()
        return None
    
    def search_get_value_atoms(self) -> List[FileData_Value]:
        atomList:List[FileData_Value] = []
        for value in self:
            if value.dataLabel is en.CellDataLabel.ATOM:
                atomList.append(value.get_self())
        return atomList

    def read_cif_file(self, cifPath:Path) -> bool:
        if not Path.is_file(cifPath): return False
        if cifPath.suffix[1:] != 'cif': return False
        self.clear()
        self.append_value(en.CellDataLabel.STATE, "FileData_CIF")
        i:int = -1
        atoms:bool = False
        atom1stIdx:int = 0
        atom2ndIdx:int = 0
        with open(cifPath) as f:
            for lineS in f:
                i += 1
                line = lineS.strip()
                if i >= 450:
                    print("readline is over.(400 lines)")
                    return False
                if i == 0:
                    if not cifPath.stem.lower() in line:
                        print("file is not compleat by Olex2-1.5")
                        return False
                    self.append_value(en.CellDataLabel.FILE_NAME, "fileName", line)
                    continue
                if "_space_group_IT_number" in line:
                    self.append_value(en.CellDataLabel.SPACE_GROUP_IT_NUM, "space_group_IT_number", line.split()[1])
                elif "_space_group_name_H-M_alt" in line:
                    stock = line.split("'")
                    self.append_value(en.CellDataLabel.SPACE_GROUP_NAME, "space_group_name_H-M_alt", '_'.join(stock[1].split(' ')))
                elif "_cell_length_" in line:
                    stock = line.split()
                    self.append_value(en.CellDataLabel.CELL_LENGTH, stock[0][1:], stock[1].split('(')[0])
                elif "_cell_angle_" in line:
                    stock = line.split()
                    self.append_value(en.CellDataLabel.CELL_ANGLE, stock[0][1:], stock[1].split('(')[0])
                elif "_cell_volume" in line:
                    self.append_value(en.CellDataLabel.CELL_VOLUME, "cell_volume", line.split()[1].split('(')[0])
                elif "_atom_site_disorder_group" in line:
                    atoms = True
                    atom1stIdx = 1
                    atom2ndIdx = 1
                    continue
                elif "loop_" in line:
                    if atoms:
                        print("read finished")
                        print("i: " + str(i))
                        break
                    else:
                        atoms = False
                        continue
                else:
                    pass
                if atoms:
                    #? 行が正しく原子情報を示しているか判定
                    atomParts = line.split()
                    if len(atomParts) < 5:
                        continue
                    #? 第1，第2 インデックス番号の決定
                    atomName = atomParts[1]
                    if atom1stIdx == 1 and atom2ndIdx == 1:
                        pass
                    elif atomName == self[-1][0]:
                        atom1stIdx = int(self[-1][1])
                    else:
                        atom1stIdx = int(self[-1][1]) + 1
                        atom2ndIdx = 1
                    #? リストへの追加。次も同じ種類の元素と仮定してatomSexIdxを+1して次へ。
                    #? また，occの有無を判別して混晶なら占有比の抜き出しも行う
                    self.append_value(en.CellDataLabel.ATOM, atomName,str(atom1stIdx),str(atom2ndIdx),atomParts[2].split('(')[0],atomParts[3].split('(')[0],atomParts[4].split('(')[0])
                    atom2ndIdx += 1
                    if not atomParts[7] == "1":
                        self[-1].append(atomParts[7].split('(')[0])
        self.print_data()
        self.save_outpuuuut_file()
        return True

    def read_output_file(self, outputFilePath:Path)->bool:
        if not Path.is_file(outputFilePath): return False
        if outputFilePath.suffix[1:] != 'txt': return False
        self.clear()
        self.append_value(en.CellDataLabel.STATE, "FileData_Output")
        i:int = -1
        with open(outputFilePath) as f:
            for lineS in f:
                i += 1
                line = lineS.strip()
                if i >= 200:
                    print("readline is over.(200)")
                    return False
                if i == 0:
                    if not re.match('MakeCi_.*', line):
                        print("This txt_file is not output_file.")
                        return False
                    else: continue

                lineP = line.split()
                for label in en.CellDataLabel:
                    if re.match(label.get_label_re(), lineP[0]):
                        self.append_value(label)
                        break
                for data in lineP:
                    self[-1].append(data)
            print(f"end_line: {i}")
        self.print_data()
        self.save_outpuuuut_file()
        return True

    def save_outpuuuut_file(self):
        outputLines:List[str] = ["MakeCi_output"]
        if not re.match('FileData_.*', self[0][0]): return
        for line in self:   #! writeメソッドをforの内側に入れる？
            if re.match('FileData_.*', line[0]): continue
            outputLines.append('   '.join(line))
        with open(OUTPUUUUT_PATH, mode='w') as f:
            f.write('\n'.join(outputLines))

    def save_output_file(self, outputPath:Path)->bool:
        if outputPath.suffix[1:] == "": return False
        if outputPath.suffix[1:] != "txt": return False
        #if not Path.exists(outputPath): return False
        if not re.match('FileData_.*', self[0][0]): return False
        with open(outputPath, mode='w') as f:
            f.write("MakeCi_output"+'\n')
            for line in self:
                if re.match('FileData_.*', line[0]): continue
                outputLine = '   '.join(line)
                f.write(outputLine + '\n')
        return True

    def change_file_name(self, newFileName:str)->Optional[str]:
        if '\\' in newFileName: return None
        if '.' in newFileName: return None
        if ' ' in newFileName: return None
        if newFileName == "": return None
        for value in self:
            if value[0] == "fileName":
                lastName = value[1]
                value[1] = newFileName
                return lastName
        return None


fileData = FileData()


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
    def __init__(self, tabIdx:en.TabIdx, leftBtnClicked:ft.ControlEvent, text:str):
        super().__init__(
            width=150,
            height=40
        )
        self.tabIdx = tabIdx
        self.on_click = leftBtnClicked
        self.text = text

class Left_TabBtn_Tab0(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(tabIdx=en.TabIdx.FILE_PATH_SELECT, leftBtnClicked=leftBtnClicked, text="ファイル設定")
class Left_TabBtn_Tab1(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(en.TabIdx.READ_DATA, leftBtnClicked, "読取結果")
class Left_TabBtn_Tab2(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(en.TabIdx.BUILDER_LOG, leftBtnClicked, "Builderログ")
class Left_TabBtn_Tab3(Left_TabBtn):
    def __init__(self, leftBtnClicked:ft.ControlEvent):
        super().__init__(en.TabIdx.BUILDER_RESULT, leftBtnClicked, "Builder動作完了")

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

class Btm_TabFuncBtn(ft.FilledButton):
    def __init__(self, text:str, workPlaceIdx:en.BtmBtnIdx):
        super().__init__(
            width=120,
            text=text
        )
        self.workPlaceIdx = workPlaceIdx

    def change_property(self, toTabIdx:en.TabIdx):
        self.disabled = True

class BtmBtn_EXit(Btm_TabFuncBtn):
    def __init__(self):
        super().__init__(
            text="ExitApp",
            workPlaceIdx=en.BtmBtnIdx.EXIT_APP
            )
        self.on_click = lambda _: self.page.window.close()

    def change_property(self, toTabIdx: en.TabIdx):
        match toTabIdx.name:
            case 'BUILDER_LOG':
                self.disabled = True
            case _:
                self.disabled = False

class BtmBtn_Next(Btm_TabFuncBtn):
    def __init__(self):
        super().__init__("Next", en.BtmBtnIdx.NEXT_TAB)

    def change_property(self, toTabIdx: en.TabIdx):
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
class BtmBtn_Func1(Btm_TabFuncBtn):
    def __init__(self):
        super().__init__("OtherFunc1", en.BtmBtnIdx.OTHER_FUNC1)

    def change_property(self, toTabIdx: en.TabIdx):
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

class BtmBtn_Func2(Btm_TabFuncBtn):
    def __init__(self):
        super().__init__("OtherFunc2", en.BtmBtnIdx.OTHER_FUNC2)

    def change_property(self, toTabIdx: en.TabIdx):
        match toTabIdx.name:
            case 'READ_DATA':
                self.text = "Remove"
                self.visible = True
            case _:
                self.text = "Func1"
                self.visible = False


class Btm_BtnBar(ft.Row):
    def __init__(self, tabIdx:en.TabIdx):
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


class Tab_FilePicker_Bar(ft.Row):
    def __init__(self, filePickerIdx:en.FilePickerIdx):
        super().__init__(
            spacing=0
        )
        self.filePickerIdx = filePickerIdx
        self.filePickeeeer = filePickers[self.filePickerIdx]
        self.filePickeeeer.on_result = self.filePicker_event
        self.filePath:Path = Path()

        self.pathTxtf = ft.TextField(expand=9, dense=True, on_blur=self.txtf_onBlur_event)
        self.controls = [
            self.pathTxtf,
            ft.FilledButton(
                expand=1,
                text="File",
                on_click=lambda _: self.filePickeeeer.pick_files(allowed_extensions=[self.filePickerIdx.get_fileType()])
            )
        ]

    def get_path(self)->Optional[Path]:
        return Path(self.filePath)

    def path_change(self, changedStr:Optional[str]=None):
        if changedStr is None:
            self.pathTxtf.value = ""
        else:
            self.pathTxtf.value = changedStr.replace(os.sep, '/').strip('"')
        value = Path(self.pathTxtf.value)
        self.filePath = value
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
    def check_true_path(self)->bool:
        if not Path.exists(self.filePath): return False
        if self.filePath.name == "": return False
        return True

class Tab0_FPBar_Builder(Tab_FilePicker_Bar):
    def __init__(self):
        super().__init__(filePickerIdx=en.FilePickerIdx.BUILDER_PICK)
        self.pathTxtf.hint_text = "Builder.exe Path"
class Tab0_FPBar_CIF(Tab_FilePicker_Bar):
    def __init__(self):
        super().__init__(filePickerIdx=en.FilePickerIdx.CIF_PICK)
        self.pathTxtf.hint_text = "CIF File Path"
class Tab0_FPBar_Output(Tab_FilePicker_Bar):
    def __init__(self):
        super().__init__(filePickerIdx=en.FilePickerIdx.OUTPUT_PICK)
        self.pathTxtf.hint_text = "Output File Path"

#* タブのコンテナ。
class Cn_TabContainer(ft.Container):
    def __init__(self, tabIdx:en.TabIdx, defVisible:bool):
        super().__init__(
            expand=10,
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.all(1, ft.Colors.random()),
            visible=defVisible
        )
        self.tabIdx = tabIdx

class Cn_Tab99_PlaceHoldeeeer(Cn_TabContainer):
    def __init__(self):
        super().__init__(tabIdx=en.TabIdx.PLACE_HOLDER, defVisible=True)
        self.content = ft.Placeholder(color=ft.Colors.random())

class Cn_Tab0_FilePathSelect(Cn_TabContainer):
    def __init__(self):
        super().__init__(tabIdx=en.TabIdx.FILE_PATH_SELECT, defVisible=True)
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
        #! ここで設定ファイルにBuilderのデータがあれば呼び出している。将来的には関数として独立させたい。
        if "builder_path" in settingData:
            self.pickBuilder.path_change(settingData['builder_path'])

class Tab1_TxtF_CellData(ft.TextField):
    def __init__(self, cell_data_label:en.CellDataLabel, label:str, hint_text:str, read_only:bool=True):
        super().__init__(
            expand=1,
            dense=True,
            label=label,
            hint_text=hint_text,
            read_only=read_only
        )
        self.cellDataLbl = cell_data_label

class Cn_Tab1_ReadData(Cn_TabContainer):
    def __init__(self):
        super().__init__(tabIdx=en.TabIdx.READ_DATA, defVisible=False)

        #* 格子定数用
            #*個別データ
        self.dataName = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.FILE_NAME, label="Data_Name", hint_text="fileName", read_only=False)
        self.spaceGItNum = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.SPACE_GROUP_IT_NUM, label="SpaceG_IT_Num", hint_text="space_group_IT_number")
        self.spaceGName = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.SPACE_GROUP_NAME, label="SpaceG_Name", hint_text="space_group_name_H-M_alt")
        self.cellLenA = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.CELL_LENGTH, label="Cell_Length_a", hint_text="cell_length_a")
        self.cellLenB = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.CELL_LENGTH, label="Cell_Length_b", hint_text="cell_length_b")
        self.cellLenC = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.CELL_LENGTH, label="Cell_Length_c", hint_text="cell_length_c")
        self.cellAngleA = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.CELL_ANGLE, label="Cell_Angle_alpha", hint_text="cell_angle_alpha")
        self.cellAngleB = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.CELL_ANGLE, label="Cell_Angle_beta", hint_text="cell_angle_beta")
        self.cellAngleC = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.CELL_ANGLE, label="Cell_Angle_gamma", hint_text="cell_angle_gamma")
        self.cellVolume = Tab1_TxtF_CellData(cell_data_label=en.CellDataLabel.CELL_VOLUME, label="Cell_Volume", hint_text="cell_volume")
        self.txtfList:List[Tab1_TxtF_CellData] = [
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
        self.saveFilePicker = filePickers[en.FilePickerIdx.OUTPUT_SAVE]
        self.saveFilePicker.on_result = self.pick_files_result
        self.outputPath:Path

    def insert_cells(self):
        # txtf_idx -> 0:fileName, 1:SpaceGITNum, 2:SpaceGName,
        # 3:CellLen_a, 4:CellLen_b, 5:CellLen_c,
        # 6:CellAngle_a, 7:CellAngle_b, 8:CellAngle_c, 9:CellVolume
        #* read_row -> data = インデックス番号
        if self.readTable.rows is None: return
        self.readTable.rows.clear()
        read_row:ft.DataRow
        i:int = -1
        n:int = 0
        for inList in fileData:
            i += 1
            if i == 0:
                if re.match('FileData_.*',inList[0]):
                    continue
                else:
                    return
            elif i == 400:
                print("list length is over(400)")
                return
            else:
                atom:bool = True
                    #* 格子の基礎データ(txtfに入力されるもの)を挿入。
                for txtf in self.txtfList:
                    if inList[0] == txtf.hint_text:
                        txtf.value = inList[1]
                        atom = False
                    #* 原子座標をデータテーブルに入力。
                if atom and re.match('[A-Z][a-z]{0,1}', inList[0]):
                    read_row = ft.DataRow(cells=[],data=n,on_select_changed=self.row_CBox_clicked)
                    for inData in inList:
                        read_row.cells.append(ft.DataCell(ft.Text(value=inData)))
                    if len(inList) <= 6:
                        read_row.cells.append(ft.DataCell(ft.Text("-")))
                    self.readTable.rows.append(read_row)
                    n += 1
                else:
                    pass

    #* 行をクリックしたときに削除リストに追加したり消したりするイベント。
    #* 実際に行を消すイベントは本体にある。
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
        print(self.selectedRows)
        self.update()

    def commit_fileData(self):
        tab1FileData:FileData = FileData()
        tab1FileData.clear()
        tab1FileData.append_value(en.CellDataLabel.STATE, "FileData_commit")
        for txtf in self.txtfList:
            tab1FileData.append_value(txtf.cellDataLbl, txtf.hint_text, txtf.value)
        for row in self.readTable.rows:
            tab1FileData.append_value(en.CellDataLabel.ATOM)
            for cell in row.cells:
                if cell.content.value == "-": pass
                else: tab1FileData[-1].append(str(cell.content.value))
        #global fileData
        fileData = copy.deepcopy(tab1FileData)
        fileData.save_outpuuuut_file()

    def pick_files_result(self, e:ft.FilePickerResultEvent):
        if e.path:
            if re.match('.*txt',e.path):
                self.outputPath = Path(e.path)
            else:
                self.outputPath = Path(e.path+".txt")
            print(self.outputPath)
            self.commit_fileData()
            fileData.save_output_file(self.outputPath)
        self.update()

    def dataTable_row_clear_event(self, e):
        if self.readTable.rows is None: return
        if len(self.readTable.rows) == 0: return
        for delIdx in self.selectedRows:
            for row in self.readTable.rows:
                if row.data == 404: continue
                if row.data == delIdx:
                    lastData = row.cells
                    self.readTable.rows.remove(row)
                    print(lastData)
            lastIdx = self.selectedRows.remove(delIdx)
        self.update()


class MakeCiSupApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.left_tabChangeBar = Left_TabChangeBar(leftBtnClicked=self.left_btn_event)
        self.cn_tab99 = Cn_Tab99_PlaceHoldeeeer()
        self.cn_tab0 = Cn_Tab0_FilePathSelect()
        self.cn_tab1 = Cn_Tab1_ReadData()
        self.cn_tabContents = ft.Stack(
            expand=10,
            controls=[
                self.cn_tab99,
                self.cn_tab0,
                self.cn_tab1
            ]
        )
        self.btmBtn_Next = BtmBtn_Next()
        self.btmBtn_Exit = BtmBtn_EXit()
        self.btmBtn_Func1 = BtmBtn_Func1()
        self.btmBtn_Func2 = BtmBtn_Func2()
        self.btmBtnContents = ft.Row(
            expand=1,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.btmBtn_Func2,
                self.btmBtn_Func1,
                self.btmBtn_Exit,
                self.btmBtn_Next
            ]
        )
        self.right_tabBase = ft.Column(
            height=540,
            expand=3,
            spacing=2,
            controls=[
                self.cn_tabContents,
                self.btmBtnContents
            ]
        )

        self.content = ft.Row(
            controls=[
                self.left_tabChangeBar,
                self.right_tabBase
            ]
        )
        self.tab_change(en.TabIdx.FILE_PATH_SELECT)


    def tab_change(self, toTabIdx:en.TabIdx):
        for tab in self.cn_tabContents.controls:
            if tab.tabIdx == toTabIdx: tab.visible = True
            elif tab.tabIdx == 99: pass
            else: tab.visible = False
        for btn in self.btmBtnContents.controls:
            btn.change_property(toTabIdx)
        self.btmBtn_func_change(toTabIdx)

    def btmBtn_func_change(self, toTabIdx:en.TabIdx):
        match toTabIdx.name:
            case 'FILE_PATH_SELECT':
                self.btmBtn_Next.on_click = self.btmBtn_tab0_readCIF_event
                self.btmBtn_Func1.on_click = self.btmBtn_tab0_readTXT_event
            case 'READ_DATA':
                self.btmBtn_Next.on_click = self.btmBtn_tab1_save_go_event
                self.btmBtn_Func1.on_click = self.btmBtn_tab1_save_event
                self.btmBtn_Func2.on_click = self.cn_tab1.dataTable_row_clear_event
            case _:
                self.btmBtn_Next.on_click = None
                self.btmBtn_Func1.on_click = None
                self.btmBtn_Func2.on_click = None

    def left_btn_event(self, e):
        self.tab_change(e.control.tabIdx)
        self.update()
    
    def btmBtn_tab0_readCIF_event(self, e):
        if self.cn_tab0.pickBuilder.check_true_path() is False: return
        if self.cn_tab0.pickCIF.check_true_path() is False: return
        if fileData.read_cif_file(self.cn_tab0.pickCIF.get_path()):
            self.tab_change(en.TabIdx.READ_DATA)
            self.cn_tab1.insert_cells()
        self.update()
    def btmBtn_tab0_readTXT_event(self, e):
        if self.cn_tab0.pickBuilder.check_true_path() is False: return
        if self.cn_tab0.pickOutput.check_true_path() is False: return
        if fileData.read_output_file(self.cn_tab0.pickOutput.get_path()):
            self.tab_change(en.TabIdx.READ_DATA)
            self.cn_tab1.insert_cells()
        self.update()
    
    def btmBtn_tab1_save_go_event(self,e):
        if not re.match('FileData_.*', fileData[0][0]): return
        self.cn_tab1.commit_fileData()
        ar.auto_atom_info_insert(self.cn_tab0.pickBuilder.get_path(), fileData)
        self.update()
    def btmBtn_tab1_save_event(self, e):
        if not re.match('FileData_.*', fileData[0][0]): return
        self.cn_tab1.commit_fileData()
        self.cn_tab1.saveFilePicker.save_file(allowed_extensions=['txt'])
        self.update()
    
    def btmBtn_tab1_remove_event(self, e):
        pass

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
        #!ここに終了時のsave動作などを追加
        self.page.window.destroy()

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
    
    global settingData
    settingDataPath = Path('MakeCiSupportApp/makeci_setting.txt')
    if Path.is_file(settingDataPath):
        with open(settingDataPath) as f:
            for lineS in f:
                lineP = lineS.rstrip().split(sep=';')
                if len(lineP) <= 1: continue
                lineP[1] = ';'.join(lineP[1:])
                settingData[lineP[0]] = lineP[1]
        print(settingData)
    else:
        with open(settingDataPath) as f:
            f.write("makeci_setting")
            f.write("app_ver;beta 0.1")
    
    makeCiSup = MakeCiSupApp()

    def window_close_event(e):
        if e.data == "close":
            page.open(ExitConfirmDialog())
            page.update()
    
    page.window.prevent_close = True
    page.window.on_event = window_close_event

    page.add(makeCiSup)
    page.window.center()
    page.update()

if __name__ == '__main__':
    ft.app(target=main)

