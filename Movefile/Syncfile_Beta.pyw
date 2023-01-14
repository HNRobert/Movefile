# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 12:28:30 20233

@author: Robert He
"""

import os
import time
import shutil


def scan_folders_in_path(folder_path):
    all_items = os.listdir(folder_path)
    item_store = [folder_path]
    for item in all_items:
        item_path = folder_path + '\\' + item
        if os.path.isdir(item_path):
            item_store.extend(scan_folders_in_path(item_path))
    item_store = sorted(set(item_store))
    return item_store


def judge_update_time(item_path_1, item_path_2):
    now = int(time.time())
    last_edit_time_1 = int(os.stat(item_path_1).st_mtime)
    last_edit_time_2 = int(os.stat(item_path_2).st_mtime)
    print(last_edit_time_1, last_edit_time_2)
    if last_edit_time_1 > last_edit_time_2:
        return '>'
    elif last_edit_time_1 < last_edit_time_2:
        return '<'
    else:
        return '='


def match_item(item__path, in_folder__path):
    item_name = item__path.split('\\')[-1]
    matched = False
    for m_item_name in os.listdir(in_folder__path):
        if m_item_name == item_name:
            md_item__path = in_folder__path + '\\' + m_item_name
            return md_item__path
    else:
        return ''


def record_match(path_1, path_2):
    for folder1_path in scan_folders_in_path(path_1):
        folder_matched = match_item(folder1_path, path_2)
            if folder_matched:

                matched = True
                item_inside1 = os.listdir(folder1_path)
                item_inside2 = os.listdir(folder2)
                print(item_inside2)
    if judge_update_time(file_path_1, file_path_2) == '>':
        pass


print(scan_folders_in_path(r'C:\Users\25674\Desktop\新建文件夹'))
# print(judge_update_time(r"C:\Users\25674\Desktop\Desktop Files' Home", "C:\Users\25674\Desktop\Desktop Files' Home"))
syncfile(r"C:\Users\25674\Desktop\新建文件夹", r"C:\Users\25674\Desktop\新建文件夹 - 副本")
