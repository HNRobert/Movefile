# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 12:28:30 20233

@author: Robert He
"""

import os
import shutil
import winreg
import configparser


def get_sf_data():
    global sf_data_path
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
    mf_data_path = roaming_path + '\\Movefile'
    sf_data_path = mf_data_path + '\\Syncfile\\'
    if 'Movefile' not in os.listdir(roaming_path) or 'Movefile' in os.listdir(
            roaming_path) and 'Syncfile' not in os.listdir(mf_data_path):
        first_ask = True
        os.mkdir(sf_data_path)
    else:
        first_ask = False
    return first_ask


def scan_files_in(folder_path):  # 扫描路径下所有文件夹
    def scan_folders_in(f_path):
        surf_items = os.listdir(f_path)
        folder_store = [f_path]
        for item in surf_items:
            item_path = f_path + '\\' + item
            if os.path.isdir(item_path):
                folder_store.extend(scan_folders_in(item_path))
        folder_store = sorted(set(folder_store))
        return folder_store
    file_store = []
    for folder in scan_folders_in(folder_path):
        files = [folder + '\\' + dI for dI in os.listdir(folder) if os.path.isfile(os.path.join(folder, dI))]
        file_store.extend(files)
    for i in range(len(file_store)):
        file_store[i] = file_store[i][len(folder_path)::]
    return file_store


def judge_file(item_path_1, item_path_2):  # 更新时间比较函数
    creat_time_1 = int(os.stat(item_path_1).st_ctime)
    creat_time_2 = int(os.stat(item_path_2).st_ctime)
    last_edit_time_1 = int(os.stat(item_path_1).st_mtime)
    last_edit_time_2 = int(os.stat(item_path_2).st_mtime)
    data = []
    if creat_time_1 == creat_time_2:
        data[0] = 's'
    else:
        data[0] = 'd'
    if last_edit_time_1 > last_edit_time_2:
        data[1] = '>'
    elif last_edit_time_1 < last_edit_time_2:
        data[1] = '<'
    else:
        data[1] = '='


def match_item(item1__path, in_folder2_path):  # 配对文件函数
    item1_name = item1__path.split('\\')[-1]
    for item2_name in os.listdir(in_folder2_path):
        if item2_name == item1_name:
            return [item1_name, item2_name]
    else:
        return [item1_name, '']


def record_match(path_1, path_2):  # 记录配对组
    cf = configparser.ConfigParser()
    folders_on_surface_path = [path_1 + '\\' + dI for dI in os.listdir(path_1) if
                               os.path.isdir(os.path.join(path_1, dI))]

    if not os.path.exists(sf_data_path + r'Syncfile_data.ini'):
        file = open(sf_data_path + r'Syncfile_data.ini', 'w+', encoding='ANSI')
        file.close()
    cf.read(sf_data_path + r'Syncfile_data.ini', encoding='ANSI')
    section_name = "Match_pairs"
    if not cf.has_section(section_name):
        cf.add_section(section_name)

    for folder_in_path1 in folders_on_surface_path:
        folder_matched = match_item(folder_in_path1, path_2)
        print(folder_matched)
        cf.set(section_name, folder_matched[0], folder_matched[1])
        cf.write(open(sf_data_path + r'Syncfile_data.ini', "w+", encoding='ANSI'))


def sync_files():
    pass


def syncfile_process():
    get_sf_data()
    all_files = scan_files_in(r"C:\Users\25674\Desktop\attempt")
    print(all_files)


if __name__ == '__main__':
    syncfile_process()
