# -*- coding: utf-8 -*-
"""
If you have any suggestion for optimizing this program,
it's welcomed to submit that to the author.

Created on Wed Dec 21 17:07:30 2022

@author: Robert He
QQ: 2567466856
GitHub address: https://github.com/HNRobert/Movefile
"""


import time


class GlobalsVar:
    def __init__(self):
        self.gvar = {
            "program_finished": False
        }

    def get(self, key):
        return self.gvar[key]

    def set(self, key, value):
        self.gvar[key] = value
        return True


gvar = GlobalsVar()


def main():
    from mf_mods import CheckMFProgress, Initialization, mf_log
    from mf_ui import make_ui
    checkpgs_result = CheckMFProgress()
    if not checkpgs_result.continue_this_progress:
        return
    initial_data = Initialization()
    time.sleep(0.1)
    visits_today = initial_data.ask_time_today
    boot_visit = initial_data.startup_visit
    first_visit = initial_data.first_visit
    quit_after_autorun = initial_data.quit_after_autorun
    mf_log(
        f"\nMovefile Start\nVisits today: {visits_today}\nStartup visit: {str(boot_visit)}")

    make_ui(first_visit=first_visit, startup_visit=boot_visit,
            visits_today=visits_today, quit_after_autorun=quit_after_autorun)


if __name__ == '__main__':
    main()
