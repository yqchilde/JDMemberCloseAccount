
import win32api, win32con, win32gui
from PIL import Image, ImageGrab
hwnd_title = dict()

def get_window_pos(name):
    name = name
    handle = win32gui.FindWindow(0, name)
    # 获取窗口句柄
    if handle == 0:
        return None
    else:
        # 返回坐标值和handle
        return win32gui.GetWindowRect(handle), handle


def fetch_image():
    (x1, y1, x2, y2), handle = get_window_pos('123321')
    # 发送还原最小化窗口的信息
    win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
    # 设为高亮
    win32gui.SetForegroundWindow(handle)
    # 截图
    grab_image = ImageGrab.grab((x1+417, y1+253, x2-68, y2-746))
    grab_image.save('ios_code_pic.png')
    return grab_image

def get_all_hwnd(hwnd, mouse):
    hWndList = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList)
    # print(hWndList)
    for hwnd in hWndList:
        title = win32gui.GetWindowText(hwnd)
        print(title)


if __name__ == '__main__':
    fetch_image()

