import flet as ft
import os
from typing import Optional

class PlaceHoldeeeer(ft.Placeholder):
    def __init__(self, expand:int=404, color=ft.Colors.random()):
        super().__init__()
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
    def __init__(self,buttonClicked, pageIdx:int, workIdx:int=0):
        super().__init__()
        self.pageIdx = pageIdx
        self.workIdx = workIdx
        self.on_click = buttonClicked
        self.text = self.select_text()
        self.width = 120

    #? workIdx = 0:Exit, 1:Next

    def select_text(self):
        re_text:str
        if self.workIdx == 0:
            re_text = "ExitApp"
        elif self.workIdx == 1:
            re_text = "Next"
        else:
            re_text = "--Null--"
        match self.pageIdx:
            case 0:
                if self.workIdx == 1:
                    re_text = "Read"
            case 1:
                if self.workIdx == 1:
                    re_text = "Save&Ins"
            case 2:
                if self.workIdx == 1:
                    re_text = "Stop"
            case 3:
                if self.workIdx == 1:
                    #! MakeMiを実装したら "MakeMi" に変更
                    re_text = "Next"
            case 4:
                if self.workIdx == 1:
                    re_text = "Stop"
            case 5:
                if self.workIdx == 1:
                    re_text = "Stop"
            case _:
                pass
        return re_text

class TabContentsContainer(ft.Container):
    def __init__(self, workIdx:int, filePicker:Optional[ft.FilePicker]=None):
        super().__init__()
        self.workIdx = workIdx
        self.filePicker = filePicker
        self.expand = 10
        self.padding = 10
        #self.height = 540
        self.bgcolor = ft.Colors.LIGHT_BLUE_100
        #self.border = ft.border.all(1,ft.Colors.BLACK)

class FilePickerBar(ft.Row):
    def __init__(self, filePicker:ft.FilePicker, hintText:str):
        super().__init__()

        self.fileName:str
        self.filePath:str
        self.filePickeeeer = filePicker
        self.filePickeeeer.on_result = self.pick_files_result
        self.textF_path = ft.TextField(expand=9,hint_text=hintText,dense=True)

        self.spacing = 0

        self.controls.append(self.filePickeeeer)
        self.controls = [
            self.textF_path,
            ft.FilledButton(expand=1,text="File", on_click=lambda _: self.filePickeeeer.pick_files(allowed_extensions=["txt"]))
        ]

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.fileName = e.files[0].name
            self.filePath = e.files[0].path.replace(os.sep, '/')
            print(f"Selected files:name={e.files[0].name}")
            print(f"Selected files:{self.filePath}")
            self.textF_path.value = self.filePath
        self.update()



class Tab_0_FilePathSelect(TabContentsContainer):
    def __init__(self, filePicker:ft.FilePicker):
        super().__init__(0,filePicker)

        self.content = ft.Column([
            ft.Text("Builder Path"),
            FilePickerBar(self.filePicker,"Builder Path"),
            ft.Text("'.cif' File Path"),
            FilePickerBar(self.filePicker,"'.cif' File Path"),
            ft.Text("Output Path"),
            FilePickerBar(self.filePicker,"Output Path")
        ])





class MakeCiApp(ft.Container):
    def __init__(self, filePicker:ft.FilePicker):
        super().__init__()
        #self.width = 800
        self.filePicker = filePicker

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
        self.tabContents = ft.Stack(
            expand=10,
            controls=[
                PlaceHoldeeeer(color=ft.Colors.with_opacity(0.2,ft.Colors.random())),
                Tab_0_FilePathSelect(self.filePicker),
                self.testholder
            ]
        )
        self.bottomButtons = ft.Row(
            expand=1,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                TabBottomButton(buttonClicked=self.button_clicked,pageIdx=0,workIdx=1)
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
            NaviButton(0, self.button_clicked),
            NaviDownMark(),
            NaviButton(1, self.button_clicked),
            NaviDownMark(),
            NaviButton(2, self.button_clicked),
            NaviDownMark(),
            NaviButton(3, self.button_clicked),
        ]

        #? パーツを配置
        
        self.content = ft.Row(
            controls=[
                self.naviBarC,
                self.tabBase
                #PlaceHoldeeeer(expand=3)
            ]
        )


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






def main(page: ft.Page):
    page.title = "Make Ci App"
    page.window.width = 800
    page.window.height = 605
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    filePickeeeer = ft.FilePicker()

    page.overlay.append(filePickeeeer)
    page.update()

    makeCi = MakeCiApp(filePicker=filePickeeeer)

    page.add(makeCi)
    page.update()

ft.app(target=main)