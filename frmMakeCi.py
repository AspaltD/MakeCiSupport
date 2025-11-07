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
        self.b_text: str
        match idx:
            case 0:
                self.b_text = "動作設定"
            case 1:
                self.b_text = "読取結果"
            case 2:
                self.b_text = "Builderログ"
            case 3:
                self.b_text = "Builder動作完了"
            case _:
                self.b_text = "Null Button"
        return self.b_text

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
    
class TabContents(ft.Container):
    def __init__(self, workIdx):
        super().__init__()
        self.workIdx = workIdx
        self.expand = 3
        self.height = 540
        self.bgcolor = ft.Colors.LIGHT_BLUE_100
        #self.border = ft.border.all(1,ft.Colors.BLACK)
        self.content = ft.Column(
            controls=[
                ft.Text(value="TabContents_0")
            ]
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
                self.tabContents
            ]
        )


    def button_clicked(self, e):
        workIdx: int = e.control.workIdx
        print(f"{workIdx}_Button clicked")

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