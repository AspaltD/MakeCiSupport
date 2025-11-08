import flet as ft

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

class TabBottomButton(ft.Button):
    def __init__(self, pageIdx:int, workIdx:int=0, buttonClicked):
        super().__init__()
        self.pageIdx = pageIdx
        self.workIdx = workIdx
        self.on_click = buttonClicked
        self.text = self.select_text()
        self.width = 40

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

class TabContents(ft.Container):
    def __init__(self, workIdx):
        super().__init__()
        self.workIdx = workIdx
        self.expand = True
        #self.height = 540
        self.bgcolor = ft.Colors.LIGHT_BLUE_100
        #self.border = ft.border.all(1,ft.Colors.BLACK)

        self.bottomButtons = ft.Row(
            expand=1,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                #TabBottomButton(pageIdx=0)
            ]
        )

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Text(value="TabContents_0")
            ],
            #expand_loose=False

        )


class MakeCiApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.width = 800

        #? パーツのインスタンス生成(宣言)
        self.naviBar = NaviBar()
        self.naviBarC = ft.Container(
            border = ft.border.all(1,ft.Colors.BLACK),
            padding = 10,
            expand = 1,
            bgcolor = ft.Colors.GREY_300,
            content = self.naviBar
        )
        self.tabContents = TabContents(0)
        self.tabContentsBase = ft.Container(
            expand = 3,
            bgcolor = ft.Colors.DEEP_ORANGE_100,
            content = ft.Stack(
                expand=True,
                controls=[
                    self.tabContents
                ]
            )
            
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
                self.tabContentsBase
            ]
        )


    def button_clicked(self, e):
        workIdx: int = e.control.workIdx
        print(f"{workIdx}_Button clicked")
        print(self.tabContents.visible)
        if self.tabContents.visible:
            self.tabContents.visible = False
        else:
            self.tabContents.visible = True
        

        self.update()






def main(page: ft.Page):
    page.title = "Make Ci App"
    page.window.width = 800
    page.window.height = 605
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()


    makeCi = MakeCiApp()

    page.add(makeCi)

ft.app(target=main)