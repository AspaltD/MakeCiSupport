import pyautogui as pag
import time

def test_pag():
    pag.press("win")
    pag.PAUSE = 1.0
    pag.write("memo")
    pag.PAUSE = 1.0
    pag.press("enter")

    pag.PAUSE = 1.0
    pag.write("test")

def test_click():
    pass