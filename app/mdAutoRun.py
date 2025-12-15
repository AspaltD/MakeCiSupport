from pywinauto import Application, timings
from win32gui import GetForegroundWindow
import pyautogui as pag
from typing import List
import time
import frmAppWindow as frm
import mdEnumClass as en
from pathlib import Path

class Ci_AutoRun():
    def __init__(self):
        self.stopRun:bool = False

    def auto_atom_info_insert(self, builder_path:Path, file_data:frm.FileData):
        insertFileData = file_data
        if insertFileData.search_get_value_single(en.CellDataLabel.FILE_NAME) is None: return

        timings.Timings.after_clickinput_wait = 0
        timings.Timings.after_setcursorpos_wait = 0
        timings.Timings.after_button_click_wait = 0

        app = Application(backend="uia")

        if self.stopRun: return
        #既存ならconnect，新規ならstart
        try:
            app.connect(title="CAESAR / Builder")
            print("app_connect")
        except:
            app = app.start(str(builder_path))
            print("app_start")

        main_win = app.window(title="CAESAR / Builder", control_type="Window")
        main_win.wrapper_object()
        main_win.set_focus()
        #main_win.move_window(x=-100, y=-100)
        print("main_win got.")

        if self.stopRun: return
        main_win.type_keys('%f')
        main_win.type_keys('n')

        if self.stopRun: return
        crystal_dlg = main_win.child_window(title="Define Crystal Structure",control_type="Window")
        crystal_dlg.wrapper_object()
        #crystal_dlg.wait("exists", timeout=3)
        #crystal_dlg.set_focus()
        print("crystal_dlg opened.")

        #?ここから格子情報の入力
        if self.stopRun: return
        #title
        crystal_dlg.type_keys(insertFileData.search_get_value_single(en.CellDataLabel.FILE_NAME)[-1])
        #Space Group
        combo2 = crystal_dlg.child_window(auto_id="1214", control_type="ComboBox").wrapper_object()
        #! ここで格子グループの選択。現状光ストレージの格子専用
        if insertFileData.search_get_value_single(en.CellDataLabel.SPACE_GROUP_IT_NUM)[-1] != "14": return
        if insertFileData.search_get_value_single(en.CellDataLabel.SPACE_GROUP_NAME)[-1] != "P_1_21/c_1":return
        spaceGroup = "P2(1)/C #14 AXIS B CHOICE 1"
        combo2.select(spaceGroup)
        print(f"Space Group: {spaceGroup}")
        #格子定数
        if self.stopRun: return
        crystal_dlg.child_window(
            title="a:",
            control_type="Edit"
        ).set_edit_text(insertFileData.search_get_value_branch(en.CellDataLabel.CELL_LENGTH, "a")[-1])
        pag.press('tab')
        pag.write(insertFileData.search_get_value_branch(en.CellDataLabel.CELL_LENGTH, "b")[-1])
        pag.press('tab')
        pag.write(insertFileData.search_get_value_branch(en.CellDataLabel.CELL_LENGTH, "c")[-1])
        pag.press('tab')
        pag.write(insertFileData.search_get_value_branch(en.CellDataLabel.CELL_ANGLE, "beta")[-1])
        print("insert cell info.")

        #原子座標
        if self.stopRun: return
        crystal_dlg.child_window(auto_id="1231", control_type="Button").click()
        atom_dlg = crystal_dlg.child_window(title="Atom Positions",control_type="Window")
        atom_dlg.wrapper_object()
        #atom_dlg.wait("exists", timeout=3)
        print("atom_dlg opened")
            #下スクロールボタンの座標を取得
        atom_dlg.child_window(title="1 行下", auto_id="DownButton", control_type="Button").click_input()
        x_down,y_down = pag.position()
        print(f'x_down: {x_down}, y: {y_down}')
        if self.stopRun: return
        atom_dlg_handle = atom_dlg.handle
        n: int = 1
        atomList:List[FileData_Value] = insertFileData.search_get_value_atoms()
        for atoms in atomList:
            if self.stopRun: return
            if atom_dlg_handle != GetForegroundWindow(): return
            for i in range(0,6):
                pag.write(atoms[i])
                pag.press('tab')
            n += 1
            if n == 11:
                pag.click(x_down,y_down,clicks=11)
                pag.press('tab',2)
                n = 1
            print(atoms)
        print("Atoms insert fin.")
        time.sleep(0.2)
        pag.press('enter')
        pag.press('tab',4)
        time.sleep(0.2)
        pag.press('enter')
        print("AutoRun completed.")




if __name__ == '__main__':
    testFile = frm.FileData()
    testFile.read_cif_file(Path("C:/Users/asufa/OneDrive/デスクトップ/test_autored.cif"))
    testCi = Ci_AutoRun()
    testCi.auto_atom_info_insert(builder_path=Path("C:/Program Files (x86)/PrimeColor Software/Caesar 1.0/bin/builder.exe"), file_data=testFile)