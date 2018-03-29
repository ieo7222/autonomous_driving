# https://stackoverflow.com/questions/3586046/fastest-way-to-take-a-screenshot-with-python-on-windows
# https://stackoverflow.com/questions/12590942/is-there-any-better-way-to-capture-the-screen-than-pil-imagegrab-grab

import cv2
import numpy as np

# pywin32
import win32com.client  # to solve bug about setforegroundwindow
import win32con 
import win32gui
import win32ui

def get_screen(resize_width, resize_height):
    """return resized image of current game screen
    find specific window that has name of 'Euro Truck Simulator 2'
    after that, get current screen
    and resize the screen
    Args:
        resize_width
        resize_height
    Returns:
        img_resized
    """
    try:
        hwnd = win32gui.FindWindow(None, 'Euro Truck Simulator 2')
        bbox = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = bbox
        width = abs(left-right)
        height = abs(top-bottom)
        winDC = win32gui.GetWindowDC(hwnd)
        srcDC = win32ui.CreateDCFromHandle(winDC)
        memDC = srcDC.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcDC, width, height)
        memDC.SelectObject(bmp)
        memDC.BitBlt((0, 0), (width, height), srcDC, (0, 0), win32con.SRCCOPY)
        signedIntsArray = bmp.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (height, width, 4)
        srcDC.DeleteDC()
        memDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, winDC)
        win32gui.DeleteObject(bmp.GetHandle())

        img_resized = cv2.resize(img, (resize_width, resize_height), interpolation=cv2.INTER_AREA)
    except:
        print('Cannot get screen')
    return cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)

def move_screen():
    """move output windows for convenience
    get handler of each windows
    and move windows right side
    based on the first place of game screen
    each location can be replaced

    excute once for initialization

    'shell' part for SetForegroundWindow
    """
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')

    hwnd1 = win32gui.FindWindow(None, 'Euro Truck Simulator 2')
    hwnd2 = win32gui.FindWindow(None, 'OUTPUT')
    hwnd3 = win32gui.FindWindow(None, 'processed')
    hwnd4 = win32gui.FindWindow(None, 'mask')
    left, top, right, bottom = win32gui.GetWindowRect(hwnd1)
    cv2.moveWindow('OUTPUT', right, top)
    cv2.moveWindow('processed', right, top+300)
    cv2.moveWindow('mask', right, top+600)
    win32gui.SetForegroundWindow(hwnd4)
    win32gui.SetForegroundWindow(hwnd3)
    win32gui.SetForegroundWindow(hwnd2)
    win32gui.SetForegroundWindow(hwnd1)
