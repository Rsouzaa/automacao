# -*- coding: utf-8 -*-
"""
Module with utilities functions for host emulator testing.
"""
import logging
import os
from datetime import datetime
from time import sleep
from settings import settings

logger = logging.getLogger(__name__)

try:
    import win32con
    import win32gui  # noqa
    import win32ui
except (ModuleNotFoundError,) as ex:
    logger.warning(ex)


def format_date(date):
    """
    Return a date formatted.
    :param date:
    :return:
    """
    return str(date).replace('-', '').replace(' ', '_').replace(':', '').replace('.', '')


def screenshot(capture_name, hwnd=None):
    """
    Take a screenshot for host emulator.
    :param capture_name:
    :param hwnd:
    :return:
    """
    if not hwnd:
        hwnd = win32gui.GetDesktopWindow()
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    h = b - t
    w = r - l
    h_dc = win32gui.GetWindowDC(hwnd)
    my_dc = win32ui.CreateDCFromHandle(h_dc)
    new_dc = my_dc.CreateCompatibleDC()

    my_bitmap = win32ui.CreateBitmap()
    my_bitmap.CreateCompatibleBitmap(my_dc, w, h)

    new_dc.SelectObject(my_bitmap)

    win32gui.SetForegroundWindow(hwnd)
    sleep(.2)
    new_dc.BitBlt((0, 0), (w, h), my_dc, (0, 0), win32con.SRCCOPY)
    my_bitmap.Paint(new_dc)
    screenshot_name = f"{capture_name}_{format_date(datetime.now())}.png"
    output_path = os.path.join(settings.BASE_PATH, 'output' + os.sep + 'screenshots')
    screenshot_path = os.path.join(output_path, screenshot_name)
    my_bitmap.SaveBitmapFile(new_dc, screenshot_path)
    return screenshot_path


def get_windows_by_title(windows_title):
    """
    Return host window by title.
    :param windows_title:
    :return:
    """

    def _window_callback(hwnd, all_windows):
        all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

    windows = []
    win32gui.EnumWindows(_window_callback, windows)

    aux = [hwnd for hwnd, title in windows if windows_title in title]
    logger.debug(f'Windows get by title {windows_title}: {aux}')
    return aux[0]


def get_host_screenshot(windows_title, capture_name=''):
    """
    Take a hot emulator screenshot by windows title.
    :param windows_title:
    :param capture_name:
    :return:
    """
    windows = get_windows_by_title(windows_title)
    return screenshot(capture_name, windows)
