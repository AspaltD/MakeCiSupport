import flet as ft
import logging

import enEnums as en
import frmInterfaces as itf


class AppMainFrame(itf.AppMainFrame):
    def __init__(self):
        super().__init__()


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