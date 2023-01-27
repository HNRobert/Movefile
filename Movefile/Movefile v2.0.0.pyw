# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 17:07:30 2022

@author: Robert He
"""

vision = 'v2.0.0'
update_time = '2023/1/28-morning'

import base64
import configparser
import hashlib
import os
import psutil
import shutil
import time
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
import winreg
import win32api
import win32com.client as com
from datetime import datetime
import threading
import pystray
from PIL import Image
from pystray import MenuItem, Menu

import winshell
from win10toast import ToastNotifier

import Movefile_icon as icon
from ComBoPicker import Combopicker


def get_boot_time():
    boot_time = psutil.boot_time()  # 返回一个时间戳
    boot_time_obj = datetime.fromtimestamp(boot_time)
    now_time = datetime.now()
    delta_time = now_time - boot_time_obj
    boot_time_s = delta_time.days * 3600 * 24 + delta_time.seconds
    return boot_time_s


def scan_removable_disks(number=None):
    disk_list = []
    show_list = []
    num_disk_pairs = []
    for item in psutil.disk_partitions():
        # 判断是不是可移动磁盘
        if "removable" in item.opts:
            # 获取可移动磁盘的盘符
            if item.mountpoint not in disk_list:
                disk_list.append(item.mountpoint)
    if disk_list:
        for pf in disk_list:
            seria_data = win32api.GetVolumeInformation(pf)
            area_name = seria_data[0]
            area_number = seria_data[1]
            fso = com.Dispatch("Scripting.FileSystemObject")
            drv = fso.GetDrive(pf)
            total_space = drv.TotalSize / 2 ** 30
            show_name = area_name + ' (' + pf[:-1] + ')' + '   ' + str(total_space // 0.01 / 100) + ' GB'
            num_disk_pair = [str(area_number), show_name]
            show_list.append(show_name)
            num_disk_pairs.append(num_disk_pair)
        if number is None:
            return show_list
        else:
            for pair in num_disk_pairs:
                if pair[0] == number:
                    return pair[1]


def detect_removable_disks():
    global new_areas_data
    disk_list = []
    area_data_list = []
    number_book = {}
    new_areas_data = []
    while True:
        for item in psutil.disk_partitions():
            # 判断是不是可移动磁盘
            if "removable" in item.opts:
                # 获取可移动磁盘的盘符
                if item.mountpoint not in disk_list:
                    disk_list.append(item.mountpoint)
        if disk_list:
            for pf in disk_list:
                if not os.path.exists(pf):
                    disk_list.remove(pf)
                    area_data_list.remove(number_book[pf])
                else:
                    seria_number = win32api.GetVolumeInformation(pf)
                    area_name = seria_number[0]
                    area_number = seria_number[1]
                    if area_number not in area_data_list:
                        area_data_list.append(area_number)
                        number_book[pf] = area_number
                        new_areas_data.append([pf, area_name, area_number])
        time.sleep(2)


def set_data_path():
    try:
        global mf_data_path, cf_data_path, sf_data_path
    except:
        pass
    finally:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
        mf_data_path = roaming_path + '\\Movefile\\'
        cf_data_path = mf_data_path + 'Cleanfile\\'
        sf_data_path = mf_data_path + 'Syncfile\\'
        if 'Movefile' not in os.listdir(roaming_path):
            os.mkdir(mf_data_path)
        if 'Cleanfile' not in os.listdir(mf_data_path):
            os.mkdir(cf_data_path)
        if 'Syncfile' not in os.listdir(mf_data_path):
            os.mkdir(sf_data_path)


def asktime_plus():
    global toaster
    toaster = ToastNotifier()
    gencf = configparser.ConfigParser()
    time_now = datetime.today()
    date = str(time_now.date())
    if not os.path.exists(mf_data_path + r'Movefile_data.ini'):  # 创建配置文件
        file = open(mf_data_path + r'Movefile_data.ini', 'w', encoding="ANSI")
        file.close()
    gencf.read(mf_data_path + r'Movefile_data.ini')
    if not gencf.has_section("General"):
        gencf.add_section("General")
        gencf.set("General", "date", date)
        gencf.set("General", "asktime_today", '0')
    if gencf.get("General", "date") != str(date):
        gencf.set("General", "asktime_today", '0')
        gencf.set("General", "date", date)
    asktime_pre = gencf.getint("General", "asktime_today") + 1
    gencf.set("General", "asktime_today", str(asktime_pre))
    gencf.write(open(mf_data_path + r'Movefile_data.ini', "w+", encoding='ANSI'))


def list_saving_data():
    global last_saving_data, all_save_names, cf_save_names, sf_save_names
    cf_store_path = cf_data_path + r'Cleanfile_data.ini'
    sf_store_path = sf_data_path + r'Syncfile_data.ini'
    cf_file = configparser.ConfigParser()
    cf_file.read(cf_store_path)
    cf_save_names = cf_file.sections()
    sf_file = configparser.ConfigParser()
    sf_file.read(sf_store_path)
    sf_save_names = sf_file.sections()
    all_save_names = cf_save_names + sf_save_names
    for cf_save_name in cf_save_names:
        if cf_file.get(cf_save_name, '_last_edit_') == 'True':
            last_saving_data = ['cf', cf_save_name, sf_save_names[0]]
            break
    else:
        for sf_save_name in sf_save_names:
            if sf_file.get(sf_save_name, '_last_edit_') == 'True':
                last_saving_data = ['sf', sf_save_name, cf_save_names[0]]
                break
        else:
            if cf_save_names:
                last_saving_data = ['cf', cf_save_names[0], '']
            elif sf_save_names:
                last_saving_data = ['sf', sf_save_names[0], '']
            else:
                last_saving_data = ['', '', '']
    return last_saving_data


def data_error(mode_, name_):
    if mode_ == 'cf':
        try:
            cf = configparser.ConfigParser()
            cf.read(cf_data_path + r'Cleanfile_data.ini')  # 获取配置文件
            old_path_ = cf.get(name_, 'old_path')  # 旧文件夹
            new_path_ = cf.get(name_, 'new_path')  # 新文件夹
            move_folder = cf.get(name_, 'move_folder')
            autorun_ = cf.get(name_, 'autorun')
            cf.getint(name_, 'set_hour')  # 过期时间
            cf.getint(name_, 'mode')
            if os.path.exists(old_path_) and os.path.exists(new_path_):
                right_path = True
            else:
                right_path = False
            if (move_folder == 'True' or move_folder == 'False') and (autorun_ == 'True' or autorun_ == 'False'):
                right_option = True
            else:
                right_option = False

            if right_path and right_option:
                return False
            else:
                return True
        except:
            return True
    elif mode_ == 'sf':
        try:
            cf = configparser.ConfigParser()
            cf.read(sf_data_path + r'Syncfile_data.ini')
            if cf.has_option(name_, 'path_1'):
                path_1_ = cf.get(name_, 'path_1')
                usb_mode = False
            else:
                path_1_ = cf.get(name_, 'disk_number')
                usb_mode = True
            path_2_ = cf.get(name_, 'path_2')
            mode_s = cf.get(name_, 'mode')
            if not usb_mode:
                os.listdir(path_1_)
            os.listdir(path_2_)
            if not (mode_s == 'double' or mode_s == 'single'):
                return True
        except:
            return True


def get_desktop():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return winreg.QueryValueEx(key, "Desktop")[0]


def load_icon():
    image = open(mf_data_path + r'Movefile.ico', 'wb')
    image.write(base64.b64decode(icon.Movefile_ico))
    image.close()


def set_startup():
    # 将快捷方式添加到自启动目录
    # 获取用户名
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
    startup_path = os.path.join(roaming_path + r"\Microsoft\Windows\Start Menu\Programs\Startup")
    bin_path = r"Movefile " + vision + ".exe"
    shortcut_path = startup_path + "\\Movefile" + ".lnk"
    desc = "自动转移文件程序"
    icon_ = mf_data_path + r'Movefile.ico'
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
    winshell.CreateShortcut(
        Path=shortcut_path,
        Target=bin_path,
        Icon=(icon_, 0),
        Description=desc)


def filehash(filepath):
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()


def cf_move_dir(old__path, new__path, pass__file, pass__format, overdue_time, check__mode, is__move__folder,
                test=False):
    def cf_show_notice(old_path, new_path, movename, errorname):
        new_folder = new_path.split('\\')[-1]
        old_folder = old_path.split('\\')[-1]
        if len(movename) > 0:
            toaster.show_toast('These Files from ' + old_folder + ' are moved to ' + new_folder + ':',
                               movename,
                               icon_path=mf_data_path + r'Movefile.ico',
                               duration=10,
                               threaded=False)
        else:
            toaster.show_toast(old_folder + ' is pretty clean now',
                               'Nothing is moved away',
                               icon_path=mf_data_path + r'Movefile.ico',
                               duration=10,
                               threaded=False)
        if len(errorname) > 0:
            toaster.show_toast("Couldn't move files",
                               errorname[:-1] + """
    无法被移动，请在关闭文件或移除重名文件后重试""",
                               icon_path=mf_data_path + r'Movefile.ico',
                               duration=10,
                               threaded=False)

    cf_movename = ''
    cf_errorname = ''
    files = os.listdir(old__path)  # 获取文件夹下所有文件和文件夹
    for file in files:
        file_path = old__path + "/" + file
        pf = False
        for m in pass__format:
            file_end = '.' + file.split('.')[-1]
            if m == file_end:
                pf = True
        if file == ('Movefile ' + vision + '.exe' or new__path.split('\\')[-1]):
            continue
        is_folder = os.path.isdir(file)
        now = int(time.time())  # 当前时间
        if (not is_folder and ((file not in pass__file) and not pf)) or (
                is_folder and file not in pass__file and is__move__folder):  # 判断移动条件
            if check__mode == 1:
                last = int(os.stat(file_path).st_mtime)  # 最后一次修改的时间 (Option 1)
            elif check__mode == 2:
                last = int(os.stat(file_path).st_atime)  # 最后一次访问的时间 (Option 2)
            else:
                raise
            if (now - last >= overdue_time) and not test:  # 移动过期文件
                try:
                    shutil.move(file_path, new__path)
                    cf_movename += (file + ',  ')
                except:
                    cf_errorname += (file + ',  ')
    cf_show_notice(old__path, new__path, cf_movename, cf_errorname)


def cf_autorun_operation():
    cf_store_path = cf_data_path + r'Cleanfile_data.ini'
    cf_file = configparser.ConfigParser()
    cf_file.read(cf_store_path)

    def get_cf_autorun_savings():
        autorun_savings = []
        for cf_name in cf_save_names:
            if cf_file.get(cf_name, 'autorun') == 'True':
                autorun_savings.append(cf_name)
        return autorun_savings

    def autorun_cf(name):
        old_path = cf_file.get(name, 'old_path')  # 旧文件夹
        new_path = cf_file.get(name, 'new_path')  # 新文件夹
        pass_file = cf_file.get(name, 'pass_filename').split(',')  # 设置跳过白名单
        pass_format = cf_file.get(name, 'pass_format').split(',')  # 设置跳过格式
        time_ = cf_file.getint(name, 'set_hour') * 3600  # 设置过期时间(hour)
        mode = cf_file.getint(name, 'mode')  # 设置判断模式
        is_move_folder = cf_file.get(name, 'move_folder')  # 设置是否移动文件夹
        cf_move_dir(old__path=old_path, new__path=new_path, pass__file=pass_file, pass__format=pass_format,
                    overdue_time=time_,
                    check__mode=mode, is__move__folder=is_move_folder)

    run_saves = get_cf_autorun_savings()
    for save_name in run_saves:
        autorun_cf(save_name)


def sf_ask_operation():
    pass


def sf_scan_files(folder_path):  # 扫描路径下所有文件夹
    def scan_folders_in(f_path):  # 扫描目录下所有的文件夹，并返回路径列表
        surf_items = os.listdir(f_path)
        folder_store = [f_path]
        for item in surf_items:
            item_path = f_path + '\\' + item
            if os.path.isdir(item_path):
                folder_store.extend(scan_folders_in(item_path))  # 继续遍历文件夹内文件夹，直到记下全部文件夹路径
        folder_store = sorted(set(folder_store))  # 排序 + 排除重复项
        return folder_store

    file_store = []
    for folder in scan_folders_in(folder_path):  # 遍历所有文件夹
        files = [folder + '\\' + dI for dI in os.listdir(folder) if os.path.isfile(os.path.join(folder, dI))]
        # 如上只生成本文件夹内 文件的路径
        file_store.extend(files)  # 存储上面文件路径
    for i in range(len(file_store)):
        file_store[i] = file_store[i][len(folder_path)::]  # 返回相对位置
    return file_store


def sf_creat_folder(target_path):
    target = target_path.split('\\')[:-1]
    try_des = ''
    for fold in target:
        try_des += fold + '\\'
        if not os.path.exists(try_des):
            os.mkdir(try_des)


def sf_sync_file(file1_path, file2_path, no_judge=False, single_way=False):
    sf_errorname = ''
    last_edit_time_1 = int(os.stat(file1_path).st_mtime)
    if os.path.exists(file2_path):
        last_edit_time_2 = int(os.stat(file2_path).st_mtime)
    else:
        last_edit_time_2 = 0
    new_file, prior_file = '', ''
    pas = False
    if no_judge:
        sf_creat_folder(file2_path)
        try:
            shutil.copyfile(file1_path, file2_path)
        except:
            sf_errorname += file1_path + ' , '
        pas = True
    elif filehash(file1_path) == filehash(file2_path):
        pas = True
    elif last_edit_time_1 > last_edit_time_2:
        new_file = file1_path
        prior_file = file2_path
    elif last_edit_time_1 < last_edit_time_2 and not single_way:
        new_file = file2_path
        prior_file = file1_path
    else:
        pas = True

    if not pas:
        try:
            shutil.copyfile(new_file, prior_file)
        except:
            sf_errorname += new_file + ' , '
    return sf_errorname


def sf_match_possibility(path_1, path_2, file_1, file_2):  # 更新时间比较函数
    file1_name = file_1.split('\\')[-1]
    file2_name = file_2.split('\\')[-1]
    file1_path = path_1 + file_1
    file2_path = path_2 + file_2
    creat_time_1 = int(os.stat(file1_path).st_ctime)
    creat_time_2 = int(os.stat(file2_path).st_ctime)

    possibility = 0
    if file_2 == file_1:  # 比对相对路径
        possibility += 50
    if file2_name == file1_name:  # 比对文件名
        possibility += 30
    if creat_time_1 == creat_time_2:
        possibility += 20

    return possibility


def sync_dir(path1, path2, single_sync, area_name=None):
    def sf_show_notice(path_1, path_2, sf_errorname):
        toaster.show_toast('Sync Successfully',
                           'The Files in "' + path_1 + '" and "' + path_2 + '" are Synchronized',
                           icon_path=mf_data_path + r'Movefile.ico',
                           duration=10,
                           threaded=False)
        if len(sf_errorname) > 0:
            toaster.show_toast("Couldn't sync files",
                               sf_errorname + """
        无法被移动，请在关闭文件或移除重名文件后重试""",
                               icon_path=mf_data_path + r'Movefile.ico',
                               duration=10,
                               threaded=False)

    def get_task():
        all_files_1 = sf_scan_files(path1)
        all_files_2 = sf_scan_files(path2)
        sync_tasks = []
        task_number = 0
        for file1 in all_files_1:
            file1_path = path1 + file1
            for file2 in all_files_2:
                file2_path = path2 + file2
                match_possibility = sf_match_possibility(path1, path2, file1, file2)
                if match_possibility > 50:
                    task_number += 1
                    show_filename['text'] = f'扫描文件中...  发现新项目{task_number}个'
                    sync_tasks.append([file1_path, file2_path, False, single_sync])
                    break
                elif match_possibility == 50:
                    sf_ask_operation()
            else:
                task_number += 1
                show_filename['text'] = f'扫描文件中...  发现新项目{task_number}个'
                sync_tasks.append([file1_path, path2 + file1, True, single_sync])
        if not single_sync:
            for file2 in all_files_2:
                file2_path = path2 + file2
                if file2 not in all_files_1:
                    task_number += 1
                    show_filename['text'] = f'扫描文件中...  发现新项目{task_number}个'
                    sync_tasks.append([file2_path, path1 + file2, True, single_sync])
        return sync_tasks

    def run_sync_tasks():
        out_data = ''
        progress_bar['value'] = 0
        sync_bar.update()
        tasks = get_task()
        progress_bar['maximum'] = len(tasks)
        for task in tasks:
            show_filename['text'] = '文件同步中：' + task[0].split('\\')[-1]
            out_data += sf_sync_file(task[0], task[1], task[2], task[3])
            progress_bar['value'] += 1
            sync_bar.update()
        sync_bar.withdraw()
        path_name_1 = path1.split('\\')[-1]
        if area_name:
            path_name_1 = area_name
        try:
            sf_show_notice(path_name_1, path2.split('\\')[-1], out_data)
        except:
            pass

    def sync_bar_on_exit():
        global stop_sync
        stop_sync = False
        if tkinter.messagebox.askyesno(title='Syncfile', message='''文件正在同步中，
确定中断同步进程并退出?'''):
            stop_sync = True

    sync_bar = tk.Tk()
    sync_bar.title('Movefile  -Syncfile Progress')
    sync_bar.geometry('420x60')
    show_filename = ttk.Label(sync_bar, text='扫描文件中...')
    show_filename.grid(row=0, column=0, padx=10, pady=5, sticky='SW')
    progress_bar = ttk.Progressbar(sync_bar)
    progress_bar.grid(row=1, column=0, padx=10, pady=0, ipadx=150)
    run_sync_tasks()
    sync_bar.protocol('WM_DELETE_WINDOW', lambda: sync_bar_on_exit())
    sync_bar.mainloop()


def sf_autorun_operation(place, saving_datas=None):
    sf_file = configparser.ConfigParser()
    sf_file.read(sf_data_path + 'Syncfile_data.ini')

    def get_sf_startup_savings():
        sf_startup_settings = []
        for section in sf_file.sections():
            if sf_file.get(section, 'place_mode') == 'local' and sf_file.get(section, 'autorun') == 'True':
                sf_startup_settings.append(section)
        return sf_startup_settings

    def autorun_movable_sf(data):
        for saving_data in data:
            path1 = saving_data[0]
            path2 = sf_file.get(saving_data[2], 'path_2')
            single_sync = True
            if sf_file.get(saving_data[2], 'mode') == 'double':
                single_sync = False
            sync_dir(path1, path2, single_sync, saving_data[1])

    def autorun_local_sf(data_name):
        for saving_data in data_name:
            path1 = sf_file.get(saving_data, 'path_1')
            path2 = sf_file.get(saving_data, 'path_2')
            single_sync = True
            if sf_file.get(saving_data, 'mode') == 'double':
                single_sync = False
            sync_dir(path1, path2, single_sync)

    if place == 'movable':
        autorun_movable_sf(saving_datas)
    elif place == 'local':
        autorun_savings = get_sf_startup_savings()
        autorun_local_sf(autorun_savings)


def make_ui(muti_ask=False, first_ask=False, startup_ask=False):
    cf_data = configparser.ConfigParser()
    sf_data = configparser.ConfigParser()
    cf_ori_old_path = ''

    def cf_refresh_whitelist_entry():
        nonlocal cf_ori_old_path
        all_ends = []
        file_names = []
        folder_names = []
        item_names = os.listdir(cf_entry_old_path.get())
        if cf_ori_old_path != cf_entry_old_path.get():
            cf_entry_keep_files.delete(0, 'end')
            cf_entry_keep_formats.delete(0, 'end')
            cf_ori_old_path = cf_entry_old_path.get()
        for item in item_names:
            if os.path.isfile(cf_entry_old_path.get() + '\\' + item):
                file_end = '.' + item.split('.')[-1]
                all_ends.append(file_end)
                file_names.append(item)
            elif os.path.isdir(cf_entry_old_path.get() + '\\' + item) and cf_is_folder_move.get():
                folder_names.append(item)
        exist_ends = sorted(set(all_ends))

        keep_file_values = ['全选'] + folder_names + file_names
        cf_entry_keep_files.values = keep_file_values
        past_values = cf_entry_keep_files.get().split(',')
        new_values = ''
        for past_value in past_values:
            if past_value in keep_file_values:
                new_values += past_value + ','
        if new_values:
            new_values = new_values[:-1]
        cf_entry_keep_files.delete(0, 'end')
        cf_entry_keep_files.insert(0, new_values)

        keep_format_values = ['全选'] + exist_ends
        cf_entry_keep_formats.values = keep_format_values
        past_values = cf_entry_keep_formats.get().split(',')
        new_values = ''
        for past_value in past_values:
            if past_value in keep_format_values:
                new_values += past_value + ','
        if new_values:
            new_values = new_values[:-1]
        cf_entry_keep_formats.delete(0, 'end')
        cf_entry_keep_formats.insert(0, new_values)

    def sf_refresh_disk_list(none_disk=False):
        disk_list = scan_removable_disks()
        if disk_list:
            sf_entry_select_removable['values'] = disk_list
        else:
            sf_entry_select_removable['values'] = ['未检测到可移动磁盘']
            if none_disk:
                sf_entry_select_removable.delete(0, 'end')

    def select_path(place, ori_content):
        path_ = tkinter.filedialog.askdirectory()
        path_ = path_.replace("/", "\\")
        if path_ != '' and path_ != ori_content:
            if place == 'old':
                oldpath.set(path_)
                cf_refresh_whitelist_entry()
            elif place == 'new':
                newpath.set(path_)
            elif place == '1':
                path_1.set(path_)
            elif place == '2':
                path_2.set(path_)

    def sf_change_place_mode(mode):
        if mode == 'movable':
            sf_label_path_1['text'] = '选择可移动磁盘：'
            sf_label_path_2['text'] = '本地文件夹路径：'
            sf_option_autorun['text'] = '可移动磁盘接入后自动按本存档设置同步(若保存)'
            sf_browse_path_1_button.grid_forget()
            sf_entry_select_removable.grid(row=2, column=1, padx=10, pady=5, ipadx=231, sticky='W')
        else:
            sf_label_path_1['text'] = '文件夹路径-A：'
            sf_label_path_2['text'] = '文件夹路径-B：'
            sf_option_autorun['text'] = '开机自动运行本存档(若保存)'
            sf_browse_path_1_button.grid(row=2, column=1, ipadx=3, sticky='E', padx=10)
            sf_entry_select_removable.grid_forget()

    def change_active_mode(mode):
        def cf_state():
            sf_label_place_mode.grid_forget()
            sf_option_mode_usb.grid_forget()
            sf_option_mode_local.grid_forget()
            sf_label_path_1.grid_forget()
            sf_label_path_2.grid_forget()
            sf_entry_path_1.grid_forget()
            sf_entry_path_2.grid_forget()
            sf_entry_select_removable.grid_forget()
            sf_browse_path_1_button.grid_forget()
            sf_browse_path_2_button.grid_forget()
            sf_option_mode_double.grid_forget()
            sf_option_mode_single.grid_forget()
            sf_label_mode.grid_forget()
            sf_label_lock_folder.grid_forget()
            sf_entry_lock_files.grid_forget()
            sf_label_match_directly.grid_forget()
            sf_entry_match_directly.grid_forget()
            sf_label_autorun.grid_forget()
            sf_option_autorun.grid_forget()

            cf_entry_old_path.grid(row=1, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            cf_browse_old_path_button.grid(row=1, column=1, ipadx=3, sticky='E', padx=10)
            cf_entry_new_path.grid(row=2, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            cf_browse_new_path_button.grid(row=2, column=1, ipadx=3, sticky='E', padx=10)
            cf_option_mode_1.grid(row=3, column=1, padx=10, ipadx=0, sticky='W')
            cf_option_mode_2.grid(row=3, column=1, padx=175, ipadx=0, sticky='E')
            cf_option_folder_move.grid(row=3, column=1, padx=10, sticky='E')
            cf_entry_keep_files.grid(row=2, column=1, ipadx=240, pady=5, sticky='W')
            cf_entry_keep_formats.grid(row=3, column=1, ipadx=240, pady=0, sticky='W')
            cf_entry_time.grid(row=6, column=1, padx=10, pady=5, ipadx=240, sticky='W')
            cf_option_is_auto.grid(row=7, column=1, padx=10, sticky='NW')
            cf_label_old_path.grid(row=1, column=0, pady=5, sticky='E')
            cf_label_new_path.grid(row=2, column=0, pady=5, sticky='E')
            cf_label_move_options.grid(row=3, column=0, pady=5, sticky='E')
            cf_label_keep_files.grid(row=4, column=0, pady=5, sticky='E')
            cf_label_keep_formats.grid(row=5, column=0, sticky='E')
            cf_label_time.grid(row=6, column=0, sticky='E')
            cf_label_start_options.grid(row=7, column=0, sticky='E')

        def sf_state():
            cf_entry_old_path.grid_forget()
            cf_browse_old_path_button.grid_forget()
            cf_entry_new_path.grid_forget()
            cf_browse_new_path_button.grid_forget()
            cf_option_mode_1.grid_forget()
            cf_option_mode_2.grid_forget()
            cf_option_folder_move.grid_forget()
            cf_entry_keep_files.grid_forget()
            cf_entry_keep_formats.grid_forget()
            cf_entry_time.grid_forget()
            cf_option_is_auto.grid_forget()
            cf_label_old_path.grid_forget()
            cf_label_new_path.grid_forget()
            cf_label_move_options.grid_forget()
            cf_label_keep_files.grid_forget()
            cf_label_keep_formats.grid_forget()
            cf_label_time.grid_forget()
            cf_label_start_options.grid_forget()

            if sf_place_mode.get() == 'movable':
                sf_change_place_mode('movable')
            else:
                sf_change_place_mode('local')

            sf_label_place_mode.grid(row=1, column=0, pady=5, sticky='E')
            sf_option_mode_usb.grid(row=1, column=1, padx=10, sticky='W')
            sf_option_mode_local.grid(row=1, column=1, padx=200, sticky='W')
            sf_label_path_1.grid(row=2, column=0, pady=5, sticky='E')
            sf_label_path_2.grid(row=3, column=0, pady=5, sticky='E')
            sf_entry_path_1.grid(row=2, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_entry_path_2.grid(row=3, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_browse_path_2_button.grid(row=3, column=1, ipadx=3, sticky='E', padx=10)
            sf_option_mode_double.grid(row=4, column=1, padx=10, ipadx=0, sticky='W')
            sf_option_mode_single.grid(row=4, column=1, padx=165, ipadx=0, sticky='E')
            sf_label_mode.grid(row=4, column=0, pady=5, sticky='E')
            sf_label_lock_folder.grid(row=5, column=0, pady=5, sticky='E')
            sf_entry_lock_files.grid(row=5, column=1, padx=10, pady=5, ipadx=240, sticky='W')
            sf_label_match_directly.grid(row=6, column=0, pady=5, sticky='E')
            sf_entry_match_directly.grid(row=6, column=1, padx=10, pady=5, ipadx=240, sticky='W')
            sf_label_autorun.grid(row=7, column=0, sticky='E')
            sf_option_autorun.grid(row=7, column=1, padx=10, sticky='W')

        if mode == 'cf':
            cf_state()
        else:
            sf_state()

    root = tk.Tk()
    root.iconbitmap(mf_data_path + r'Movefile.ico')
    oldpath = tk.StringVar()
    newpath = tk.StringVar()
    path_1 = tk.StringVar()
    path_2 = tk.StringVar()
    root.title('Movefile Setting')
    root.geometry("800x310")

    label_choose_state = ttk.Label(root, text='功能选择：')
    label_choose_state.grid(row=0, column=0, pady=5, sticky='E')
    cf_or_sf = tk.StringVar()
    option_is_cleanfile = ttk.Radiobutton(root, text='清理文件', variable=cf_or_sf, value='cf',
                                          command=lambda: change_active_mode(cf_or_sf.get()))
    option_is_cleanfile.grid(row=0, column=1, padx=10, pady=5, sticky='W')
    option_is_syncfile = ttk.Radiobutton(root, text='同步文件', variable=cf_or_sf, value='sf',
                                         command=lambda: change_active_mode(cf_or_sf.get()))
    option_is_syncfile.grid(row=0, column=1, padx=100, pady=5, sticky='W')

    cf_label_old_path = ttk.Label(root, text="原文件夹路径：")
    cf_label_old_path.grid(row=1, column=0, pady=5, sticky='E')
    cf_entry_old_path = ttk.Entry(root, textvariable=oldpath)
    cf_entry_old_path.grid(row=1, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    cf_browse_old_path_button = ttk.Button(root, text="浏览", command=lambda: select_path(place='old',
                                                                                          ori_content=cf_entry_old_path.get()))
    cf_browse_old_path_button.grid(row=1, column=1, ipadx=3, sticky='E', padx=10)

    cf_label_new_path = ttk.Label(root, text='新文件夹路径：')
    cf_label_new_path.grid(row=2, column=0, pady=5, sticky='E')
    cf_entry_new_path = ttk.Entry(root, textvariable=newpath)
    cf_entry_new_path.grid(row=2, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    cf_browse_new_path_button = ttk.Button(root, text="浏览", command=lambda: select_path(place='new',
                                                                                          ori_content=cf_entry_new_path.get()))
    cf_browse_new_path_button.grid(row=2, column=1, ipadx=3, sticky='E', padx=10)

    cf_label_move_options = ttk.Label(root, text='文件移动选项：')
    cf_label_move_options.grid(row=3, column=0, pady=5, sticky='E')
    cf_entry_mode = tk.IntVar()
    cf_option_mode_1 = ttk.Radiobutton(root, text="以项目最后修改时间为过期判断依据", variable=cf_entry_mode, value=1)
    cf_option_mode_1.grid(row=3, column=1, padx=10, ipadx=0, sticky='W')
    cf_option_mode_2 = ttk.Radiobutton(root, text="以项目最后访问时间为过期判断依据", variable=cf_entry_mode, value=2)
    cf_option_mode_2.grid(row=3, column=1, padx=175, ipadx=0, sticky='E')
    cf_is_folder_move = tk.BooleanVar()
    cf_option_folder_move = ttk.Checkbutton(root, text='移动项目包括文件夹', variable=cf_is_folder_move)
    cf_option_folder_move.grid(row=3, column=1, padx=10, sticky='E')

    cf_entry_frame_keep_files = tk.Frame(root)
    cf_entry_frame_keep_files.grid(row=4, column=1, ipadx=5, sticky='E')
    cf_label_keep_files = ttk.Label(root, text='保留项目(选填)：')
    cf_label_keep_files.grid(row=4, column=0, pady=5, sticky='E')
    cf_entry_keep_files = Combopicker(master=cf_entry_frame_keep_files, values='', frameheight=120)
    cf_entry_keep_files.grid(row=4, column=1, ipadx=240, pady=0, sticky='W')
    cf_entry_keep_files.bind('<Button-1>', lambda event: cf_refresh_whitelist_entry())

    cf_entry_frame_keep_formats = tk.Frame(root)
    cf_entry_frame_keep_formats.grid(row=5, column=1, pady=5, ipadx=5, sticky='E')
    cf_label_keep_formats = ttk.Label(root, text='     保留文件格式(选填)：')
    cf_label_keep_formats.grid(row=5, column=0, sticky='E')
    cf_entry_keep_formats = Combopicker(master=cf_entry_frame_keep_formats, values='', frameheight=90)
    cf_entry_keep_formats.grid(row=5, column=1, ipadx=240, pady=0, sticky='W')
    cf_entry_keep_formats.bind('<Button-1>', lambda event: cf_refresh_whitelist_entry())

    cf_label_time = ttk.Label(root, text='过期时间设定(小时)：')
    cf_label_time.grid(row=6, column=0, sticky='E')
    cf_entry_time = ttk.Entry(root)
    cf_entry_time.grid(row=6, column=1, padx=10, pady=5, ipadx=240, sticky='W')

    cf_label_start_options = ttk.Label(root, text='系统选项：')
    cf_label_start_options.grid(row=7, column=0, sticky='E')
    cf_is_autorun = tk.BooleanVar()
    cf_option_is_auto = ttk.Checkbutton(root, text='开机自动运行本存档(若保存)', variable=cf_is_autorun)
    cf_option_is_auto.grid(row=7, column=1, padx=10, sticky='NW')

    sf_label_place_mode = ttk.Label(root, text='路径模式选择：')
    sf_label_place_mode.grid(row=1, column=0, pady=5, sticky='E')
    sf_place_mode = tk.StringVar()
    sf_option_mode_usb = ttk.Radiobutton(root, text='可移动磁盘(卷)同步模式',
                                         variable=sf_place_mode,
                                         value='movable',
                                         command=lambda: sf_change_place_mode(mode=sf_place_mode.get()))
    sf_option_mode_usb.grid(row=1, column=1, padx=10, sticky='W')
    sf_option_mode_local = ttk.Radiobutton(root, text='本地文件夹同步模式',
                                           variable=sf_place_mode,
                                           value='local',
                                           command=lambda: sf_change_place_mode(mode=sf_place_mode.get()))
    sf_option_mode_local.grid(row=1, column=1, padx=200, sticky='W')
    sf_place_mode.set('movable')

    sf_label_path_1 = ttk.Label(root, text="文件夹路径-A：")
    sf_label_path_1.grid(row=2, column=0, pady=5, sticky='E')
    sf_entry_path_1 = ttk.Entry(root, textvariable=path_1)
    sf_entry_path_1.grid(row=2, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    sf_browse_path_1_button = ttk.Button(root, text="浏览",
                                         command=lambda: select_path(place='1', ori_content=sf_entry_path_1.get()))
    sf_browse_path_1_button.grid(row=2, column=1, ipadx=3, sticky='E', padx=10)

    sf_entry_select_removable = ttk.Combobox(root, values=scan_removable_disks(), state='readonly')
    sf_entry_select_removable.grid(row=2, column=1, padx=10, pady=5, ipadx=231, sticky='W')
    sf_entry_select_removable.bind('<Button-1>', lambda event: sf_refresh_disk_list())

    sf_label_path_2 = ttk.Label(root, text='文件夹路径-B：')
    sf_label_path_2.grid(row=3, column=0, pady=5, sticky='E')
    sf_entry_path_2 = ttk.Entry(root, textvariable=path_2)
    sf_entry_path_2.grid(row=3, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    sf_browse_path_2_button = ttk.Button(root, text="浏览",
                                         command=lambda: select_path(place='2', ori_content=sf_entry_path_2.get()))
    sf_browse_path_2_button.grid(row=3, column=1, ipadx=3, sticky='E', padx=10)

    sf_label_mode = ttk.Label(root, text='             同步模式选择：')
    sf_label_mode.grid(row=4, column=0, pady=5, sticky='E')
    sf_entry_mode = tk.StringVar()
    sf_option_mode_double = ttk.Radiobutton(root, text="双向同步（皆保留最新版本）", variable=sf_entry_mode,
                                            value='double')
    sf_option_mode_double.grid(row=4, column=1, padx=10, ipadx=0, sticky='W')
    sf_option_mode_single = ttk.Radiobutton(root, text="单向同步（来自路径B的新数据不会同步到路径A）",
                                            variable=sf_entry_mode,
                                            value='single')
    sf_option_mode_single.grid(row=4, column=1, padx=165, ipadx=0, sticky='E')

    sf_label_lock_folder = ttk.Label(root, text='锁定文件夹(开发中)：')
    sf_label_lock_folder.grid(row=5, column=0, pady=5, sticky='E')
    sf_entry_lock_files = ttk.Entry(root)
    sf_entry_lock_files.grid(row=5, column=1, padx=10, pady=5, ipadx=240, sticky='W')
    sf_entry_lock_files.config(state=tk.DISABLED)

    sf_label_match_directly = ttk.Label(root, text='手动配对(开发中)：')
    sf_label_match_directly.grid(row=6, column=0, pady=5, sticky='E')
    sf_entry_match_directly = ttk.Entry(root)
    sf_entry_match_directly.grid(row=6, column=1, padx=10, pady=5, ipadx=240, sticky='W')
    sf_entry_match_directly.config(state=tk.DISABLED)

    sf_label_autorun = ttk.Label(root, text='系统选项：')
    sf_label_autorun.grid(row=7, column=0, sticky='E')
    sf_entry_is_autorun = tk.BooleanVar()
    sf_option_autorun = ttk.Checkbutton(root,
                                        text='可移动磁盘接入后自动同步',
                                        variable=sf_entry_is_autorun)
    sf_option_autorun.grid(row=7, column=1, padx=10, sticky='W')

    def help_main():
        tkinter.messagebox.showinfo(title='Movefile', message="""软件名称： Movefile
软件版本： """ + vision + """               更新时间： """ + update_time + """

功能概述：
本程序可将某个文件夹中满足一定设定要求的文件
转移到另一个文件夹，或者与另外一个文件夹同步
使你可以方便地整理文件

如果对本软件功能有任何疑惑，可以查看菜单栏中的 "帮助" 选项

作者：Robert He
如果对本软件有任何改进意见，请联系作者
如果意见被采纳，新版本中会进行更改

如有功能异常请先访问 Github 查看有无新版本，
或者阅读 Github 中的其他注意事项和运行机制说明
地址：https://github.com/HNRobert/Movefile
""")

    def help_before_use():
        tkinter.messagebox.showinfo(title='Movefile', message="""使用前特别注意事项：
1.本软件必须在64位操作系统下运行，
  后续将推出32位操作系统版本
2.本exe文件的名称请不要改变："Movefile """ + vision + """.exe"
  否则会影响开机自启功能
3.使用本软件前请打开Windows设置中的
  系统/通知和操作/通知/
  “获取来自应用和其他发送者的通知” 选项，
  否则会影响操作结果通知功能
4.使用本软件前请先将本软件放入
  Windows安全中心的防病毒扫描排除项中，
  否则在运行时会被直接删除
  这是因为本软件涉及更改开机启动项。
  如果本软件在使用中被意外删除，
  请在Windows安全中心中
  病毒威胁和防护的 "保护历史记录"
  或其他安全软件中找回本软件
5.如果经过版本新后软件无法运行，
  可以尝试删除位于Roaming文件夹中的配置文件
6.若有其他原因导致软件功能无法正常运行，
  且无法按上面的解释修复，可以访问 Github 网站
  或直接联系作者（QQ:2567466856），我会尽快尝试帮你修复""")

    def cf_help():
        tkinter.messagebox.showinfo(title='Movefile', message="""Cleanfile
清理文件工具

这是一个用来整理文件夹（尤其是桌面）的程序，
也是Movefile推出的第一个程序块
包含选取保留文件，保留文件类型
设定是否移动文件夹，
设定过期时间以及判断方式
开机自动运行存档等功能""")

    def cf_help_keep():
        tkinter.messagebox.showinfo(title='Movefile', message="""保留项目/文件格式选择功能详解：

保留项目选择：
选中的项目不会被转移

保留文件格式选择：
某种格式类型的文件都不会被转移
比如选中'.lnk'，即表示原文件夹中所有的快捷方式不会被转移""")

    def cf_help_timeset():
        tkinter.messagebox.showinfo(title='Movefile', message="""过期时间功能详解：

本软件可以获取文件的最后修改、访问时间
可以保留一定时间内修改/访问过的文件
例如若将过期时间设为"48"，判定方式设为"以最后修改时间为依据"
则运行日期前两天内修改过的文件不会被删除
如果不想用此方法，则过期时间设为"0"即可""")

    def sf_help():
        tkinter.messagebox.showinfo(title='Movefile', message='''Syncfile
同步文件工具

这是一个用来同步文件两个路径下文件的程序，
也可以将U盘数据与电脑同步

包括 可移动磁盘与本地磁盘 与 本地磁盘间同步 两种模式选择，
选择单向与双向同步模式，保留最新更改文件
开机自动运行存档
自动检测选定的可移动磁盘接入并自动同步等功能''')

    def cf_is_num():
        try:
            float(cf_entry_time.get())
        except:
            return False
        else:
            return True

    def cf_has_blank():
        blank = 0
        if len(cf_entry_old_path.get()) == 0:
            blank += 1
        elif len(cf_entry_new_path.get()) == 0:
            blank += 1
        elif len(cf_entry_time.get()) == 0:
            blank += 1
        elif cf_entry_mode.get() == 0:
            blank += 1
        if blank == 0:
            return False
        else:
            return True

    def cf_path_error():
        try:
            os.listdir(cf_entry_old_path.get())
            os.listdir(cf_entry_new_path.get())
        except:
            return True
        else:
            return False

    def sf_has_blank():
        blank = 0
        if sf_place_mode.get() == 'movable' and len(sf_entry_select_removable.get()) == 0:
            blank += 1
        elif sf_place_mode.get() == 'local' and len(sf_entry_path_1.get()) == 0:
            blank += 1
        elif len(sf_entry_path_2.get()) == 0:
            blank += 1
        if blank == 0:
            return False
        else:
            return True

    def sf_path_error():
        try:
            if sf_place_mode.get() == 'movable':
                os.listdir(sf_entry_select_removable.get().split(':')[0][-1] + ':')
            else:
                os.listdir(sf_entry_path_1.get())
            os.listdir(sf_entry_path_2.get())
        except:
            return True
        else:
            return False

    def cf_has_error():
        if not cf_is_num():
            tkinter.messagebox.showwarning('Movefile', '警告：请在时间设定栏内输入数字')
            return True
        elif cf_has_blank():
            tkinter.messagebox.showwarning(title='Movefile', message='警告：请填写所有非选填项目！')
            return True
        elif cf_path_error():
            tkinter.messagebox.showwarning(title='Movefile', message='警告：请填输入有效路径！（建议使用浏览）')
            return True
        else:
            return False

    def sf_has_error():
        if sf_has_blank():
            tkinter.messagebox.showwarning(title='Movefile', message='警告：请填写所有非选填项目！')
            return True
        elif sf_path_error():
            tkinter.messagebox.showwarning(title='Movefile', message='警告：请填输入有效路径！（建议使用浏览）')
            return True
        else:
            return False

    def savefile(mode, save_name='New_Setting'):  # 保存文件
        cf_data.read(cf_data_path + r'Cleanfile_data.ini')
        sf_data.read(sf_data_path + r'Syncfile_data.ini')
        list_saving_data()

        if len(cf_save_names) != 0:  # 更改上次修改项
            for cf_save in cf_save_names:
                try:
                    cf_data.set(cf_save, '_last_edit_', 'False')
                    cf_data.write(open(cf_data_path + r'Cleanfile_data.ini', 'w+', encoding='ANSI'))
                except:
                    pass
        if len(sf_save_names) != 0:
            for sf_save in sf_save_names:
                try:
                    sf_data.set(sf_save, '_last_edit_', 'False')
                    sf_data.write(open(sf_data_path + r'Syncfile_data.ini', 'w+', encoding='ANSI'))
                except:
                    pass

        if mode == 'cf':  # 如果当前界面为cf
            if not os.path.exists(cf_data_path + r'Cleanfile_data.ini'):
                file = open(cf_data_path + r'Cleanfile_data.ini', 'w', encoding='ANSI')
                file.close()
            cf_data.read(cf_data_path + r'Cleanfile_data.ini')
            if not cf_data.has_section(str(save_name)):
                cf_data.add_section(str(save_name))
            cf_data.set(save_name, '_last_edit_', 'True')
            cf_data.set(save_name, "old_path", cf_entry_old_path.get())
            cf_data.set(save_name, "new_path", cf_entry_new_path.get())
            cf_data.set(save_name, "pass_filename", cf_entry_keep_files.get())
            cf_data.set(save_name, "pass_format", cf_entry_keep_formats.get())
            cf_data.set(save_name, "set_hour", cf_entry_time.get())
            cf_data.set(save_name, "mode", str(cf_entry_mode.get()))
            cf_data.set(save_name, "autorun", str(cf_is_autorun.get()))
            cf_data.set(save_name, "move_folder", str(cf_is_folder_move.get()))
            cf_data.write(open(cf_data_path + r'Cleanfile_data.ini', "w+", encoding='ANSI'))

        if mode == 'sf':  # 如果当前界面为sf
            if not os.path.exists(sf_data_path + r'Syncfile_data.ini'):
                file = open(sf_data_path + r'Syncfile_data.ini', 'w', encoding='ANSI')
                file.close()
            sf_data.read(sf_data_path + r'Syncfile_data.ini')
            if not sf_data.has_section(str(save_name)):
                sf_data.add_section(str(save_name))
            sf_data.set(save_name, '_last_edit_', 'True')
            sf_data.set(save_name, 'place_mode', sf_place_mode.get())
            if sf_place_mode.get() == 'local':
                sf_data.set(save_name, 'path_1', sf_entry_path_1.get())
            else:
                disk_data = sf_entry_select_removable.get()
                sf_data.set(save_name, 'disk_number',
                            str(win32api.GetVolumeInformation(disk_data.split(':')[0][-1] + ':')[1]))
            sf_data.set(save_name, 'path_2', sf_entry_path_2.get())
            sf_data.set(save_name, 'mode', sf_entry_mode.get())
            sf_data.set(save_name, 'lock_path', sf_entry_lock_files.get())
            sf_data.set(save_name, 'autorun', str(sf_entry_is_autorun.get()))
            sf_data.write(open(sf_data_path + r'Syncfile_data.ini', 'w+', encoding='ANSI'))

        tkinter.messagebox.showinfo(title='信息提示', message='信息保存成功！')
        bt2.config(state=tk.NORMAL)

    def read_saving(ask_path=False):
        cf_store_path = cf_data_path + r'Cleanfile_data.ini'
        sf_store_path = sf_data_path + r'Syncfile_data.ini'
        cf_file = configparser.ConfigParser()
        cf_file.read(cf_store_path)  # 获取配置文件
        sf_file = configparser.ConfigParser()
        sf_file.read(sf_store_path)
        new_values = []

        last_data = ['', '']
        if list_saving_data():
            last_data = list_saving_data()
        mode = last_data[0]
        save_name = last_data[1]

        def open_cf_saving(setting_name):
            nonlocal cf_ori_old_path
            if cf_entry_old_path.get() != '':
                cf_entry_old_path.delete(0, 'end')
            if cf_entry_new_path.get() != '':
                cf_entry_new_path.delete(0, 'end')
            cf_entry_old_path.insert(0, cf_file.get(setting_name, 'old_path'))  # 旧文件夹
            cf_ori_old_path = cf_entry_old_path.get()
            cf_entry_new_path.insert(0, cf_file.get(setting_name, 'new_path'))  # 新文件夹
            cf_refresh_whitelist_entry()
            if cf_entry_keep_files.get() != '':
                cf_entry_keep_files.delete(0, 'end')
            if cf_entry_keep_formats.get() != '':
                cf_entry_keep_formats.delete(0, 'end')
            if cf_entry_time.get() != '':
                cf_entry_time.delete(0, 'end')
            cf_entry_keep_files.insert(0, cf_file.get(setting_name, 'pass_filename'))  # 设置跳过白名单
            cf_entry_keep_formats.insert(0, cf_file.get(setting_name, 'pass_format'))  # 设置跳过格式
            cf_entry_time.insert(0, cf_file.get(setting_name, 'set_hour'))  # 设置过期时间(hour)
            cf_entry_mode.set(cf_file.getint(setting_name, 'mode'))  # 设置判断模式
            cf_is_autorun.set(cf_file.get(setting_name, 'autorun'))
            cf_is_folder_move.set(cf_file.get(setting_name, 'move_folder'))
            change_active_mode('cf')
            cf_or_sf.set('cf')
            if data_error('cf', setting_name):
                tkinter.messagebox.showwarning(title='Movefile', message='''错误：配置信息无效！
请尽量不要手动更改ini配置文件''')

        def open_sf_saving(setting_name):
            if sf_entry_path_1.get() != '':
                sf_entry_path_1.delete(0, 'end')
            if sf_entry_path_2.get() != '':
                sf_entry_path_2.delete(0, 'end')
            place_mode = sf_file.get(setting_name, 'place_mode')
            sf_place_mode.set(place_mode)
            sf_change_place_mode(place_mode)
            if not cf_entry_old_path.get():
                cf_entry_old_path.insert(0, get_desktop())
            cf_refresh_whitelist_entry()
            if place_mode == 'local':
                sf_entry_path_1.insert(0, sf_file.get(setting_name, 'path_1'))
            else:
                area_number = sf_file.get(setting_name, 'disk_number')
                sf_entry_select_removable.delete(0, 'end')
                sf_last_data = scan_removable_disks(area_number)
                count_i = 0
                for value in sf_entry_select_removable['values']:
                    if sf_last_data == value:
                        sf_entry_select_removable.current(count_i)
                        break
                    count_i += 1
            sf_entry_path_2.insert(0, sf_file.get(setting_name, 'path_2'))
            sf_entry_mode.set(sf_file.get(setting_name, 'mode'))
            sf_entry_is_autorun.set(sf_file.get(setting_name, 'autorun'))
            change_active_mode('sf')
            cf_or_sf.set('sf')
            if data_error('sf', setting_name):
                tkinter.messagebox.showwarning(title='Movefile', message='''错误：配置信息无效！
请尽量不要手动更改ini配置文件''')

        def refresh_saving():
            nonlocal new_values
            try:
                list_saving_data()
                if mode_entry.get() == '清理文件(Cleanfile)':
                    new_values = cf_save_names
                    name_entry['value'] = new_values
                elif mode_entry.get() == '同步文件(Syncfile)':
                    new_values = sf_save_names
                    name_entry['value'] = new_values
                else:
                    new_values = []
                if name_entry.get() not in new_values:
                    name_entry.delete(0, 'end')
            except:
                pass

        def del_saving():
            del_mode = mode_entry.get()
            del_name = name_entry.get()
            is_continue = tk.messagebox.askyesno(title='Movefile', message='确认删除配置 ' + del_name + ' ?')
            ini_file = configparser.ConfigParser()
            if del_mode == '清理文件(Cleanfile)' and is_continue:
                ini_file.read(cf_data_path + 'Cleanfile_data.ini')
                ini_file.remove_section(del_name)
                ini_file.write(open(cf_data_path + r'Cleanfile_data.ini', 'w+', encoding='ANSI'))
            elif del_mode == '同步文件(Syncfile)' and is_continue:
                ini_file.read(sf_data_path + 'Syncfile_data.ini')
                ini_file.remove_section(del_name)
                ini_file.write(open(sf_data_path + r'Syncfile_data.ini', 'w+', encoding='ANSI'))

        def sure_open():
            saving_name = name_entry.get()
            if mode_entry.get() == '清理文件(Cleanfile)':
                open_cf_saving(saving_name)
            elif mode_entry.get() == '同步文件(Syncfile)':
                open_sf_saving(saving_name)
            root.title('Movefile   --> ' + saving_name)
            ask_saving_root.quit()
            ask_saving_root.destroy()

        if ask_path:
            ask_saving_root = tk.Tk()
            ask_saving_root.iconbitmap(mf_data_path + r'Movefile.ico')
            ask_saving_root.geometry('675x35')
            ask_saving_root.title('读取存档')
            last_edit_mode = ''
            last_edit_name = ''
            save_names = []
            if last_saving_data:
                last_edit_mode = last_saving_data[0]
                last_edit_name = last_saving_data[1]
            name_label = ttk.Label(ask_saving_root, text='     选择存档：')
            name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')
            mode_entry = ttk.Combobox(ask_saving_root, values=['清理文件(Cleanfile)', '同步文件(Syncfile)'],
                                      state='readonly')
            mode_entry.grid(row=0, column=1, pady=5, padx=5, )
            if last_edit_mode == 'sf':
                mode_entry.current(1)
            elif last_edit_mode == 'cf':
                mode_entry.current(0)
            name_entry = ttk.Combobox(ask_saving_root, values=save_names, state='readonly')
            refresh_saving()
            for save_index, name in enumerate(new_values):
                if name == last_edit_name:
                    name_entry.current(save_index)
            name_entry.grid(row=0, column=2, padx=5, pady=5, ipadx=20, sticky='W')
            del_save_button = ttk.Button(ask_saving_root, text='删除存档', command=lambda: del_saving())
            del_save_button.grid(row=0, column=3, padx=5, pady=5)
            sure_name_bottom = ttk.Button(ask_saving_root, text='读取存档', command=lambda: sure_open())
            sure_name_bottom.grid(row=0, column=4, pady=5)
            name_entry.bind('<Button-1>', lambda event: refresh_saving())
            ask_saving_root.mainloop()
        elif mode == 'cf':
            open_cf_saving(save_name)
            root.title('Movefile   --> ' + save_name)
        elif mode == 'sf':
            open_sf_saving(save_name)
            root.title('Movefile   --> ' + save_name)

    def ask_save_name():
        list_saving_data()

        def sure_save():
            savefile(mode=cf_or_sf.get(), save_name=name_entry.get())
            ask_name_window.quit()
            ask_name_window.destroy()

        mode = cf_or_sf.get()
        if mode == 'cf':
            has_error = cf_has_error()
            pri_save_names = cf_save_names
        elif mode == 'sf':
            has_error = sf_has_error()
            pri_save_names = sf_save_names
        else:
            has_error = True
            pri_save_names = []
        if not has_error:
            ask_name_window = tk.Tk()
            ask_name_window.iconbitmap(mf_data_path + r'Movefile.ico')
            ask_name_window.geometry('400x35')
            ask_name_window.title('设置配置存档名称')
            last_edit_name = 'New_Setting'
            if last_saving_data:
                if last_saving_data[0] == mode:
                    last_edit_name = last_saving_data[1]
                else:
                    last_edit_name = last_saving_data[2]
            name_label = ttk.Label(ask_name_window, text='  请输入存档的名称：')
            name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')

            name_entry = ttk.Combobox(ask_name_window, values=pri_save_names)
            name_entry.insert(0, last_edit_name)
            name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='W')
            sure_name_bottom = ttk.Button(ask_name_window, text='确定保存', command=lambda: sure_save())
            sure_name_bottom.grid(row=0, column=2, sticky='W')
            ask_name_window.mainloop()

    def cf_operate_from_root():
        old_path = cf_entry_old_path.get()  # 旧文件夹
        new_path = cf_entry_new_path.get()  # 新文件夹
        pass_file = cf_entry_keep_files.get().split(',')  # 设置跳过白名单
        pass_format = cf_entry_keep_formats.get().split(',')  # 设置跳过格式
        time_ = int(cf_entry_time.get()) * 3600  # 设置过期时间(hour)
        mode = int(cf_entry_mode.get())  # 设置判断模式
        is_move_folder = cf_is_folder_move.get()  # 设置是否移动文件夹

        cf_move_dir(old__path=old_path, new__path=new_path, pass__file=pass_file, pass__format=pass_format,
                    overdue_time=time_,
                    check__mode=mode, is__move__folder=is_move_folder)

    def sf_operate_from_root():
        if sf_place_mode.get() == 'movable':
            path1 = sf_entry_select_removable.get().split(':')[0][-1] + ':'
        else:
            path1 = sf_entry_path_1.get()
        path2 = sf_entry_path_2.get()
        mode = sf_entry_mode.get()
        area_name = None
        if len(path1) == 2:
            area_name = win32api.GetVolumeInformation(path1)[0]
        if mode == 'single':
            single_sync = True
        else:
            single_sync = False
        sync_dir(path1, path2, single_sync, area_name)

    def continue_going():
        if cf_or_sf.get() == 'cf' and not cf_has_error():
            cf_operator = threading.Thread(target=lambda: cf_operate_from_root(), daemon=True)
            cf_operator.start()
            root.withdraw()
        elif cf_or_sf.get() == 'sf' and not sf_has_error():
            sf_operator = threading.Thread(target=lambda: sf_operate_from_root(), daemon=True)
            sf_operator.start()
            root.withdraw()

    def exit_program():
        root.quit()
        root.destroy()
        ask_permit.join()
        butt_icon.join()

    # 创建按键
    bt1 = ttk.Button(root, text='保存', command=lambda: ask_save_name())
    bt1.grid(row=8, column=1, ipadx=100, pady=4, padx=10, sticky='W')
    bt2 = ttk.Button(root, text='运行当前配置', command=lambda: continue_going())
    bt2.grid(row=8, column=1, ipadx=100, pady=4, padx=10, sticky='E')
    bt2.config(state=tk.DISABLED)

    # 菜单栏
    main_menu = tk.Menu(root)
    file_menu = tk.Menu(main_menu, tearoff=False)
    file_menu.add_command(label="读取配置文件", command=lambda: read_saving(ask_path=True), accelerator="Ctrl+O")
    file_menu.add_command(label="保存", command=lambda: savefile(mode=cf_or_sf.get(), save_name=ask_save_name()),
                          accelerator="Ctrl+S")
    help_menu = tk.Menu(main_menu, tearoff=False)
    help_menu.add_command(label="关于本软件", command=help_main)
    help_menu.add_command(label="使用前注意事项", command=help_before_use)
    help_menu.add_separator()
    help_menu.add_command(label='Cleanfile', command=cf_help)
    help_menu.add_command(label="保留文件/文件格式选择", command=cf_help_keep)
    help_menu.add_command(label="过期时间设定", command=cf_help_timeset)
    help_menu.add_separator()
    help_menu.add_command(label='Syncfile', command=sf_help)
    main_menu.add_cascade(label="文件", menu=file_menu)
    main_menu.add_cascade(label="帮助", menu=help_menu)
    root.config(menu=main_menu)

    # 托盘菜单
    menu = (
        MenuItem('设置', lambda: root.deiconify(), default=True), Menu.SEPARATOR,
        MenuItem('退出', lambda: exit_program()))
    image = Image.open(mf_data_path + 'Movefile.ico')
    task_menu = pystray.Icon("icon", image, "Movefile", menu)
    # 重新定义点击关闭按钮的处理

    root.bind("<Control-o>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-O>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-s>", lambda event: ask_save_name())
    root.bind("<Control-S>", lambda event: ask_save_name())
    root.bind('<Button-1>'), lambda: sf_refresh_disk_list(none_disk=True)
    root.protocol('WM_DELETE_WINDOW', root.withdraw)

    if first_ask:
        cf_entry_old_path.insert(0, get_desktop())
        cf_entry_time.insert(0, '0')
        cf_entry_mode.set(1)
        cf_refresh_whitelist_entry()
        cf_or_sf.set('cf')
        change_active_mode('cf')
        help_main()
        help_before_use()
    elif muti_ask:
        read_saving(ask_path=False)
        cf_refresh_whitelist_entry()
        bt2.config(state=tk.NORMAL)
        if cf_or_sf.get() == '':
            cf_or_sf.set('cf')
            change_active_mode('cf')
        if startup_ask:
            root.withdraw()

    def get_movable_autorun_ids():
        sf_dat = configparser.ConfigParser()
        sf_dat.read(sf_data_path + 'Syncfile_data.ini')
        savings = sf_dat.sections()
        autorun_ids = []
        for saving in savings:
            if sf_dat.get(saving, 'place_mode') == 'movable' and sf_dat.get(saving, 'autorun') == 'True':
                autorun_ids.append([sf_dat.get(saving, 'disk_number'), saving])
        return autorun_ids

    def ask_sync_disk():
        while True:
            run_list = []
            for new_area_data in new_areas_data:
                for autorun_id in get_movable_autorun_ids():
                    if str(new_area_data[2]) == autorun_id[0] and tk.messagebox.askokcancel(title='Movefile',
                                                                                            message=f'检测到可移动磁盘{new_area_data[1]} ({new_area_data[0][:-1]})接入，'+'\n' +
                                                                                                    f'确定按配置 "{autorun_id[1]}" 进行同步?'):
                        run_list.append([new_area_data[0], new_area_data[1], autorun_id[1]])
                new_areas_data.remove(new_area_data)
            if run_list:
                sf_autorun_operation('movable', run_list)
            time.sleep(1)

    butt_icon = threading.Thread(target=task_menu.run, daemon=True)
    butt_icon.start()
    background_detect = threading.Thread(target=lambda: detect_removable_disks(), daemon=True)
    background_detect.start()
    ask_permit = threading.Thread(target=lambda: ask_sync_disk(), daemon=True)
    ask_permit.start()
    root.mainloop()


def mainprocess():
    set_data_path()
    load_icon()
    set_startup()
    asktime_plus()

    first_visit = False
    if list_saving_data() == ['', '', '']:  # 判断是否为首次访问
        first_visit = True

    cf = configparser.ConfigParser()
    sf = configparser.ConfigParser()
    mf = configparser.ConfigParser()
    cf.read(cf_data_path + r'Cleanfile_data.ini')
    sf.read(sf_data_path + r'Syncfile_data.ini')
    mf.read(mf_data_path + r"Movefile_data.ini")

    boot_time = get_boot_time()
    ask_time_today = mf.getint("General", "asktime_today")
    if first_visit:
        make_ui(first_ask=True)
    elif ask_time_today > 1:
        make_ui(muti_ask=True)
    elif boot_time <= 60 and ask_time_today == 1:
        cf_autorun_operation()
        sf_autorun_operation('local')
        make_ui(muti_ask=True, startup_ask=True)


if __name__ == '__main__':
    mainprocess()
