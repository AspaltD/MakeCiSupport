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
import mdInterfaces as i

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
        self.appVerNum = "4.0"
        self._allowVerNum = 4.0

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
                if len(lineP) == 0: continue
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
        appLogger.info("read_gjf")
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
            appLogger.info("This value is max length.")
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
        appLogger.info("idx: value")
        for value in self:
            i += 1
            appLogger.info(f'{i}: {value}')

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
                    appLogger.error("readline is over.(400 lines)")
                    return False
                if i == 0:
                    if not cifPath.stem.lower() in line:
                        appLogger.info("file is not compleat by Olex2-1.5")
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
                    appLogger.info("readline is over.(200)")
                    return False
                if i == 0:
                    if not re.match('MakeCi_.*', line):
                        appLogger.info("This txt_file is not output_file.")
                        return False
                    else: continue

                lineP = line.split()
                for label in en.CellDataLabel:
                    if re.match(label.get_label_re(), lineP[0]):
                        self.append_value(label)
                        break
                for data in lineP:
                    self[-1].append(data)
            appLogger.info(f"end_line: {i}")
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




class TabLogHandler(logging.Handler):
    def __init__(self, terminal_view:Tab2_LogView):
        super().__init__()
        self.terminalView = terminal_view

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.terminalView.log_write(msg, record.levelname)
    


class MakeCiSupApp(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
        )
        self.content = ft.Row(expand=True, controls=[])
        #左右を分ける一番大きな区分け
        self.left_tabChangeBar = tcb.Left_TabChangeBar(leftBtnClicked=self.left_btn_event)
        self.right_tabBase = ft.Column(expand=3, spacing=2, controls=[])
        #右側部分の2番目の区分け
        self.cn_tabContents = ft.Stack(expand=10, controls=[])
        self.btmBtnContents = ft.Row(expand=1, alignment=ft.MainAxisAlignment.END, controls=[])

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
        self.btmBtn_Next = bb.BtmBtn_Next(self.btmBtn_def_event)
        self.btmBtn_Exit = bb.BtmBtn_EXit(self.btmBtn_exit_event)
        self.btmBtn_Func1 = bb.BtmBtn_Func1(self.btmBtn_def_event)
        self.btmBtn_Func2 = bb.BtmBtn_Func2(self.btmBtn_def_event)
        self.btmBtnContents.controls =[
                self.btmBtn_Func2,
                self.btmBtn_Func1,
                self.btmBtn_Exit,
                self.btmBtn_Next,
            ]
        self.right_tabBase.controls.append(self.btmBtnContents)
        #本体に配置
        self.content.controls = [
                self.left_tabChangeBar,
                self.right_tabBase
            ]
        #self.tab_change(en.TabIdx.FILE_PATH_SELECT)

        #pywinautoを宣言してる自動化用クラスを実装
        self.ciAuto = ar.Ci_AutoRun()

    def tab_change(self, toTabIdx:en.TabIdx):
        appLogger.debug(f'tab_change -> {toTabIdx.get_tab_name()}')
        for tab in self.cn_tabContents.controls:
            if not isinstance(tab, Cn_TabContainer): continue
            if tab.tabIdx == toTabIdx: tab.visible = True
            elif tab.tabIdx == 99: pass
            elif tab.tabIdx == 2: pass
            else: tab.visible = False
        self._btmBtn_func_change(toTabIdx)
        for btn in self.btmBtnContents.controls:
            if not isinstance(btn, bb.Btm_TabFuncBtn): continue
            msgs = btn.change_property(toTabIdx)
            for msg in msgs: appLogger.debug(msg)

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
    
    def btmBtn_def_event(self, e:ft.ControlEvent):
        appLogger.error("This is BtmBtn's default event.")
        raise ValueError("ボタンに機能が付加されていないにもかかわらずクリックできる状態です")

    def btmBtn_exit_event(self, e:ft.ControlEvent):
        self.page.window.close()

    def btmBtn_tab0_readCIF_event(self, e:ft.ControlEvent):
        if self.cn_tab0.pickBuilder.check_true_path() is False: return
        if self.cn_tab0.pickCIF.check_true_path() is False: return
        appLogger.info("Read_CIF started -->")
        if fileData.read_cif_file(self.cn_tab0.pickCIF.get_path()):
            self.tab_change(en.TabIdx.READ_DATA)
            self.cn_tab1.insert_cells()
        appLogger.info("<-- end")
        self.update()
    def btmBtn_tab0_readTXT_event(self, e):
        if self.cn_tab0.pickBuilder.check_true_path() is False: return
        if self.cn_tab0.pickOutput.check_true_path() is False: return
        appLogger.info("Read_TXT started -->")
        if fileData.read_output_file(self.cn_tab0.pickOutput.get_path()):
            self.tab_change(en.TabIdx.READ_DATA)
            self.cn_tab1.insert_cells()
        appLogger.info("<-- end")
        self.update()
    
    def btmBtn_tab1_save_go_event(self,e):
        if not re.match('FileData_.*', fileData[0][0]): return
        self.cn_tab1.commit_fileData()
        self.ciAuto.stopRun = False
        self.tab_change(en.TabIdx.BUILDER_LOG)
        self.update()
        self.ciAuto.auto_atom_info_insert(self.cn_tab0.pickBuilder.get_path(), fileData)
        self.page.window.to_front()
        self.cn_tab3.ins_txtf_fileName()
        self.tab_change(en.TabIdx.BUILDER_RESULT)
        self.update()
    def btmBtn_tab1_save_event(self, e):
        if not re.match('FileData_.*', fileData[0][0]): return
        self.cn_tab1.commit_fileData()
        self.cn_tab1.saveFilePicker.save_file(allowed_extensions=['txt'], file_name=fileData.search_get_value_single(en.CellDataLabel.FILE_NAME)[-1])
        self.update()
    
    def btmBtn_tab2_stop_event(self, e):
        self.ciAuto.stopRun = True
        self.update()

    def btmBtn_tab4_preview_event(self, e:ft.ControlEvent):
        if not self.cn_tab4.pickMI.check_true_path(): return
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