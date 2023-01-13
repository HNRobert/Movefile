# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 12:28:30 20233

@author: Robert He
"""

import os
import time
import shutil


def scan_folder(folder_path):
    all_items = os.listdir(folder_path)
    item_store = []
    for item in all_items:
        item_path = folder_path + '\\' + item

        item_store.append(item_path)
        if os.path.isdir(item_path):
            item_store.extend(scan_folder(item_path))
    return item_store


def judge_update_time(file_path_1, file_path_2):
    now = int(time.time())
    last_edit_time_1 = int(os.stat(file_path_1).st_mtime)
    last_edit_time_2 = int(os.stat(file_path_2).st_mtime)
    print(last_edit_time_1, last_edit_time_2)
    if last_edit_time_1 > last_edit_time_2:
        return '>'
    elif last_edit_time_1 < last_edit_time_2:
        return '<'
    else:
        return '='


print(scan_folder('C:\\Users\\25674\\Desktop'))
print(judge_update_time("C:\\Users\\25674\\Desktop\\Desktop Files' Home", "C:\\Users\\25674\\Desktop\\Desktop Files' Home"))

