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
    item_store = [folder_path]
    for item in all_items:
        item_path = folder_path + '\\' + item
        if os.path.isdir(item_path):
            item_store.extend(scan_folder(item_path))
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


def match_items(item__path, folder__path):
    item_name = item__path.split('\\')[-1]
    matched = False
    for m_item_name in os.listdir(folder__path):
        if m_item_name == item_name:
            md_item__path = folder__path + '\\' + m_item_name
            return md_item__path
    else:
        return ''


def syncfile(file_path_1, file_path_2):
    for folder1 in scan_folder(file_path_1):
        match = False
        folder1_name = folder1.split('\\')[-1]
        for folder2 in scan_folder(file_path_2):
            folder2_name = folder2.split('\\')[-1]
            if folder1_name == folder2_name:
                matched = True
                item_inside1 = os.listdir(folder1)
                item_inside2 = os.listdir(folder2)
                print(item_inside2)
    if judge_update_time(file_path_1, file_path_2) == '>':
        pass


print(scan_folder(r'C:\Users\25674\Desktop\新建文件夹'))
# print(judge_update_time(r"C:\Users\25674\Desktop\Desktop Files' Home", "C:\Users\25674\Desktop\Desktop Files' Home"))
syncfile(r"C:\Users\25674\Desktop\新建文件夹", r"C:\Users\25674\Desktop\新建文件夹 - 副本")
