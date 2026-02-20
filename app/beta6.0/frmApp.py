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
        self.rgtTabs = ft.Stack(
            expand=3,
            controls=[
                self.tab99,
                self.tab0,
                self.tab1,
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

def main(page: ft.Page):
    page.title = "Make CI Support App"
    page.window.width = 800
    page.window.height = 605
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    appMainFrame = AppMainFrame()
    page.add(appMainFrame)
    page.window.center()
    page.update()

    appMainFrame.set_init()
    page.update()

if __name__ == '__main__':
    ft.app(target=main)