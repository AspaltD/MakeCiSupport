from pywinauto.application import Application
import pprint

# uia バックエンドを指定してメモ帳を起動
app = Application(backend="uia")
app.start("C:/Program Files (x86)/PrimeColor Software/Caesar 1.0/bin/builder.exe")
app.connect(title="CAESAR / Builder")

#? ↓コントロールの情報取得用の出力コマンド
#app.Builder.print_control_identifiers(depth=1,filename="C:/Users/asufa/OneDrive/デスクトップ/Children_output2.txt")

main_win = app.window(title_re=".*Builder")
main_win.wait('visible')
print("hello builder!")

main_win.menu_select("File->New")
crystal_dlg = main_win.child_window(title="Define Crystal Structure",control_type="Window")
#!crystal_dlg.wait('visible')
#crystal_dlg.print_control_identifiers(filename="C:/Users/asufa/OneDrive/デスクトップ/Crystal_output.txt")
print("hello crystal!!")
"""
#?コンボボックス1の選択で2の選択肢が増減する関係か1で.select()すると動作が不安定だったので2のみで指定している。
#combo1 = crystal_dlg.child_window(auto_id="1212", control_type="ComboBox")
combo2 = crystal_dlg.child_window(auto_id="1214", control_type="ComboBox")
#combo1.select("monoclinic")
space_group = "P2(1)/C #14 AXIS B CHOICE 1"
combo2.select(space_group)
print(f"Space Group: {space_group}")

crystal_dlg.child_window(title="a:", control_type="Edit").set_edit_text("7.5317")
crystal_dlg.child_window(title="b:", control_type="Edit").set_edit_text("11.3884")
crystal_dlg.child_window(title="c:", control_type="Edit").set_edit_text("22.3365")
crystal_dlg.child_window(title="beta:", control_type="Edit").set_edit_text("98.077")
print("insert cell info.")


"""
crystal_dlg.Button4.click()
#crystal_dlg["Atom Positions..."].click()
atom_dlg = crystal_dlg.child_window(title="Atom Positions",control_type="Window")
#!atom_dlg.wait('visible')
#atom_dlg.print_control_identifiers(filename="C:/Users/asufa/OneDrive/デスクトップ/atoms_output.txt")
print("hello atom!!!")

#atom_list_down = atom_dlg.child_window(auto_id="1491", control_type="ScrollBar").child_window(title="1 行下", auto_id="DownButton", control_type="Button")
atom_list_down = atom_dlg.child_window(auto_id="1491", control_type="ScrollBar").child_window(title="下へドラッグ", auto_id="DownPageButton", control_type="Button")
print(atom_list_down.class_name)
for i in range(3):
    atom_list_down.click()
    print(i)


"""
atom_dlg.Close.click()
crystal_dlg.Cancel.click()
main_win.wait("enabled")
main_win.close()
print("App_Test Completed!!!!!!!!!!!!!!")
"""