from pywinauto.application import Application
import os

testReadPath = "C:/Users/asufa/OneDrive/デスクトップ/1006_1h_def/outpuuuut.txt"

atoms_info = [["Read Atoms"]]

with open(testReadPath) as f:
    i: int = 0
    print("\n")
    for line in f:
        line_s = line.strip()
        match i:
            case 0:
                if not line_s == "MakeCi_output":
                    print("This file is not output_file.")
                    exit()
            case 3:
                atoms_info_fragments = line_s.split()
                spaceGroup = '_'.join(atoms_info_fragments[1:])
                atoms_info.append([atoms_info_fragments[0],spaceGroup])
            case _:
                atoms_info_fragments = line_s.split()
                atoms_info.append([])
                for fragment in atoms_info_fragments:
                    atoms_info[-1].append(fragment)
        i += 1
    print(f"end_line: {i}")

for n in atoms_info:
    print(n)



app = Application(backend="uia")
app.start("C:/Program Files (x86)/PrimeColor Software/Caesar 1.0/bin/builder.exe")
app.connect(title="CAESAR / Builder")

main_win = app.window(title="CAESAR / Builder")
#main_win.wait('visible')
print("hello builder!")

main_win.menu_select("File->New")
crystal_dlg = main_win.child_window(title="Define Crystal Structure",control_type="Window")
print("hello crystal!!")

#?ここから格子定数の入力
crystal_dlg.child_window(title="Title", auto_id="1201", control_type="Edit").set_edit_text(atoms_info[1][-1])

combo2 = crystal_dlg.child_window(auto_id="1214", control_type="ComboBox")
if atoms_info[2][1] == "14" and atoms_info[3][1] == "P_1_21/c_1":
    space_group:str = "P2(1)/C #14 AXIS B CHOICE 1"
    combo2.select(space_group)
    print(f"Space Group: {space_group}")

crystal_dlg.child_window(title="a:", control_type="Edit").set_edit_text(atoms_info[4][1])
crystal_dlg.child_window(title="b:", control_type="Edit").set_edit_text(atoms_info[5][1])
crystal_dlg.child_window(title="c:", control_type="Edit").set_edit_text(atoms_info[6][1])
crystal_dlg.child_window(title="beta:", control_type="Edit").set_edit_text(atoms_info[8][1])
print("insert cell info.")

crystal_dlg.child_window(title="Atom Positions...", auto_id="1231", control_type="Button").click()
atom_dlg = crystal_dlg.child_window(title="Atom Positions",control_type="Window")
print("hello atom!!!")

atom_list_down = atom_dlg.child_window(title="1 行下", auto_id="DownButton", control_type="Button")

for atoms in atoms_info[10:11]:
    atom_dlg.child_window(auto_id="1421", control_type="Edit").set_edit_text(atoms[0])
    atom_dlg.child_window(auto_id="1431", control_type="Edit").set_edit_text(atoms[1])
    atom_dlg.child_window(auto_id="1405", control_type="Edit").set_edit_text(atoms[2])
    atom_dlg.child_window(auto_id="1451", control_type="Edit").set_edit_text(atoms[3])
    atom_dlg.child_window(auto_id="1461", control_type="Edit").set_edit_text(atoms[4])
    atom_dlg.child_window(auto_id="1471", control_type="Edit").set_edit_text(atoms[5])

    atom_list_down.click_input()
    atom_list_down.click_input()

print("Atoms insert fin.")
atom_dlg.child_window(title="Close", auto_id="1", control_type="Button").click()
crystal_dlg.child_window(title="OK", auto_id="1", control_type="Button").click()
print("AutoRun completed.")