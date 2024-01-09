# -*- coding: utf-8 -*-
"""
If you have any suggestion for optimizing this program,
it's welcomed to submit that to the author.

Created on Wed Dec 21 17:07:30 2022

@author: Robert He
QQ: 2567466856
GitHub address: https://github.com/HNRobert/Movefile
"""


import logging
import time
import tkinter.messagebox

from mf_mods import Initialization
from mf_ui import make_ui
from mttkinter import mtTkinter as tk
from win32gui import FindWindow, ShowWindow


class GlobalsVar:
    def __init__(self):
        self.gvar = {
            "program_finished": False,
            "new_areas_data": []
        }

    def get(self, key):
        return self.gvar[key]

    def set(self, key, value):
        self.gvar[key] = value
        return True


gvar = GlobalsVar()



# The CheckMFProgress class is used to check if the program is already running.
# If it's running, it will display a message box to inform the user, and put the window on the top.
class CheckMFProgress:

    def __init__(self):
        self.continue_this_progress = True
        if self.proc_root_on():
            self.continue_this_progress = False

    def proc_root_on(self):
        mfs_hwnd = FindWindow(None, 'Movefile Setting')
        if mfs_hwnd:
            return self.display_root(mfs_hwnd)
        return False

    def display_root(self, mf_hwnd):
        temp_root = tk.Tk()
        temp_root.withdraw()
        try:
            ShowWindow(mf_hwnd, 5)
            tkinter.messagebox.showinfo(
                title="Movefile", message="The app's running!")
            temp_root.quit()
            temp_root.destroy()
            return True
        except:
            temp_root.quit()
            temp_root.destroy()
            return False


def main():
    checkpgs_result = CheckMFProgress()
    if not checkpgs_result.continue_this_progress:
        return
    initial_data = Initialization()
    time.sleep(0.1)
    visits_today = initial_data.ask_time_today
    boot_visit = initial_data.startup_visit
    first_visit = initial_data.first_visit
    logging.info(
        f"\nMovefile Start\nVisits today: {visits_today}\nStartup visit: {str(boot_visit)}")

    make_ui(first_visit=first_visit, startup_visit=boot_visit,
            visits_today=visits_today)


if __name__ == '__main__':
    main()
