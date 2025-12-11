from pywinauto import Application
import pyautogui as pag
from typing import List
import time
from frmAppWindow import FileData, FileData_Value
import mdEnumClass as en
from pathlib import Path

def auto_atom_info_insert(builder_path:Path, file_data:FileData):
    insertFileData = file_data
    if insertFileData.search_get_value_single(en.CellDataLabel.FILE_NAME) is None: return

    app = Application(backend="uia")

    #既存ならconnect，新規ならstart
    try:
        app.connect(title="CAESAR / Builder")
        print("app_connect")
    except:
        app = app.start(str(builder_path))
        print("app_start")

    #メインのダイアログ(ウィンドウ)を取得，最小化対策にset_focus()。
    #ここでwaitを付けてないとうまく動かない。多分コード処理とデータ保持の認識速度の問題？
    #pywinautoのダイアログ取得は「WindowSpecification」という検索条件での仮置きと「WindowWrapper」というホンモノの2状態がある？
    #dlg.wait("exists")により存在を認識できたときに始めてホンモノになる模様
    main_win = app.window(title="CAESAR / Builder", control_type="Window")
    main_win.wait('exists', timeout=5)
    main_win.set_focus()
    print("main_win got.")

    main_win.type_keys('%f')
    main_win.type_keys('n')

    crystal_dlg = main_win.child_window(title="Define Crystal Structure",control_type="Window")
    crystal_dlg.wait("exists", timeout=3)
    #crystal_dlg.set_focus()
    print("crystal_dlg opened.")

    #?ここから格子情報の入力
    #title
    crystal_dlg.type_keys(insertFileData.search_get_value_single(en.CellDataLabel.FILE_NAME)[-1])
    #Space Group
    combo2 = crystal_dlg.child_window(auto_id="1214", control_type="ComboBox")
    #! ここで格子グループの選択。現状光ストレージの格子専用
    if insertFileData.search_get_value_single(en.CellDataLabel.SPACE_GROUP_IT_NUM)[-1] != "14": return
    if insertFileData.search_get_value_single(en.CellDataLabel.SPACE_GROUP_NAME)[-1] != "P_1_21/c_1":return
    spaceGroup = "P2(1)/C #14 AXIS B CHOICE 1"
    combo2.select(spaceGroup)
    print(f"Space Group: {spaceGroup}")
    #格子定数
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
    crystal_dlg.child_window(title="Atom Positions...", auto_id="1231", control_type="Button").click()
    atom_dlg = crystal_dlg.child_window(title="Atom Positions",control_type="Window")
    print("atom_dlg opened")
        #下スクロールボタンの座標を取得
    atom_dlg.child_window(auto_id="1491", control_type="ScrollBar").child_window(title="1 行下", auto_id="DownButton", control_type="Button").click_input()
    x_down,y_down = pag.position()
    print(f'x_down: {x_down}, y: {y_down}')

    n: int = 1
    atomList:List[FileData_Value] = insertFileData.search_get_value_atoms()
    for atoms in atomList:
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
    auto_atom_info_insert(builder_path=Path("C:/Program Files (x86)/PrimeColor Software/Caesar 1.0/bin/builder.exe"), file_data=FileData())