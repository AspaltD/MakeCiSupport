import flet as ft
import logging

import enEnums as en
import frmInterfaces as itf





class AppMainFrame(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
        )
        self.leftTabChBar = itf.Left_box_TabChangeBar()
        self.tab99 = itf.Rgt_tab_99_PlaceHolder()
        self.tab0 = itf.Rgt_tab_0_CIFSelect()
        self.tab1 = itf.Rgt_tab_1_CIFPreview()
        self.tab2 = itf.Rgt_tab_2_AppLogs()
        self.tab3 = itf.Rgt_tab_3_BuilderResult()
        self.tab4 = itf.Rgt_tab_4_MISelect()
        self.tab5 = itf.Rgt_tab_5_GJFPreview()
        self.rgtTabs = ft.Stack(
            expand=3,
            controls=[
                self.tab99,
                self.tab2,
                self.tab0,
                self.tab1,
                self.tab3,
                self.tab4,
                self.tab5,
            ]
        )
        self.content = ft.Row(
            expand=True,
            controls=[
                self.leftTabChBar,
                self.rgtTabs,
            ]
        )

    def set_init(self):
        self.leftTabChBar.set_tabBtn_on_click(self._left_tabBtn_event)

    def tab_change(self, to_tab_idx:en.TabIdx):
        for _tab in self.rgtTabs.controls:
            if not isinstance(_tab, itf.Rgt_col_TabBase): continue
            if _tab.tabIdx == to_tab_idx: _tab.visible = True
            elif _tab.tabIdx == 99: pass
            elif _tab.tabIdx == 2: pass
            else: _tab.visible = False
        self.update()
    def _left_tabBtn_event(self, e:ft.ControlEvent):
        if not isinstance(e.control, itf.Left_btn_TabChange): return
        self.tab_change(e.control.tabIdx)
        self.update()


class App_ExitConfirmDlg(itf.App_ExitConfirmDlg):
    def __init__(self):
        super().__init__()

    def yes_clicked(self, e):
        self.page.close(self)
        #!ここに終了時動作
        self.page.window.destroy()

def main(page: ft.Page):
    page.title = "Make CI Support App"
    page.window.width = 800
    page.window.height = 605
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def window_close_event(e):
        if e.data == 'close':
            page.open(App_ExitConfirmDlg())
            page.update()
    page.window.prevent_close = True
    page.window.on_event = window_close_event

    appMainFrame = AppMainFrame()
    page.add(appMainFrame)
    page.window.center()
    page.update()

    appMainFrame.set_init()
    page.update()

if __name__ == '__main__':
    ft.app(target=main)