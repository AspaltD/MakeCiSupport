import flet as ft
import logging
import os
from pathlib import Path
from typing import Optional,List,Dict
import re
import copy

import enEnums as en
import frmInterfaces as itf
import mdAutoRun as auto


LATEST_VER_TYPE = en.AppVerType.BETA
LATEST_VER_NUM = 6.0
ATOMS_SPLIT = "_,_"
_mgr_cellData:Mgr_CellData
_mgr_settingData:Mgr_SettingData
_mgr_filePickers:Mgr_FilePickers
_mgr_gjfData:Mgr_GJFData
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
                    valueData = re.sub(r"\(\d+\)", "", valueData)
                    valueData = valueData.strip("'")
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
            #if savePath.is_file():
            if savePath.suffix[1:] != "txt":
                raise ValueError("This path's suffix is not true.")
            #else:
            #    raise ValueError("This path is not complete.")
        with open(savePath, mode='w') as f:
            f.write("MakeCi_output\n")
            for _line in self.cellData:
                if _line == en.CellDataLbl.STATE.value: continue
                f.write(f'{_line}   {self.cellData[_line]}\n')
        self.savedPath = savePath

    def commit_save_cellData(self, new_cellData:itf.App_dict_CellData, save_path:Optional[Path]=None):
        if new_cellData[en.CellDataLbl.STATE.value] != 'data_picked':
            raise ValueError("cellData is not picked.")
        self.last_cellData = copy.deepcopy(self.cellData)
        self.cellData = new_cellData
        print("saved")
        self.save_cellData(save_path)

class Mgr_FilePickers(Dict[en.FilePickerIdx, ft.FilePicker]):
    def __init__(self):
        super().__init__()
        for _name in en.FilePickerIdx:
            self[_name] = ft.FilePicker()

class Mgr_GJFData():
    def __init__(self):
        self.DFLT_BASE_GJF_PATH = Path("./datatext/default.gjf")
        self.DFLT_SAVE_GJF_PATH = Path("./datatext/outpuuuut.gjf")
        self.base_gjfData:itf.App_List_GJFData
        self.saved_gjfData:itf.App_List_GJFData
        self.saved_path:Path
        self.picked_mi_path:Path

    def set_init(self):
        if not self.DFLT_BASE_GJF_PATH.is_file():
            self._make_dflt_base_gjf_file()
        if _mgr_settingData.settingData[en.SettingLabel.GJF_BASE_PATH] == "None":
            base_gjf_path = self.DFLT_BASE_GJF_PATH
        else:
            base_gjf_path = Path(_mgr_settingData.settingData[en.SettingLabel.GJF_BASE_PATH])
        self.read_base_gjf(base_gjf_path)
        #print(self.base_gjfData)

    def _make_dflt_base_gjf_file(self):
        if not Path('./datatext').is_dir():
            Path.mkdir(Path('./datatext'))
        self.DFLT_BASE_GJF_PATH.touch()
        self.DFLT_SAVE_GJF_PATH.touch()
        self.base_gjfData = itf.App_List_GJFData()
        self.base_gjfData.append("%chk=C:/Users/Owner/Desktop/Data/Yoshida/def/default.chk")
        self.base_gjfData.append("# wb97xd/lanl2dz pop=full geom=connectivity")
        self.base_gjfData.append("\n")
        self.base_gjfData.append("Title Card Required")
        self.base_gjfData.append("\n")
        self.base_gjfData.append("0 1")
        self.save_gjf_data(self.DFLT_BASE_GJF_PATH)

    def save_gjf_data(self, save_gjf_path:Optional[Path]=None):
        save_path = save_gjf_path
        if save_path is None:
            save_path = self.DFLT_SAVE_GJF_PATH
        else:
            if save_path.suffix[1:] != "gjf":
                raise ValueError("This path's suffix is not true.")
        with open(save_path, mode='w') as f:
            for _line in self.saved_gjfData:
                f.write(f'{_line}\n')
        self.saved_Path = save_path

    def read_base_gjf(self, base_gjf_path:Optional[Path]=None):
        read_path = base_gjf_path
        if read_path is None:
            read_path = self.DFLT_BASE_GJF_PATH
        else:
            if read_path.suffix[1:] != "gjf":
                raise ValueError("This path's suffix is not true.")
        self.base_gjfData = itf.App_List_GJFData()
        with open(read_path) as f:
            for _line in f:
                _line = _line.rstrip()
                self.base_gjfData.append(_line)
                if len(self.base_gjfData) >= 6: break

    def read_mi_to_gjf(self, read_mi_path:Path):
        mi_path = read_mi_path
        if not mi_path.is_file():
            raise ValueError("This mi path is not true.")
        if mi_path.suffix[1:] != "mi":
            raise ValueError("This path's suffix is not true.")
        if len(self.base_gjfData) <= 4:
            self.read_base_gjf()
        self.picked_mi_path = mi_path
        self.saved_gjfData = copy.deepcopy(self.base_gjfData)
        i = -1
        with open(mi_path) as f:
            for _line in f:
                i += 1
                _line = _line.strip()
                if not _line: continue
                if i >= 450:
                    raise IndexError("readline is over.(450 lines)")
                _line_value = _line.split()
                if _line_value[0] != "POS": continue
                _line_value[1] = _line_value[1].split(sep='-')[0]
                if len(_line_value[1]) < 2:
                    _line_value[1] += '_'
                for _n in range(2, 5):
                    while len(_line_value[_n]) < 10:
                        _line_value[_n] = '_' + _line_value[_n]
                _line_value_comp = '  '.join(_line_value[1:])
                self.saved_gjfData.append(_line_value_comp.replace('_', ' '))


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
            _app_mainFrame.tab3.txtf_cifName.value = str(pickedCIF_path.resolve())
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
            _app_mainFrame.tab3.txtf_cifName.value = str(pickedTXT_path.resolve())
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
        self.commit_cellData()
        _app_mainFrame.start_ins_ci_auto()

class Tab3_BuilderResult(itf.Rgt_tab_3_BuilderResult):
    def __init__(self):
        super().__init__()

class Tab4_MISelect(itf.Rgt_tab_4_MISelect):
    def __init__(self):
        super().__init__()

    def set_init(self):
        self.pickGJF.set_picker_init(_mgr_filePickers[en.FilePickerIdx.PICK_GJF])
        self.pickMI.set_picker_init(_mgr_filePickers[en.FilePickerIdx.PICK_MI])
        self.pickGJF._filePicker.on_result = self._gjfPicker_picked_event
        self.btmBtns.btnNext.on_click = self.read_mi_event

    def _gjfPicker_picked_event(self, e:ft.FilePickerResultEvent):
        if e.files: self.pickGJF.path_change(e.files[0].path)
        _mgr_gjfData.read_base_gjf(self.pickGJF.pickedPath)
        self.listV_baseGJF.controls = []
        for _line in _mgr_gjfData.base_gjfData:
            self.listV_baseGJF.controls.append(
                ft.TextField(
                    value=_line,
                    read_only=True,
                    dense=True,
                    border=ft.InputBorder.NONE
                )
            )
        self.update()

    def read_mi_event(self, e:ft.ControlEvent):
        pickedMI_path = self.pickMI.pickedPath
        pickedGJF_path = self.pickGJF.pickedPath
        if pickedGJF_path is None:
            raise ValueError("Base_GJF path is not selected.")
        else:
            _mgr_settingData.change_setting(en.SettingLabel.GJF_BASE_PATH, str(pickedGJF_path.resolve()))
        if pickedMI_path is None:
            raise ValueError("MI path is not selected.")
        else:
            _mgr_settingData.change_setting(en.SettingLabel.MI_PATH, str(pickedMI_path.resolve()))
            _mgr_gjfData.read_mi_to_gjf(pickedMI_path)
            _mgr_gjfData.save_gjf_data()
            _app_mainFrame.tab5.ins_gjf_preview()
        _app_mainFrame.tab_change(en.TabIdx.GJF_PREVIEW)

class Tab5_GJFPreview(itf.Rgt_tab_5_GJFPreview):
    def __init__(self):
        super().__init__()
        self.saveFPicker_gjf:ft.FilePicker
        self.savedPath_gjf:Path

    def set_init(self):
        self.saveFPicker_gjf = _mgr_filePickers[en.FilePickerIdx.SAVE_GJF]
        self.saveFPicker_gjf.on_result = self._pick_files_result
        self.btmBtns.btnNext.on_click = self._save_next_gjfData_event

    def ins_gjf_preview(self):
        self.listV_GJFPre.controls.clear()
        for _line in _mgr_gjfData.saved_gjfData:
            self.listV_GJFPre.controls.append(
                ft.TextField(
                    value=_line,
                    read_only=True,
                    dense=True,
                    border=ft.InputBorder.NONE
                )
            )

    def _pick_files_result(self, e:ft.FilePickerResultEvent):
        if e.path:
            if re.match('.*gjf', e.path):
                gjfPath = Path(e.path)
            else:
                gjfPath = Path(e.path+".gjf")
            _mgr_gjfData.save_gjf_data(gjfPath)
            self.savedPath_gjf = gjfPath
        self.update()

    def _save_next_gjfData_event(self, e:ft.ControlEvent):
        if len(self.listV_GJFPre.controls) == 0:
            raise ValueError("There are non gjf data.")
        self.saveFPicker_gjf.save_file(
            allowed_extensions=['gjf'],
            file_name=_mgr_gjfData.picked_mi_path.stem
        )


class AppMainFrame(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
        )
        self.ciAuto = auto.Ci_AutoRun(ATOMS_SPLIT)
        self.leftTabChBar = itf.Left_box_TabChangeBar()
        self.tab99 = itf.Rgt_tab_99_PlaceHolder()
        self.tab0 = Tab0_CIFSelect()
        self.tab1 = Tab1_CIFPreview()
        self.tab2 = itf.Rgt_tab_2_AppLogs()
        self.tab3 = itf.Rgt_tab_3_BuilderResult()
        self.tab4 = Tab4_MISelect()
        self.tab5 = Tab5_GJFPreview()
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
        self.tab4.set_init()
        self.tab5.set_init()

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

    def start_ins_ci_auto(self):
        exe_path = self.tab0.pickBuilder.pickedPath
        if exe_path is None:
            raise ValueError("Builder.exe path is not enter.")
        self.tab_change(en.TabIdx.APP_LOG)
        self.ciAuto.auto_atom_info_insert(exe_path, _mgr_cellData.cellData)
        self.tab_change(en.TabIdx.BUILDER_RESULT)


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
    _mgr_gjfData.set_init()
    #print(_mgr_settingData.settingData)
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
    _mgr_gjfData = Mgr_GJFData()
    _app_mainFrame = AppMainFrame()
    ft.app(target=main)