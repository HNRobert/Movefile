from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ['ToastNotifier']

# #############################################################################
# ########## Libraries #############
# ##################################
# standard library
import logging
import threading
import queue
from os import path
from time import sleep
from pkg_resources import Requirement
from pkg_resources import resource_filename
from queue import Queue

# 3rd party modules
from win32api import GetModuleHandle
from win32api import PostQuitMessage
from win32con import CW_USEDEFAULT
from win32con import IDI_APPLICATION
from win32con import IMAGE_ICON
from win32con import LR_DEFAULTSIZE
from win32con import LR_LOADFROMFILE
from win32con import WM_DESTROY
from win32con import WM_USER
from win32con import WS_OVERLAPPED
from win32con import WS_SYSMENU
from win32gui import CreateWindow
from win32gui import DestroyWindow
from win32gui import LoadIcon
from win32gui import LoadImage
from win32gui import NIF_ICON
from win32gui import NIF_INFO
from win32gui import NIF_MESSAGE
from win32gui import NIF_TIP
from win32gui import NIM_ADD
from win32gui import NIM_DELETE
from win32gui import NIM_MODIFY
from win32gui import RegisterClass
from win32gui import UnregisterClass
from win32gui import Shell_NotifyIcon
from win32gui import UpdateWindow
from win32gui import WNDCLASS


# ############################################################################
# ########### Classes ##############
# ##################################


class ToastNotifier(object):
    """Create a Windows 10  toast notification.

    from: https://github.com/jithurjacob/Windows-10-Toast-Notifications
    """

    def __init__(self):
        """Initialize."""
        self._thread = None
        self._lock = threading.Lock()  # Create a lock object
        self._notification_queue = Queue()

        self._stop_notification_thread = threading.Event()  # Event to signal thread to stop
        self._notification_thread = threading.Thread(target=self._process_notifications)
        self._notification_thread.start()

    def _process_notifications(self):
        while not self._stop_notification_thread.is_set() or self._notification_queue.qsize() > 0:
            try:
                title, msg, icon_path, duration = self._notification_queue.get(timeout=1)
                self._show_toast(title, msg, icon_path, duration)
                self._notification_queue.task_done()
            except queue.Empty:
                sleep(0.2)

    def stop_notification_thread(self):
        self._stop_notification_thread.set()
        self._notification_thread.join()  # Wait for the thread to finish

    def _show_toast(self, title, msg,
                    icon_path, duration):
        """Notification settings.

        :title: notification title
        :msg: notification message
        :icon_path: path to the .ico file to custom notification
        :duration: delay in seconds before notification self-destruction
        """
        message_map = {WM_DESTROY: self.on_destroy, }

        # Register the window class.
        self.wc = WNDCLASS()
        self.hinst = self.wc.hInstance = GetModuleHandle(None)
        self.wc.lpszClassName = str("PythonTaskbar")  # must be a string
        self.wc.lpfnWndProc = message_map  # could also specify a wndproc.
        try:
            self.classAtom = RegisterClass(self.wc)
        except Exception:
            pass  # not sure of this
        style = WS_OVERLAPPED | WS_SYSMENU
        self.hwnd = CreateWindow(self.classAtom, "Taskbar", style,
                                 0, 0, CW_USEDEFAULT,
                                 CW_USEDEFAULT,
                                 0, 0, self.hinst, None)
        UpdateWindow(self.hwnd)

        # icon
        if icon_path is not None:
            icon_path = path.realpath(icon_path)
        else:
            icon_path = resource_filename(Requirement.parse("win10toast"), "win10toast/data/python.ico")
        icon_flags = LR_LOADFROMFILE | LR_DEFAULTSIZE
        try:
            hicon = LoadImage(self.hinst, icon_path,
                              IMAGE_ICON, 0, 0, icon_flags)
        except Exception as e:
            logging.error("Some trouble with the icon ({}): {}"
                          .format(icon_path, e))
            hicon = LoadIcon(0, IDI_APPLICATION)

        # Taskbar icon
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, WM_USER + 20, hicon, "Notification")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, (self.hwnd, 0, NIF_INFO,
                                      WM_USER + 20,
                                      hicon, "Balloon Tooltip", msg, 200,
                                      title))
        # take a rest then destroy
        sleep(duration)
        with self._lock:
            DestroyWindow(self.hwnd)
            sleep(0.1)  # Wait for a short time to ensure the window is destroyed
            UnregisterClass(self.wc.lpszClassName, None)
        return 0

    def show_toast(self, title="Notification", msg="Here comes the message",
                   icon_path=None, duration=5):
        """Notification settings.

        :title: notification title
        :msg: notification message
        :icon_path: path to the .ico file to custom notification
        :duration: delay in seconds before notification self-destruction
        """
        self._notification_queue.put((title, msg, icon_path, duration))

    def notification_active(self):
        """See if we have an active notification showing"""
        if self._thread is not None and self._thread.is_alive():
            # We have an active notification, let it finish, we don't spam them
            return True
        return False

    def on_destroy(self, hwnd, msg, wparam, lparam):
        """Clean after notification ended.

        :hwnd:
        :msg:
        :wparam:
        :lparam:
        """
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)

        return 0
