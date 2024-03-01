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


def main():
    from mf_mods import Initialization, is_proc_running
    from mf_ui import make_ui
    check_result = is_proc_running()
    if check_result:
        return
    init_data = Initialization()
    time.sleep(0.1)

    make_ui(first_visit=init_data.first_visit, startup_visit=init_data.startup_visit,
            visits_today=init_data.ask_time_today, quit_after_autorun=init_data.quit_after_autorun)


if __name__ == '__main__':
    main()
