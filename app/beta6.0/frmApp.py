import flet as ft
import logging
import os
from pathlib import Path
from typing import Optional,List,Dict
import re
import copy

import enEnums as en
import frmInterfaces as itf


LATEST_VER_TYPE = en.AppVerType.BETA
LATEST_VER_NUM = 6.0
ATOMS_SPLIT = "_,_"
_mgr_cellData:Mgr_CellData
_mgr_settingData:Mgr_SettingData
_mgr_filePickers:Mgr_FilePickers
_app_mainFrame:AppMainFrame

class Mgr_SettingData():
    def __init__(self):
        self.settingData = itf.App_dict_Setting()
        self.PATH_SETTING = Path('./datatext/makeci_setting.txt')

    def read_setting(self):
        if not self.PATH_SETTING.is_file():
            self._make_setting_file()
        with open(self.PATH_SETTING) as f:
            for _line in f:
                _lineData = _line.rstrip().split(sep=';')
                _lineData[1] = ';'.join(_lineData[1:])
                for _lbl in en.SettingLabel:
                    if _lbl.value == _lineData[0]:
                        self.settingData[_lbl] = _lineData[1]
                        break
        self._save_setting()

    def _make_setting_file(self):
        if not Path('./datatext').is_dir():
            Path.mkdir(Path('./datatext'))
        self.PATH_SETTING.touch()
        newSetting = itf.App_dict_Setting()
        newSetting[en.SettingLabel.APP_VER_TYPE] = LATEST_VER_TYPE.name
        newSetting[en.SettingLabel.APP_VER_NUM] = str(LATEST_VER_NUM)
        self._save_setting(newSetting)

    def _save_setting(self, list_setting:Optional[itf.App_dict_Setting]=None):
        listSetting = list_setting
        if listSetting is None:
            listSetting = self.settingData
        with open(self.PATH_SETTING, mode='w') as f:
            for _lbl in listSetting:
                f.write(f'{_lbl.value};{listSetting[_lbl]}\n')

    def change_setting(self, setting_label:en.SettingLabel, new_value:str):
        if self.settingData[setting_label] == new_value: return
        self.settingData[setting_label] = new_value
        self._save_setting()

class Mgr_CellData():
    def __init__(self):
        self.cellData = itf.App_dict_CellData()
        self.last_cellData:itf.App_dict_CellData
        self.DFLT_SAVE_PATH = Path('./datatext/outpuuuut.txt')
        self.pickedPath:Path
        self.savedPath:Path

    def _make_dflt_save_file(self):
        if not Path('./datatext').is_dir():
            Path.mkdir(Path('./datatext'))
        self.DFLT_SAVE_PATH.touch()

    #? 今betaからcifファイルとtxtファイル両用に変更。
    #? cifファイル内の原子座標の配置構造が分かったので一般性を持たせられるかも(2026/3/4現在未対応)
    def read_cellData(self, pick_path:Path):
        if not (pick_path.suffix[1:] == 'cif' or pick_path.suffix[1:] =='txt'):
            raise ValueError(f'{pick_path}\'s suffix is not true')
        new_cellData = itf.App_dict_CellData()
        new_cellData[en.CellDataLbl.STATE.value] = "data_reading"

        i = -1
        atom1stIdx:int
        atom2ndIdx:int
        lastAtoms:Optional[str]
        lastAtoms_detail:List[str]
        #atomOcc:Optional[str] = None
        new_atoms:List[str]
        nearly_atoms = False
        this_atoms = False
        exit_count = 0
        with open(pick_path) as f:
            for _line in f:
                i += 1
                if i > 450: break
                    #raise IndexError("readline is over.(450 lines)")
                #if not _line.strip(): continue
                _line = _line.strip()
                if not _line: continue
                #* データ名
                if re.match('data_.*', _line):
                    if _line == "data_xcalibur":
                        raise ValueError("This file is not compleat by Olex2.")
                    elif 'data_name' in _line:
                        _line = ' '.join(_line.split()[1:])
                    new_cellData[en.CellDataLbl.DATA_NAME.value] = _line.lstrip("data_")
                    continue
                #* 格子データ
                _lineData = _line.split()
                if _lineData[0] in en.CellDataLbl:
                    valueData = '_'.join(_lineData[1:])
                    valueData.strip("'")
                    valueData = re.sub(r"\(\d+\)", "", valueData)
                    new_cellData[_lineData[0]] = valueData
                    continue
                #* cifファイル用原子座標
                if nearly_atoms or "_atom_site_fract_z" in _line:
                    nearly_atoms = True
                    if len(_lineData) >= 4:
                        #print(_lineData)
                        this_atoms = True
                        exit_count = 0
                        #_lineData[0] = re.sub(r'\d+', '', _lineData[0])
                        lastAtoms = new_cellData.get_last_atom()
                        if lastAtoms is None:
                            atom1stIdx = 1
                            atom2ndIdx = 1
                        else:
                            lastAtoms_detail = lastAtoms.split(ATOMS_SPLIT)
                            if _lineData[1] == lastAtoms_detail[0]:
                                atom1stIdx = int(lastAtoms_detail[1])
                                atom2ndIdx = int(lastAtoms_detail[2]) + 1
                            else:
                                atom1stIdx = int(lastAtoms_detail[1]) + 1
                                atom2ndIdx = 1
                        #if 'Uani' in _lineData:
                        new_atoms = [
                            _lineData[1], str(atom1stIdx), str(atom2ndIdx), re.sub(r"\(\d+\)","", _lineData[2]),
                            re.sub(r"\(\d+\)", "", _lineData[3]), re.sub(r"\(\d+\)", "", _lineData[4]),
                            ]
                        if _lineData[7] == '1':
                            new_atoms.append("-")
                        else:
                            new_atoms.append(re.sub(r"\(\d+\)", "", _lineData[7]))
                            #atomOcc = _lineData[_lineData.index('Uani')+1]
                        new_cellData[en.CellDataLbl.ATOMS.value] = ATOMS_SPLIT.join(new_atoms)
                        continue
                    else:
                        exit_count += 1
                    if this_atoms and exit_count >= 2: break
                #* txtファイル用原子座標
                if re.match(r'atoms#\d+', _lineData[0]):
                    new_cellData[en.CellDataLbl.ATOMS.value] = _lineData[1]
                    continue
        new_cellData[en.CellDataLbl.STATE.value] = "data_picked"
        self.cellData = new_cellData
        self.save_cellData()
        print(f'end_line:{i}')

    def save_cellData(self, save_path:Optional[Path]=None):
        savePath = save_path
        if self.cellData[en.CellDataLbl.STATE.value] != 'data_picked':
            raise ValueError("cellData is not picked.")
        if savePath is None:
            savePath = self.DFLT_SAVE_PATH
            if not savePath.is_file():
                self._make_dflt_save_file()
        else:
            if savePath.is_file():
                if savePath.suffix[1:] != "txt":
                    raise ValueError("This path's suffix is not true.")
            else:
                raise ValueError("This path is not complete.")
        with open(savePath, mode='w') as f:
            f.write("MakeCi_output\n")
            for _line in self.cellData:
                if _line == en.CellDataLbl.STATE.value: continue
                f.write(f'{_line}   {self.cellData[_line]}\n')
        self.savedPath = savePath

    def commit_save_cellData(self, new_cellData:itf.App_dict_CellData, save_path:Optional[Path]=None):
        if new_cellData[en.CellDataLbl.STATE.value] != 'data_picked':
            raise ValueError("cellData is not picked.")
        #self.last_cellData = itf.App_dict_CellData()
        #for _lbl in self.cellData:
        #    if 'atoms' in _lbl:
        #        self.last_cellData['atoms'] = copy.deepcopy(self.cellData[_lbl])
        #    self.last_cellData[copy.deepcopy(_lbl)] = copy.deepcopy(self.cellData[_lbl])
        self.last_cellData = copy.deepcopy(self.cellData)
        self.cellData = new_cellData
        print("saved")
        self.save_cellData(save_path)

class Mgr_FilePickers(Dict[en.FilePickerIdx, ft.FilePicker]):
    def __init__(self):
        super().__init__()
        for _name in en.FilePickerIdx:
            self[_name] = ft.FilePicker()

class Tab0_CIFSelect(itf.Rgt_tab_0_CIFSelect):
    def __init__(self):
        super().__init__()

    def set_init(self):
        self.pickBuilder.set_picker_init(_mgr_filePickers[en.FilePickerIdx.PICK_BUILDER])
        self.pickCIF.set_picker_init(_mgr_filePickers[en.FilePickerIdx.PICK_CIF])
        self.pickTXT.set_picker_init(_mgr_filePickers[en.FilePickerIdx.PICK_TXT])
        self.btmBtns.btnNext.on_click = self.readCIF_event
        self.btmBtns.btnFunc1.on_click = self.readTXT_event

        setting_exePath = _mgr_settingData.settingData[en.SettingLabel.BUILDER_PATH]
        setting_cifPath = _mgr_settingData.settingData[en.SettingLabel.CIF_PATH]
        setting_txtPath = _mgr_settingData.settingData[en.SettingLabel.TXT_PATH]
        if setting_exePath != "None":
            self.pickBuilder.path_change(setting_exePath)
        if setting_cifPath != "None":
            self.pickCIF.path_change(setting_cifPath)
        if setting_txtPath != "None":
            self.pickTXT.path_change(setting_txtPath)

    def readCIF_event(self, e:ft.ControlEvent):
        pickedEXE_path = self.pickBuilder.pickedPath
        pickedCIF_path = self.pickCIF.pickedPath
        if pickedEXE_path is None:
            raise ValueError("Builder.exe path is not selected.")
        else:
            _mgr_settingData.change_setting(en.SettingLabel.BUILDER_PATH, str(pickedEXE_path.resolve()))
        if pickedCIF_path is None:
            raise ValueError("CIF path is not selected.")
        else:
            _mgr_settingData.change_setting(en.SettingLabel.CIF_PATH, str(pickedCIF_path.resolve()))
            _mgr_cellData.read_cellData(pickedCIF_path)
            _app_mainFrame.tab1.insert_cell_data()
        _app_mainFrame.tab_change(en.TabIdx.CIF_PREVIEW)

    def readTXT_event(self, e:ft.ControlEvent):
        pickedEXE_path = self.pickBuilder.pickedPath
        pickedTXT_path = self.pickTXT.pickedPath
        if pickedEXE_path is None:
            raise ValueError("Builder.exe path is not selected.")
        else:
            _mgr_settingData.change_setting(en.SettingLabel.BUILDER_PATH, str(pickedEXE_path.resolve()))
        if pickedTXT_path is None:
            raise ValueError("TXT path is not selected.")
        else:
            _mgr_settingData.change_setting(en.SettingLabel.TXT_PATH, str(pickedTXT_path.resolve()))
            _mgr_cellData.read_cellData(pickedTXT_path)
            _app_mainFrame.tab1.insert_cell_data()
        _app_mainFrame.tab_change(en.TabIdx.CIF_PREVIEW)

class Tab1_CIFPreview(itf.Rgt_tab_1_CIFPreview):
    def __init__(self):
        super().__init__()
        self.selectedRows:List[str] = []
        self.saveFPicker:ft.FilePicker
        self.savedPath:Path

    def set_init(self):
        self.saveFPicker = _mgr_filePickers[en.FilePickerIdx.SAVE_TXT]
        self.saveFPicker.on_result = self.pick_files_result
        self.dataName.on_blur = self.txtf_dataName_on_blur

        self.btmBtns.btnNext.on_click = self.save_go_cellData_event
        self.btmBtns.btnFunc1.on_click = self.save_func1_cellData_event
        self.btmBtns.btnFunc2.on_click = self.row_selected_clear_event

    def insert_cell_data(self):
        cellData = _mgr_cellData.cellData
        if cellData[en.CellDataLbl.STATE.value] != "data_picked":
            raise ValueError("This cellData is not picked.")
        self.atomsTable.rows.clear()
        table_row:ft.DataRow
        for _lbl in cellData:
            if re.match(r'atoms#\d+', _lbl):
                table_row = ft.DataRow(cells=[], data=_lbl, on_select_changed=self.row_select_event)
                for _data in cellData[_lbl].split(ATOMS_SPLIT):
                    table_row.cells.append(ft.DataCell(ft.Text(value=_data)))
                self.atomsTable.rows.append(table_row)
                continue
            for _txtf in self.tabItems:
                if not isinstance(_txtf, itf.Tab_txtf_CellData): continue
                if _lbl == _txtf.cellDataLbl.value:
                    _txtf.value = cellData[_lbl]
                    break
        self.update()


    def row_select_event(self, e:ft.ControlEvent):
        clicked_row = e.control
        if not isinstance(clicked_row, ft.DataRow): pass
        else:
            if clicked_row.selected:
                if clicked_row.data in self.selectedRows:
                    self.selectedRows.remove(clicked_row.data)
            else:
                self.selectedRows.append(clicked_row.data)
            clicked_row.selected = not clicked_row.selected
        print(self.selectedRows)
        self.update()

    def txtf_dataName_on_blur(self, e:ft.ControlEvent):
        txtf_value = e.control.value
        if txtf_value is None or txtf_value.strip() is False:
            if _mgr_cellData.cellData[en.CellDataLbl.STATE.value] == "data_picked":
                txtf_value = _mgr_cellData.cellData[en.CellDataLbl.DATA_NAME.value]
            else:
                txtf_value = ''
        else:
            _mgr_cellData.cellData[en.CellDataLbl.DATA_NAME.value] = txtf_value
        self.update()

    def row_selected_clear_event(self, e:ft.ControlEvent):
        if len(self.atomsTable.rows) == 0: return
        for _delLbl in self.selectedRows:
            for _row in self.atomsTable.rows:
                if _row.data == _delLbl:
                    self.atomsTable.rows.remove(_row)
        self.update()

    def commit_cellData(self, save_path:Optional[Path]=None):
        if self.dataName.value is None:
            raise ValueError("This tab's data is not completed.")
        commit_cellData = itf.App_dict_CellData()
        commit_cellData[en.CellDataLbl.STATE.value] = "data_picked"
        for _txtf in self.tabItems:
            if not isinstance(_txtf, itf.Tab_txtf_CellData): continue
            #if _txtf.cellDataLbl.value in commit_cellData:
            #    print(_txtf.value)
            commit_cellData[_txtf.cellDataLbl.value] = _txtf.value
        for _row in self.atomsTable.rows:
            atoms_value:List[str] = []
            for _cell in _row.cells:
                atoms_value.append(_cell.content.value)
            commit_cellData[en.CellDataLbl.ATOMS.value] = ATOMS_SPLIT.join(atoms_value)
        _mgr_cellData.commit_save_cellData(commit_cellData, save_path)

    def pick_files_result(self, e:ft.FilePickerResultEvent):
        if e.path:
            if re.match('.*txt',e.path):
                self.savedPath = Path(e.path)
            else:
                self.savedPath = Path(e.path+".txt")
            self.savedPath.touch()
            print(self.savedPath)
            self.commit_cellData(self.savedPath)
        self.update()

    def save_func1_cellData_event(self, e:ft.ControlEvent):
        if self.dataName.value is None or self.dataName.value == '':
            raise ValueError("This tab's data is not completed.")
        self.saveFPicker.save_file(
            allowed_extensions=['txt'],
            file_name=self.dataName.value
        )
        self.update()

    def save_go_cellData_event(self, e:ft.ControlEvent):
        pass


class Tab3_BuilderResult(itf.Rgt_tab_3_BuilderResult):
    def __init__(self):
        super().__init__()


class AppMainFrame(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
        )
        self.leftTabChBar = itf.Left_box_TabChangeBar()
        self.tab99 = itf.Rgt_tab_99_PlaceHolder()
        self.tab0 = Tab0_CIFSelect()
        self.tab1 = Tab1_CIFPreview()
        self.tab2 = itf.Rgt_tab_2_AppLogs()
        self.tab3 = itf.Rgt_tab_3_BuilderResult()
        self.tab4 = itf.Rgt_tab_4_MISelect()
        self.tab5 = itf.Rgt_tab_5_GJFPreview()
        self.rgtTabs = ft.Stack(
            expand=3,
            controls=[
                self.tab99,
                self.tab2,
                self.tab0,
                self.tab1,
                self.tab3,
                self.tab4,
                self.tab5,
            ]
        )
        self.content = ft.Row(
            expand=True,
            controls=[
                self.leftTabChBar,
                self.rgtTabs,
            ]
        )

        self.rgtTabs.data = self.tab_change

    def set_init(self):
        self.leftTabChBar.set_tabBtn_on_click(self._left_tabBtn_event)
        self.tab0.set_init()
        self.tab1.set_init()

    def tab_change(self, to_tab_idx:en.TabIdx):
        for _tab in self.rgtTabs.controls:
            if not isinstance(_tab, itf.Rgt_col_TabBase): continue
            if _tab.tabIdx == to_tab_idx: _tab.visible = True
            elif _tab.tabIdx == 99: pass
            elif _tab.tabIdx == 2: pass
            else: _tab.visible = False
        self.update()
    def _left_tabBtn_event(self, e:ft.ControlEvent):
        if not isinstance(e.control, itf.Left_btn_TabChange): return
        self.tab_change(e.control.tabIdx)
        self.update()


class App_ExitConfirmDlg(itf.App_ExitConfirmDlg):
    def __init__(self):
        super().__init__()

    def yes_clicked(self, e):
        self.page.close(self)
        #!ここに終了時動作
        self.page.window.destroy()

def main(page: ft.Page):
    page.title = "Make CI Support App"
    page.window.width = 800
    page.window.height = 605
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def window_close_event(e):
        if e.data == 'close':
            page.open(App_ExitConfirmDlg())
            page.update()
    page.window.prevent_close = True
    page.window.on_event = window_close_event

    _mgr_settingData.read_setting()
    print(_mgr_settingData.settingData)
    for _name in _mgr_filePickers:
        page.overlay.append(_mgr_filePickers[_name])
    page.update()

    #appMainFrame = AppMainFrame()
    page.add(_app_mainFrame)
    page.window.center()
    page.update()


    _app_mainFrame.set_init()
    page.update()

if __name__ == '__main__':
    _mgr_cellData = Mgr_CellData()
    _mgr_settingData = Mgr_SettingData()
    _mgr_filePickers = Mgr_FilePickers()
    _app_mainFrame = AppMainFrame()
    ft.app(target=main)
    """
    test_mgr_cif = Mgr_CellData()
    test_mgr_cif.read_cellData(Path("C:\\Users\\asufa\\OneDrive\\ドキュメント\\Python\\MakeCiSupport\\datatext\\outpuuuut.txt"))
    for _line in test_mgr_cif.cellData:
        print(f'{_line} : {test_mgr_cif.cellData[_line]}')
    print(test_mgr_cif.savedPath)
    #print(os.getcwd())
    """