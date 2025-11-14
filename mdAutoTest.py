from pywinauto.application import Application
import pyautogui as pag
import time
import os

testReadPath = "D:/2_Saturn/1113_3/outpuuuut.txt"

atoms_info = [["Read Atoms"]]
def ReadAtomsInfo():
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

def AutoRunSample1():
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
        atom_list_down.click()

    print("Atoms insert fin.")
    atom_dlg.child_window(title="Close", auto_id="1", control_type="Button").click()
    crystal_dlg.child_window(title="OK", auto_id="1", control_type="Button").click()
    print("AutoRun completed.")

def AutoRunSample2():
    app = Application(backend="uia")
    app.start("C:/Program Files (x86)/PrimeColor Software/Caesar 1.0/bin/builder.exe")
    app.connect(title="CAESAR / Builder")

    main_win = app.window(title="CAESAR / Builder", control_type="Window")
    #main_win.wait('visible')
    print("hello builder!")

    main_win.type_keys('%f')
    main_win.type_keys('n')

    crystal_dlg = main_win.child_window(title="Define Crystal Structure",control_type="Window")
    print("hello crystal!!")

    #?ここから格子定数の入力
    #title
    crystal_dlg.type_keys(atoms_info[1][-1])
    #Space Group
    combo2 = crystal_dlg.child_window(auto_id="1214", control_type="ComboBox")
    if atoms_info[2][1] == "14" and atoms_info[3][1] == "P_1_21/c_1":
        space_group:str = "P2(1)/C #14 AXIS B CHOICE 1"
        combo2.select(space_group)
        print(f"Space Group: {space_group}")
    #Cell Info(ある程度早いので未改良)
    crystal_dlg.child_window(title="a:", control_type="Edit").set_edit_text(atoms_info[4][1])
    crystal_dlg.child_window(title="b:", control_type="Edit").set_edit_text(atoms_info[5][1])
    crystal_dlg.child_window(title="c:", control_type="Edit").set_edit_text(atoms_info[6][1])
    crystal_dlg.child_window(title="beta:", control_type="Edit").set_edit_text(atoms_info[8][1])
    print("insert cell info.")

    crystal_dlg.child_window(title="Atom Positions...", auto_id="1231", control_type="Button").click()
    atom_dlg = crystal_dlg.child_window(title="Atom Positions",control_type="Window")
    print("hello atom!!!")

    #下スクロール(スクロールバーの下側の方)
    atom_list_down = atom_dlg.child_window(auto_id="1491", control_type="ScrollBar").child_window(title="1 行下", auto_id="DownButton", control_type="Button")
    #atom_list_down = atom_dlg.child_window(auto_id="1491", control_type="ScrollBar").child_window(title="下へドラッグ", auto_id="DownPageButton", control_type="Button")
    n: int = 1
    for atoms in atoms_info[10:]:
        """
        for i in range(0,6,2):
            #main_win.child_window(title="Define Crystal Structure", control_type="Window").child_window(title="Atom Positions", control_type="Window").type_keys(atoms[i]+'{TAB}', with_tabs=True)
            atom_dlg.type_keys(atoms[i]+'{TAB}'+atoms[i+1]+'{TAB}', with_tabs=True)
        """
        atom_dlg.type_keys(atoms[0]+'{TAB}'+atoms[1]+'{TAB}'+atoms[2]+'{TAB}'+atoms[3]+'{TAB}'+atoms[4]+'{TAB}'+atoms[5]+'{TAB}', with_tabs=True)
        #atom_dlg.type_keys(atoms[3]+'{TAB}'+atoms[4]+'{TAB}'+atoms[5]+'{TAB}', with_tabs=True)

        n += 1
        if n == 10:
            atom_list_down.click_input()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_dlg.type_keys('{TAB}'+'{TAB}'+'{TAB}',with_tabs=True)
            n = 1

    print("Atoms insert fin.")
    atom_dlg.child_window(title="Close", auto_id="1", control_type="Button").click()
    crystal_dlg.child_window(title="OK", auto_id="1", control_type="Button").click()
    print("AutoRun completed.")

def AutoRunSample3():
    app = Application(backend="uia")
    app.start("C:/Program Files (x86)/PrimeColor Software/Caesar 1.0/bin/builder.exe")
    app.connect(title="CAESAR / Builder")

    main_win = app.window(title="CAESAR / Builder", control_type="Window")
    #main_win.wait('visible')
    print("hello builder!")

    main_win.type_keys('%f')
    main_win.type_keys('n')

    crystal_dlg = main_win.child_window(title="Define Crystal Structure",control_type="Window")
    print("hello crystal!!")

    #?ここから格子定数の入力
    #title
    #crystal_dlg.wait('visible')
    #pag.PAUSE = 0.4
    #pag.write(atoms_info[1][-1])
    crystal_dlg.type_keys(atoms_info[1][-1])
    #Space Group
    combo2 = crystal_dlg.child_window(auto_id="1214", control_type="ComboBox")
    if atoms_info[2][1] == "14" and atoms_info[3][1] == "P_1_21/c_1":
        space_group:str = "P2(1)/C #14 AXIS B CHOICE 1"
        combo2.select(space_group)
        print(f"Space Group: {space_group}")
        #Cell Info
        #time.sleep(0.3)
        #pag.press('tab')
        crystal_dlg.child_window(title="a:", control_type="Edit").set_edit_text(atoms_info[4][1])
        for i in range(5,7):
            pag.press('tab')
            pag.write(atoms_info[i][1])
        pag.press('tab')
        pag.write(atoms_info[8][1])
        #crystal_dlg.type_keys('{TAB}'+atoms_info[5][1]+'{TAB}'+atoms_info[6][1]+'{TAB}'+atoms_info[8][1],with_tabs=True)

        """
        crystal_dlg.child_window(title="a:", control_type="Edit").set_edit_text(atoms_info[4][1])
        crystal_dlg.child_window(title="b:", control_type="Edit").set_edit_text(atoms_info[5][1])
        crystal_dlg.child_window(title="c:", control_type="Edit").set_edit_text(atoms_info[6][1])
        crystal_dlg.child_window(title="beta:", control_type="Edit").set_edit_text(atoms_info[8][1])
        """
        print("insert cell info.")

    crystal_dlg.child_window(title="Atom Positions...", auto_id="1231", control_type="Button").click()
    atom_dlg = crystal_dlg.child_window(title="Atom Positions",control_type="Window")
    print("hello atom!!!")

    #下スクロール
    atom_dlg.child_window(auto_id="1491", control_type="ScrollBar").child_window(title="1 行下", auto_id="DownButton", control_type="Button").click_input()
    x_down,y_down = pag.position()
    print(f'x_down: {x_down}, y: {y_down}')
    x_close:int = 0
    y_close:int = 0

    #atom_list_down = atom_dlg.child_window(auto_id="1491", control_type="ScrollBar").child_window(title="下へドラッグ", auto_id="DownPageButton", control_type="Button")
    n: int = 1
    for atoms in atoms_info[10:]:
        for i in range(0,6):
            pag.write(atoms[i])
            pag.press('tab')
        """
        for i in range(0,6,2):
            #main_win.child_window(title="Define Crystal Structure", control_type="Window").child_window(title="Atom Positions", control_type="Window").type_keys(atoms[i]+'{TAB}', with_tabs=True)
            atom_dlg.type_keys(atoms[i]+'{TAB}'+atoms[i+1]+'{TAB}', with_tabs=True)
        """
        #atom_dlg.type_keys(atoms[0]+'{TAB}'+atoms[1]+'{TAB}'+atoms[2]+'{TAB}'+atoms[3]+'{TAB}'+atoms[4]+'{TAB}'+atoms[5]+'{TAB}', with_tabs=True)
        #atom_dlg.type_keys(atoms[3]+'{TAB}'+atoms[4]+'{TAB}'+atoms[5]+'{TAB}', with_tabs=True)

        n += 1
        if n == 11:
            pag.click(x_down,y_down,clicks=11)
            #pag.moveTo(x_down,y_down)
            """
            atom_list_down.click_input()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            atom_list_down.click()
            """
            #atom_dlg.type_keys('{TAB}'+'{TAB}',with_tabs=True)
            """
            if x_close == 0 and y_close == 0:
                x_close,y_close = pag.position()
                print(f'x_close: {x_close}, y: {y_close}')
            """
            pag.press('tab',2)
            n = 1
    print(n)

    print("Atoms insert fin.")
    time.sleep(0.2)
    pag.press('enter')
    #pag.press('tab')
    #pag.press('enter')
    #atom_dlg.child_window(title="Close", auto_id="1", control_type="Button").click()
    pag.press('tab',4)
    time.sleep(0.2)
    pag.press('enter')
    #crystal_dlg.child_window(title="OK", auto_id="1", control_type="Button").click()
    print("AutoRun completed.")


ReadAtomsInfo()
#AutoRunSample1()
#AutoRunSample2()
AutoRunSample3()