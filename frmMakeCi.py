import flet as ft
import os
import re
from typing import Optional, Dict, List
#import mdAutoTest

#? ファイルピッカーの宣言(コンテンツ内で使いたいのにPageでのOverlay作業が必要なためグローバル変数で宣言)
#! 改善案募集中：ﾌｧｲﾙﾋﾟｯｶｰの同一の機能を同じコンテナ内で使うにはそれぞれで個別のﾌｧｲﾙﾋﾟｯｶｰが必要っぽい。
file_pickers: Dict[str,ft.FilePicker]
fileData: List[List[str]] = [["FileData"]]
settingData: Dict[str,str] = {}

class PlaceHoldeeeer(ft.Placeholder):
    def __init__(self, expand:int=404, color=ft.Colors.random()):
        super().__init__()
        self.data = 99
        if expand == 404:
            self.expand = True
        else:
            self.expand = expand
        self.color = color
class NaviButton(ft.FilledButton):
    def __init__(self, workIdx:int, button_clicked, height=40):
        super().__init__()
        #self.expand = expand
        self.width = 150
        self.height = height
        self.on_click = button_clicked
        self.workIdx = workIdx
        self.text = self.select_text(workIdx)

    def select_text(self, idx:int):
        b_text: str
        match idx:
            case 0:
                b_text = "動作設定"
            case 1:
                b_text = "読取結果"
            case 2:
                b_text = "Builderログ"
            case 3:
                b_text = "Builder動作完了"
            case _:
                b_text = "Null Button"
        return b_text

class NaviDownMark(ft.Text):
    def __init__(self):
        super().__init__()
        self.width = 180
        self.text_align = ft.TextAlign.CENTER
        self.value = "▼"

class NaviBar(ft.Column):
    def __init__(self):
        super().__init__()
        self.width = 180
        self.height = 520
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 0
        self.expand_loose = True
        self.expand = 1
        #self.tight = False
        #self.alignment = ft.MainAxisAlignment.CENTER
        #self.expand = True

class TabBottomButton(ft.FilledButton):
    def __init__(self,buttonClicked, workIdx:int=0):
        super().__init__()
        self.pageIdx = 0
        self.workIdx = workIdx
        self.on_click = buttonClicked
        self.width = 120
        self.change_init(0)

    #? workIdx = 0:Exit, 1:Next

    def change_init(self, toPageIdx:int):
        workIdx = self.workIdx
        if workIdx == 0:
            self.text = "ExitApp"
            return
        elif workIdx == 1:
            self.text = "Next"
        elif workIdx == 2:
            self.text = "OtherFunc"
        elif workIdx == 3:
            self.text = "OtherFunc2"
        else:
            self.text = "--Null--"
            self.disabled = True
        
        match toPageIdx:
            case 0:
                self.pageIdx = 0
                if workIdx == 1:
                    self.text = "ReadCif"
                    self.disabled = False
                elif workIdx == 2:
                    self.visible = False
                elif workIdx == 3:
                    self.visible = False
            case 1:
                self.pageIdx = 1
                if workIdx == 1:
                    self.text = "Save&Go"
                    self.disabled = False
                elif workIdx == 2:
                    self.text = "Save"
                    self.visible = True
                elif workIdx == 3:
                    self.text = "Remove"
                    self.visible = True
            case 2:
                self.pageIdx = 2
                if workIdx == 1:
                    self.text = "Stop"
                    self.disabled = False
                elif workIdx == 2:
                    self.visible = False
                elif workIdx == 3:
                    self.visible = False
            case _:
                self.pageIdx = 99        



class TabContentsContainer(ft.Container):
    def __init__(self, workIdx:int, visible:bool=True):
        super().__init__()
        self.data = workIdx
        self.visible = visible
        self.expand = 10
        self.padding = 10
        #self.height = 540
        self.bgcolor = ft.Colors.LIGHT_BLUE_100
        #self.border = ft.border.all(1,ft.Colors.BLACK)

class FilePickerBar(ft.Row):
    def __init__(self, filePicker:ft.FilePicker, workIdx:int):
        super().__init__()

        self.fileName:str = ""
        self.filePath:str = ""
        self.data = workIdx
        self.fileType:str
        self.fileLabel:str
        self.filePickeeeer = filePicker
        self.filePickeeeer.on_result = self.pick_files_result
        self.file_init_select()
        self.textF_path = ft.TextField(expand=9,hint_text=self.fileLabel,dense=True,on_change=self.value_change)

        self.spacing = 0


        self.controls = [
            self.textF_path,
            ft.FilledButton(expand=1,text="File", on_click=lambda _: self.filePickeeeer.pick_files(allowed_extensions=[self.fileType]))
        ]

    def file_init_select(self):
        match self.data:
            case 0:
                self.fileType = "exe"
                self.fileLabel = "Builder Path"
            case 1:
                self.fileType = "cif"
                self.fileLabel = "'.cif' File Path"
            case 2:
                self.fileType = "txt"
                self.fileLabel = "Output File Path"
            case _:
                self.fileType = "txt"
                self.fileLabel = "404 Path"

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.fileName = e.files[0].name
            self.filePath = e.files[0].path.replace(os.sep, '/')
            print(f"Selected files:name={e.files[0].name}")
            print(f"Selected files:{self.filePath}")
            self.textF_path.value = self.filePath
        self.update()
    
    def value_change(self, e:ft.ControlEvent):
        line:Optional[str] = e.control.value
        if line == "" or line is None:
            self.fileName = ""
            self.filePath = ""
        else:
            if os.path.isfile(line):
                self.fileName = os.path.splitext(os.path.basename(line))[0]
                self.filePath = line
            else:
                self.fileName = ""
                self.filePath = ""
            #print(self.filePath)
        self.update()

class Tab_0_FilePathSelect(TabContentsContainer):
    def __init__(self, visible:bool):
        super().__init__(workIdx=0, visible=visible)
        #global fileData
        self.pick1 = FilePickerBar(file_pickers["builder_pick"],0)
        self.pick2 = FilePickerBar(file_pickers["cif_pick"],1)
        self.pick3 = FilePickerBar(file_pickers["outpuuuut_pick"],2)

        self.content = ft.Column([
            ft.Text("Builder Path"),
            self.pick1,
            ft.Text("'.cif' File Path"),
            self.pick2,
            ft.Text("Output Path"),
            self.pick3
        ])

        if "builder_path" in settingData:
            self.pick1.textF_path.value = settingData["builder_path"]
            self.pick1.fileName = os.path.splitext(os.path.basename(settingData["builder_path"]))[0]
            self.pick1.filePath = settingData["builder_path"]

    def read_output_file(self)->bool:
        global fileData
        fileData.clear()
        fileData = [["FileData_Output"]]
        outputPath = self.pick3.filePath
        if self.pick1.filePath == "":
            print("filePath not enter.")
            return False
        if outputPath == "":
            print("outputPath not enter.")
            return False
        #print(outputPath)
        with open(outputPath) as f:
            i:int = 0
            for line in f:
                lineParts = line.strip()
                match i:
                    case 0:
                        if not lineParts == "MakeCi_output":
                            return False
                    case 3:
                        atomInfo = lineParts.split()
                        spaceGroup = '_'.join(atomInfo[1:])
                        fileData.append([atomInfo[0],spaceGroup])
                    case _:
                        atomInfo = lineParts.split()
                        fileData.append([])
                        for info in atomInfo:
                            fileData[-1].append(info)
                i += 1
            print(f"end_line: {i}")

        for n in fileData:
            print(n)
        return True


class Tab_1_ReadData(TabContentsContainer):
    def __init__(self, visible:bool):
        super().__init__(workIdx=1, visible=visible)
        self.padding = 10

        #格子定数用
        self.spaceGItNum:str
        self.spaceGName:str
        self.dataName = ft.TextField(expand=1,label="Data_Name",read_only=True)
        self.cellLenA = ft.TextField(expand=1,label="Cell_Length_a",read_only=True)
        self.cellLenB = ft.TextField(expand=1,label="Cell_Length_b",read_only=True)
        self.cellLenC = ft.TextField(expand=1,label="Cell_Length_c",read_only=True)
        self.cellAngleA = ft.TextField(expand=1,label="Cell_Angle_alpha",read_only=True)
        self.cellAngleB = ft.TextField(expand=1,label="Cell_Angle_beta",read_only=True)
        self.cellAngleC = ft.TextField(expand=1,label="Cell_Angle_gamma",read_only=True)
        self.cellVolume = ft.TextField(expand=1,label="Cell_Volume",read_only=True)
        self.cellLengths = ft.Row(
            spacing=0,
            controls=[
                self.cellLenA,
                self.cellLenB,
                self.cellLenC
                ]
            )
        self.cellAngles = ft.Row(
            spacing=0,
            controls=[
                self.cellAngleA,
                self.cellAngleB,
                self.cellAngleC
                ]
            )
        self.cellData = ft.Column(
            expand=1,
            controls=[
                self.dataName,
                self.cellLengths,
                self.cellAngles
            ]
        )
        #原子座標用
        self.selectedRows:List[int] = []
        self.readTable = ft.DataTable(
            border = ft.border.all(1, ft.Colors.BLACK),
            show_checkbox_column=True,
            column_spacing=20,
            columns=[
                ft.DataColumn(ft.Text("Atom")),
                ft.DataColumn(ft.Text("Idx1"),numeric=True),
                ft.DataColumn(ft.Text("Idx2"),numeric=True),
                ft.DataColumn(ft.Text("X"),numeric=True),
                ft.DataColumn(ft.Text("Y"),numeric=True),
                ft.DataColumn(ft.Text("Z"),numeric=True),
                ft.DataColumn(ft.Text("Occ."),numeric=True)
            ]
        )
        self.readTableBase = ft.Column(
            expand=2,
            controls=[
                self.readTable
            ],
            scroll=ft.ScrollMode.ALWAYS
        )




        self.content = ft.Column(
            controls=[
                self.cellData,
                #PlaceHoldeeeer(2)
                self.readTableBase
            ]
        )

    def insert_cells(self):
        #* read_row -> data = インデックス番号
        read_row:ft.DataRow
        i:int = 0
        n:int = 0
        for inList in fileData:
            if i == 0:
                if inList[0] == 'FileData_Output':
                    pass
                else:
                    return
            elif i == 1 and inList[0] == 'fileName':
                self.dataName.value = inList[1]
                #continue
            elif i == 400:
                return
            if i >= 2:
                match inList[0]:
                    case 'space_group_IT_number':
                        self.spaceGItNum = inList[1]
                    case 'space_group_name_H-M_alt':
                        self.spaceGName = inList[1]
                    case 'cell_length_a':
                        self.cellLenA.value = inList[1]
                    case 'cell_length_b':
                        self.cellLenB.value = inList[1]
                    case 'cell_length_c':
                        self.cellLenC.value = inList[1]
                    case 'cell_angle_alpha':
                        self.cellAngleA.value = inList[1]
                    case 'cell_angle_beta':
                        self.cellAngleB.value = inList[1]
                    case 'cell_angle_gamma':
                        self.cellAngleC.value = inList[1]
                    case x if re.match('[A-Z][a-z]{0,1}',x):
                        read_row = ft.DataRow(cells=[],data=n,on_select_changed=self.row_CBox_clicked)
                        for inData in inList:
                            read_row.cells.append(ft.DataCell(ft.Text(inData)))
                        if len(inList) <= 6:
                            read_row.cells.append(ft.DataCell(content=ft.Text("-")))
                        self.readTable.rows.append(read_row)
                        n += 1
                    case _:
                        pass
            i += 1

    def row_CBox_clicked(self,e:ft.ControlEvent):
        if e.control.selected:
            e.control.selected = False
            for idx in self.selectedRows:
                if idx == e.control.data:
                    self.selectedRows.remove(idx)
                else:
                    pass
        else:
            e.control.selected = True
            self.selectedRows.append(e.control.data)
        print(self.selectedRows)
        #print(e.control.data)
        self.update()





class MakeCiApp(ft.Container):
    def __init__(self):
        super().__init__()
        #self.width = 800

        #? パーツのインスタンス生成(宣言)
        self.naviBar = NaviBar()
        self.naviBarC = ft.Container(
            border = ft.border.all(1,ft.Colors.BLACK),
            padding = 10,
            expand = 1,
            bgcolor = ft.Colors.GREY_300,
            content = self.naviBar
        )
        #self.tabContentsContainer = TabContentsContainer(0)

        self.testholder = PlaceHoldeeeer()

        self.tab0 = Tab_0_FilePathSelect(visible=True)
        self.tab1 = Tab_1_ReadData(visible=False)
        self.tabContents = ft.Stack(
            expand=10,
            controls=[
                PlaceHoldeeeer(color=ft.Colors.with_opacity(0.2,ft.Colors.random())),
                self.tab0,
                self.tab1
                #self.testholder
            ]
        )
        
        self.bottomBtn0 = TabBottomButton(buttonClicked=self.bottom_btn_clicked,workIdx=0)
        self.bottomBtn1 = TabBottomButton(buttonClicked=self.bottom_btn_clicked,workIdx=1)
        self.bottomBtn2 = TabBottomButton(buttonClicked=self.bottom_btn_clicked,workIdx=2)
        self.bottomBtn3 = TabBottomButton(buttonClicked=self.bottom_btn_clicked,workIdx=3)
        self.bottomButtons = ft.Row(
            expand=1,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.bottomBtn3,
                self.bottomBtn2,
                self.bottomBtn0,
                self.bottomBtn1
            ]
        )
        self.tabBase = ft.Column(
            height=540,
            expand=3,
            spacing=2,
            controls=[
                self.tabContents,
                self.bottomButtons
            ]
        )




        #? パーツの個別設定
        self.naviBar.controls = [
            NaviButton(0, self.navigate_btn_clicked),
            NaviDownMark(),
            NaviButton(1, self.navigate_btn_clicked),
            NaviDownMark(),
            NaviButton(2, self.navigate_btn_clicked),
            NaviDownMark(),
            NaviButton(3, self.navigate_btn_clicked),
        ]

        #? パーツを配置
        self.content = ft.Row(
            controls=[
                self.naviBarC,
                self.tabBase
            ]
        )


    def navigate_btn_clicked(self,e):
        self.tab_change(e.control.workIdx)
        #self.update()

    def tab_change(self, toIdx:int):
        # ↓親コンテナ(tabContents)のｺﾝﾄﾛｰﾙﾘｽﾄ(ft.stackで配置)的には，
        # ↓場所固定用のプレースホルダが一番背後(idx=0)に常駐してるのでタブコンテナ内蔵のidx値と1ズレる
        #self.tabContents.controls[toIdx+1].visible
        #? ↑廃止matchを使おうとしてできなかった時の残骸か。
        for tab in self.tabContents.controls:
            if tab.data == toIdx:
                tab.visible = True
            elif tab.data == 99:
                pass
            else:
                tab.visible = False
        btn:TabBottomButton
        for btn in self.bottomButtons.controls:
            btn.change_init(toIdx)

        self.update()

    def bottom_btn_clicked(self,e):
        pageIdx:int = e.control.pageIdx
        workIdx:int = e.control.workIdx

        if workIdx == 0:
            self.page.window.close()

        match pageIdx:
            case 0:
                if workIdx == 1:
                    if self.tab0.read_output_file():
                        self.tab_change(1)
                        self.tab1.insert_cells()
            case 1:
                if workIdx == 1:
                    print("page1")
                elif workIdx == 3:
                    if len(self.tab1.readTable.rows) == 0 or self.tab1.readTable.rows == None:
                        pass
                    else:
                        for delIdx in self.tab1.selectedRows:
                            for roooow in self.tab1.readTable.rows:
                                if roooow.data == delIdx:
                                    #! 一回分の戻る操作を可能にしたい
                                    self.tab1.readTable.rows.remove(roooow)
                        self.tab1.selectedRows.clear()
            case x:
                pass
        self.update()

    #! ↓テスト用ボタンの機能。削除予定
    def button_clicked(self, e):
        workIdx:int = e.control.workIdx
        print(f"{workIdx}_Button clicked")
        print(self.testholder.visible)
        if self.testholder.visible:
            #self.tabContentsContainer.testholder.visible
            self.testholder.visible = False
        else:
            self.testholder.visible = True
        

        self.update()

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
        #!ここに終了時のsave動作などを追加
        self.page.window.destroy()




def main(page: ft.Page):
    page.title = "Make Ci App"
    page.window.width = 800
    page.window.height = 605
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    #? ファイルピッカーの追加はここで。(グローバル変数を関数内で編集するには一度宣言が必要っぽい)
    global file_pickers
    file_pickers = {
            "builder_pick": ft.FilePicker(),
            "cif_pick": ft.FilePicker(),
            "outpuuuut_pick": ft.FilePicker()
        }
        # ↓ここですべてのﾌｧｲﾙﾋﾟｯｶｰのPageへのOverlayをしてる。
        #  新規にﾌｧｲﾙﾋﾟｯｶｰを追加してもここに手を加える必要はない
    for i in file_pickers.keys():
        page.overlay.append(file_pickers.get(i))
        page.update()

    #? 設定ファイルの読み込み
    global settingData
    settingFilePath = os.getcwd()+os.sep+"makeci_setting.txt"
    if os.path.isfile(settingFilePath):
        print("True")
        with open(settingFilePath) as f:
            for line in f:
                lineParts = line.rstrip().split(sep=';')
                if len(lineParts) <= 1:
                    continue
                elif len(lineParts) >= 3:
                    lineParts[1] = ';'.join(lineParts[1:])
                settingData[lineParts[0]] = lineParts[1]
        print(settingData)
    else:
        print("False")

    makeCi = MakeCiApp()

    def window_event(e):
        if e.data == "close":
            page.open(ExitConfirmDialog())
            page.update()
    page.window.prevent_close = True
    page.window.on_event = window_event

    page.add(makeCi)
    page.window.center()
    page.update()

ft.app(target=main)