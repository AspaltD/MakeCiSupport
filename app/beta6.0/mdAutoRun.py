from pywinauto import Application, timings
from win32gui import GetForegroundWindow
import pyautogui as pag
from typing import List
import time
from pathlib import Path

import frmInterfaces as itf
import enEnums as en

class Ci_AutoRun():
    def __init__(self, atoms_split:str):
        self.stopRun:bool = False
        self._ins_cellData:itf.App_dict_CellData
        self.ATOMS_SPLIT = atoms_split

    def auto_atom_info_insert(self, builder_path:Path, ins_cell_data:itf.App_dict_CellData):
        self._ins_cellData = ins_cell_data

        timings.Timings.after_clickinput_wait = 0
        timings.Timings.after_setcursorpos_wait = 0
        timings.Timings.after_button_click_wait = 0

        app = Application(backend="uia")

        if self.stopRun: return
        #既存ならconnect，新規ならstart
        try:
            app.connect(title="CAESAR / Builder")
        except:
            app = app.start(str(builder_path))

        main_win = app.window(title="CAESAR / Builder", control_type="Window")
        main_win.wrapper_object()
        main_win.set_focus()
        #main_win.move_window(x=-100, y=-100)

        if self.stopRun: return
        main_win.type_keys('%f')
        main_win.type_keys('n')

        if self.stopRun: return
        crystal_dlg = main_win.child_window(title="Define Crystal Structure",control_type="Window")
        crystal_dlg.wrapper_object()
        #crystal_dlg.wait("exists", timeout=3)
        #crystal_dlg.set_focus()

        #?ここから格子情報の入力
        if self.stopRun: return
        #title
        crystal_dlg.type_keys(self._ins_cellData[en.CellDataLbl.DATA_NAME.value])
        #Space Group
        combo2 = crystal_dlg.child_window(auto_id="1214", control_type="ComboBox").wrapper_object()
        #! ここで格子グループの選択。現状光ストレージの格子専用
        rightStorage:bool = True
        if self._ins_cellData[en.CellDataLbl.SPACE_G_IT_NUM.value] != "14": rightStorage = False
        if self._ins_cellData[en.CellDataLbl.SPACE_G_NAME.value] != "P_1_21/c_1": rightStorage = False
        if rightStorage: spaceGroup = "P2(1)/C #14 AXIS B CHOICE 1"
        else: spaceGroup = "unknown"
        combo2.select(spaceGroup)
        #格子定数
        if self.stopRun: return
        crystal_dlg.child_window(
            title="a:",
            control_type="Edit"
        ).set_edit_text(self._ins_cellData[en.CellDataLbl.CELL_LEN_A.value])
        pag.press('tab')
        pag.write(self._ins_cellData[en.CellDataLbl.CELL_LEN_B.value])
        pag.press('tab')
        pag.write(self._ins_cellData[en.CellDataLbl.CELL_LEN_C.value])
        if not rightStorage:
            pag.press('tab')
            pag.write(self._ins_cellData[en.CellDataLbl.CELL_ANGLE_A.value])
        pag.press('tab')
        pag.write(self._ins_cellData[en.CellDataLbl.CELL_ANGLE_B.value])
        if not rightStorage:
            pag.press('tab')
            pag.write(self._ins_cellData[en.CellDataLbl.CELL_ANGLE_C.value])

        #原子座標
        if self.stopRun: return
        crystal_dlg.child_window(auto_id="1231", control_type="Button").click()
        atom_dlg = crystal_dlg.child_window(title="Atom Positions",control_type="Window")
        atom_dlg.wrapper_object()
        #atom_dlg.wait("exists", timeout=3)
            #下スクロールボタンの座標を取得
        atom_dlg.child_window(title="1 行下", auto_id="DownButton", control_type="Button").click_input()
        x_down,y_down = pag.position()
        if self.stopRun: return
        atom_dlg_handle = atom_dlg.handle
        n: int = 1

        atomsList:List[str] = self._ins_cellData.get_atoms_list()
        for _atom in atomsList:
            atom_data = _atom.split(self.ATOMS_SPLIT)
            if self.stopRun: return
            if atom_dlg_handle != GetForegroundWindow(): return
            for i in range(0,6):
                pag.write(atom_data[i])
                pag.press('tab')
            n += 1
            if n == 11:
                pag.click(x_down,y_down,clicks=11)
                pag.press('tab',2)
                n = 1
        time.sleep(0.2)
        pag.press('enter')
        if rightStorage:
            pag.press('tab',4)
            time.sleep(0.2)
            pag.press('enter')




if __name__ == '__main__':
    pass