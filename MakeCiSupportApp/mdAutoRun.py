from pywinauto import Application
import pyautogui as pag
from typing import List
from frmAppWindow import FileData, FileData_Value,Enum_CellDataLabel
from pathlib import Path

def auto_atom_info_insert(builder_path:Path, file_data:FileData):
    insertFileData = file_data
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

    #?ここから格子定数の入力
    #title
    crystal_dlg.type_keys(insertFileData[1][-1])
    #Space Group
    combo2 = crystal_dlg.child_window(auto_id="1214", control_type="ComboBox")





if __name__ == '__main__':
    auto_atom_info_insert(builder_path=Path("C:/Program Files (x86)/PrimeColor Software/Caesar 1.0/bin/builder.exe"), file_data=FileData())