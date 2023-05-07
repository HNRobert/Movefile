# -*- coding: utf-8 -*-
"""
Due to the limited ability of the author,
nearly all the code is integrated in this main program.
If you have any suggestion for optimizing structure of this program,
it's welcomed to submit them to the author.

Created on Wed Dec 21 17:07:30 2022

@author: Robert He
QQ: 2567466856
GitHub address: https://github.com/HNRobert/Movefile
"""
import base64
import configparser
import hashlib
import os
import shutil
import threading
import time
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
import winreg
from datetime import datetime

import psutil
import pystray
import win32api
import win32com.client as com
import winshell
from PIL import Image
from mttkinter import mtTkinter as tk
from pystray import MenuItem, Menu
from win10toast import ToastNotifier

import Movefile_icon as icon
from ComBoPicker import Combopicker
from LT_Dic import vision


class Initialization:
    def __init__(self):
        global startup_root, first_visit, boot_time, ask_time_today
        self.set_data_path()
        startup_root = threading.Thread(target=self.check_window, daemon=True)
        startup_root.start()
        self.get_desktop()
        self.load_icon()
        self.asktime_plus()

        first_visit = False
        if list_saving_data() == ['', '', '']:  # 判断是否为首次访问
            first_visit = True

        mf = configparser.ConfigParser()
        mf.read(mf_data_path + r"Movefile_data.ini")

        boot_time = self.get_boot_time()
        ask_time_today = mf.getint("General", "asktime_today")

    @staticmethod
    def get_boot_time():
        boot_t = psutil.boot_time()
        boot_time_obj = datetime.fromtimestamp(boot_t)
        now_time = datetime.now()
        delta_time = now_time - boot_time_obj
        boot_time_s = delta_time.days * 3600 * 24 + delta_time.seconds
        return boot_time_s

    @staticmethod
    def set_data_path():
        global mf_data_path, cf_data_path, sf_data_path
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

    @staticmethod
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

        if not gencf.has_option('General', 'language'):
            import ctypes
            dll_handle = ctypes.windll.kernel32
            if hex(dll_handle.GetSystemDefaultUILanguage()) == '0x804':
                gencf.set('General', 'language', 'Chinese')
            else:
                gencf.set('General', 'language', 'English')
        if not gencf.has_option('General', 'autorun'):
            gencf.set('General', 'autorun', 'False')
        gencf.write(open(mf_data_path + r'Movefile_data.ini', "w+", encoding='ANSI'))

    @staticmethod
    def get_desktop():
        global desktop_path
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        desktop_path = winreg.QueryValueEx(key, "Desktop")[0]

    @staticmethod
    def load_icon():
        image = open(mf_data_path + r'Movefile.ico', 'wb')
        image.write(base64.b64decode(icon.Movefile_ico))
        image.close()

    @staticmethod
    def check_window():
        from LT_Dic import cr_label_text_dic
        global c_root
        mf_file = configparser.ConfigParser()
        mf_file.read(mf_data_path + 'Movefile_data.ini')
        # l_n = language_num(mf_file.get('General', 'language'))
        c_root = tk.Tk()
        c_root.geometry('420x60')
        c_root.iconbitmap(mf_data_path + r'Movefile.ico')
        c_root.title('Movefile')
        c_label = tk.Label(c_root, text=cr_label_text_dic['c_label'][1])
        c_label.grid(row=0, column=0, padx=10, pady=5)
        c_bar = ttk.Progressbar(c_root, mode='indeterminate')
        c_bar.grid(row=1, column=0, padx=10, pady=0, ipadx=150)
        c_bar.start(10)
        c_bar.mainloop()


def set_startup(state=True):
    # 将快捷方式添加到自启动目录
    # 获取用户名
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
    startup_path = os.path.join(roaming_path + r"\Microsoft\Windows\Start Menu\Programs\Startup")
    bin_path = r"Movefile " + vision + ".exe"
    shortcut_path = startup_path + "\\Movefile" + ".lnk"
    desc = "自动转移文件程序"
    icon_ = mf_data_path + r'Movefile.ico'
    gen_cf = configparser.ConfigParser()
    gen_cf.read(mf_data_path + 'Movefile_data.ini')
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
    if state:
        gen_cf.set('General', 'autorun', 'True')
        winshell.CreateShortcut(
            Path=shortcut_path,
            Target=bin_path,
            Icon=(icon_, 0),
            Description=desc)
    else:
        gen_cf.set('General', 'autorun', 'False')
    gen_cf.write(open(mf_data_path + r'Movefile_data.ini', "w+", encoding='ANSI'))


def language_num(language_name):
    if language_name == 'Chinese':
        l_num = 0
    elif language_name == 'English':
        l_num = 1
    else:
        l_num = 2
    return l_num


def filehash(filepath):
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()


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
            last_saving_data = ['cf', cf_save_name, '']
            if sf_save_names:
                last_saving_data[2] = sf_save_names[0]
            break
    else:
        for sf_save_name in sf_save_names:
            if sf_file.get(sf_save_name, '_last_edit_') == 'True':
                last_saving_data = ['sf', sf_save_name, '']
                if cf_save_names:
                    last_saving_data[2] = cf_save_names[0]
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
            right_path = False
            if os.path.exists(old_path_) and os.path.exists(new_path_) or new_path_ == '':
                right_path = True
            right_option = False
            if (move_folder == 'True' or move_folder == 'False') and (autorun_ == 'True' or autorun_ == 'False'):
                right_option = True
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


def detect_removable_disks_thread():
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


def scan_items(folder_path):  # 扫描路径下所有文件夹
    def scan_folders_in(f_path):  # 扫描目录下所有的文件夹，并返回路径列表
        surf_items = os.listdir(f_path)
        folders = [f_path]
        for item in surf_items:
            item_path = f_path + '\\' + item
            if os.path.isdir(item_path):
                folders.extend(scan_folders_in(item_path))  # 继续遍历文件夹内文件夹，直到记下全部文件夹路径
        folders = sorted(set(folders))  # 排序 + 排除重复项
        return folders

    file_store = []
    folder_store = scan_folders_in(folder_path)
    for folder in folder_store:  # 遍历所有文件夹
        files = [folder + '\\' + dI for dI in os.listdir(folder) if os.path.isfile(os.path.join(folder, dI))]
        # 如上只生成本文件夹内 文件的路径
        file_store.extend(files)  # 存储上面文件路径
    for i in range(len(file_store)):
        file_store[i] = file_store[i][len(folder_path)::]  # 返回相对位置
    result = [folder_store, file_store]
    return result


def cf_move_dir(old__path, new__path, pass__file, pass__format, overdue_time, check__mode, is__move__folder):
    from LT_Dic import cf_label_text_dic as cfdic
    mf_file = configparser.ConfigParser()
    mf_file.read(mf_data_path + 'Movefile_data.ini')
    lang_num = language_num(mf_file.get('General', 'language'))

    def cf_show_notice(old_path, new_path, movename, errorname):
        new_folder = new_path.split('\\')[-1]
        old_folder = old_path.split('\\')[-1]
        if len(movename) > 0:
            notice_title = cfdic['title_p1'][lang_num] + old_folder + cfdic['title_p2_1'][lang_num] + new_folder + ':'
            if new_path == '':
                notice_title = cfdic['title_p1'][lang_num] + old_folder + cfdic['title_p2_2'][lang_num]
            toaster.show_toast(notice_title, movename,
                               icon_path=mf_data_path + r'Movefile.ico',
                               duration=10,
                               threaded=False)
        else:
            notice_title = old_folder + cfdic['cltitle'][lang_num]
            notice_content = cfdic['clcontent'][lang_num]
            toaster.show_toast(notice_title, notice_content,
                               icon_path=mf_data_path + r'Movefile.ico',
                               duration=10,
                               threaded=False)
        if len(errorname) > 0:
            notice_title = cfdic['errtitle'][lang_num]
            notice_content = errorname[:-1] + '\n' + cfdic['errcontent'][lang_num]
            toaster.show_toast(notice_title, notice_content,
                               icon_path=mf_data_path + r'Movefile.ico',
                               duration=10,
                               threaded=False)

    def del_item(path):  # 递归删除文件夹或单个文件, 代替shutil.rmtree和os.remove  (shutil.rmtree会莫名报错)
        error_files = ''
        moved_files = ''
        if os.path.isdir(path):
            del_data = scan_items(path)  # 扫描文件夹里所有子文件夹和文件
            for dfile in del_data[1]:
                try:
                    os.remove(path + dfile)
                except:
                    error_files += dfile + ',  '  # 这样还可以返回文件夹里无法移动的单个文件
            for dfolder in del_data[0][::-1]:
                try:
                    os.rmdir(dfolder)
                except:
                    pass
            if not os.path.exists(path):
                moved_files += path.split('\\')[-1] + ',  '
        else:
            try:
                os.remove(path)  # 若是文件直接处理
            except:
                error_files += path.split('\\')[-1] + ',  '
            else:
                moved_files += path.split('\\')[-1] + ',  '
        return [moved_files, error_files]

    """
    def ask_operation(file1_path, file2_path):  # planning
        text = f'''{cfdic['cptitle'][lang_num]}
{file1_path}:
{cfdic['cpsize'][lang_num]} {os.stat(file1_path).st_size}
{cfdic['cpctime'][lang_num]} {os.stat(file1_path).st_ctime}
{cfdic['cpetime'][lang_num]} {os.stat(file1_path).st_mtime}

{file2_path}:
{cfdic['cpsize'][lang_num]} {os.stat(file2_path).st_size}
{cfdic['cpctime'][lang_num]} {os.stat(file2_path).st_ctime}
{cfdic['cpetime'][lang_num]} {os.stat(file2_path).st_mtime}
'''
        return text
    """

    cf_movename = ''
    cf_errorname = ''
    items = os.listdir(old__path)  # 获取文件夹下所有文件和文件夹
    now = int(time.time())  # 当前时间
    for item in items:
        item_path = old__path + "\\" + item
        is_folder = os.path.isdir(item_path)
        if '.' + item.split('.')[-1] in pass__format and not is_folder or item in pass__file:
            continue
        if item == 'Movefile ' + vision + '.exe' or item == new__path.split('\\')[-1]:
            continue
        if check__mode == 1:
            last = int(os.stat(item_path).st_mtime)  # 最后一次修改的时间 (Option 1)
        elif check__mode == 2:
            last = int(os.stat(item_path).st_atime)  # 最后一次访问的时间 (Option 2)
        else:
            raise
        if (not is_folder or is_folder and is__move__folder) and (now - last >= overdue_time):  # 判断移动条件
            # attitude = False
            if os.path.exists(new__path + '\\' + item):
                del_item(new__path + '\\' + item)
                # attitude = ask_operation(item_path, new__path + '\\' + item)  # 重名文件判断
            if new__path != '':  # 如果 new path 有内容就移动到 new path, 否则删除
                try:
                    shutil.move(item_path, new__path)
                except:
                    cf_errorname += (item + ',  ')
                else:
                    cf_movename += (item + ',  ')
            else:
                result = del_item(item_path)
                cf_movename += result[0]
                cf_errorname += result[1]

    cf_show_notice(old__path, new__path, cf_movename, cf_errorname)


def cf_autorun_operation():
    cf_store_path = cf_data_path + r'Cleanfile_data.ini'
    cf_file = configparser.ConfigParser()
    cf_file.read(cf_store_path)

    autorun_savings = []
    for cf_name in cf_save_names:
        if cf_file.get(cf_name, 'autorun') == 'True':
            autorun_savings.append(cf_name)

    for save_name in autorun_savings:
        cf_move_dir(old__path=cf_file.get(save_name, 'old_path'),
                    new__path=cf_file.get(save_name, 'new_path'),
                    pass__file=cf_file.get(save_name, 'pass_filename').split(','),
                    pass__format=cf_file.get(save_name, 'pass_format').split(','),
                    overdue_time=cf_file.getint(save_name, 'set_hour') * 3600,
                    check__mode=cf_file.getint(save_name, 'mode'),
                    is__move__folder=cf_file.get(save_name, 'move_folder'))


def sf_ask_operation():
    pass  # planning


def sf_creat_folder(target_path):
    target = target_path.split('\\')[:-1]
    try_des = ''
    for fold in target:
        try_des += fold + '\\'
        if not os.path.exists(try_des):
            os.mkdir(try_des)


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


def sf_sync_dir(path1, path2, single_sync, language_number, area_name=None, pass_item_rpath='', pass_folder_paths=''):
    from LT_Dic import sf_label_text_dic

    def sf_show_notice(path_1, path_2, sf_errorname):
        toaster.show_toast('Sync Successfully',
                           'The Files in "' + path_1 + '" and "' + path_2 + '" are Synchronized',
                           icon_path=mf_data_path + r'Movefile.ico',
                           duration=10,
                           threaded=False)
        if len(sf_errorname) > 0:
            toaster.show_toast("Couldn't sync files",
                               sf_errorname + sf_label_text_dic['can_not_move_notice'][language_number],
                               icon_path=mf_data_path + r'Movefile.ico',
                               duration=10,
                               threaded=False)

    def show_running():
        show_running_bar.start(10)

    def get_task():
        all_files_1 = scan_items(path1)[1]
        all_files_2 = scan_items(path2)[1]
        sync_tasks = []
        pass_folder_rpaths = []
        task_number = 0
        for pass_folder in pass_folder_paths.split(','):
            if pass_folder[:len(path1)] == path1:
                pass_folder_rpaths.append(path1.split('\\')[-1] + pass_folder[len(path1)::])
            elif pass_folder != '':
                pass_folder_rpaths.append(path2.split('\\')[-1] + pass_folder[len(path2)::])
        for file1 in all_files_1:
            filename = file1.split('\\')[-1]
            file1_path = path1 + file1
            for file2 in all_files_2:
                file2_path = path2 + file2
                match_possibility = sf_match_possibility(path1, path2, file1, file2)
                if match_possibility > 50:
                    new_file, old_file = file1, file2
                    new_file_path, old_file_path = file1_path, file2_path
                    new_file_rpath = path1.split('\\')[-1] + file1
                    old_file_rpath = path2.split('\\')[-1] + file2
                    if int(os.stat(new_file_path).st_mtime) < int(os.stat(old_file_path).st_mtime):
                        if single_sync:
                            break
                        old_file, new_file = new_file, old_file
                        new_file_path, old_file_path = old_file_path, new_file_path
                        new_file_rpath, old_file_rpath = old_file_path, new_file_rpath
                    if any(pfolder == old_file_rpath[:len(pfolder)] for pfolder in pass_folder_rpaths) and pass_folder_rpaths != []\
                            or any(old_file == pfile[-len(old_file):] for pfile in pass_item_rpath.split(',')) and pass_item_rpath != []\
                            or filehash(new_file_path) == filehash(old_file_path):
                        break
                    task_number += 1
                    main_progress_label['text'] = sf_label_text_dic['main_progress_label'][language_number] + filename
                    sync_tasks.append([new_file_path, old_file_path, False])
                    break
                elif match_possibility == 50:
                    sf_ask_operation()
            else:
                newfile1_rpath = path2.split('\\')[-1] + file1
                if any(pfolder == newfile1_rpath[:len(pfolder)] for pfolder in pass_folder_rpaths) and pass_folder_rpaths != []:
                    continue
                task_number += 1
                main_progress_label['text'] = sf_label_text_dic['main_progress_label'][language_number] + filename
                sync_bar.update_idletasks()
                sync_tasks.append([file1_path, path2 + file1, True])
        if not single_sync:
            for file2 in all_files_2:
                filename = file2.split('\\')[-1]
                file2_path = path2 + file2
                newfile2_rpath = path1.split('\\')[-1] + file2
                if file2 not in all_files_1:
                    if any(pfolder == newfile2_rpath[:len(pfolder)] for pfolder in pass_folder_rpaths) and pass_folder_rpaths != []:
                        continue
                    task_number += 1
                    main_progress_label['text'] = sf_label_text_dic['main_progress_label'][language_number] + filename
                    sync_bar.update_idletasks()
                    sync_tasks.append([file2_path, path1 + file2, True])
        return sync_tasks

    def run_sync_tasks():
        sf_errorname = ''
        main_progress_bar['value'] = 0
        sync_bar.update_idletasks()
        tasks = get_task()
        main_progress_bar['maximum'] = len(tasks)
        main_progress_label[
            'text'] = f'{sf_label_text_dic["main_progress_label1"][language_number][0]}{str(main_progress_bar["value"])}/{str(len(tasks))}  {sf_label_text_dic["main_progress_label1"][language_number][1]}'
        for task in tasks:
            current_file_label['text'] = sf_label_text_dic["current_file_label1"][language_number] + \
                                         task[0].split('\\')[-1]
            if task[2]:
                sf_creat_folder(task[1])
            try:
                shutil.copyfile(task[0], task[1])
            except:
                sf_errorname += task[0] + ' , '
            main_progress_bar['value'] += 1
            main_progress_label[
                'text'] = f'{sf_label_text_dic["main_progress_label1"][language_number][0]}{str(main_progress_bar["value"])}/{str(len(tasks))}  {sf_label_text_dic["main_progress_label1"][language_number][1]}'
            sync_bar.update_idletasks()
        sync_bar.withdraw()
        path_name_1 = path1.split('\\')[-1]
        if area_name:
            path_name_1 = area_name
        try:
            sf_show_notice(path_name_1, path2.split('\\')[-1], sf_errorname)
        except:
            pass
        finally:
            sync_bar.withdraw()
            roll_bar.join()

    def sync_bar_on_exit():
        if tkinter.messagebox.askyesno(title='Syncfile', message='''文件正在同步中，
确定中断同步进程并退出?'''):
            sync_bar.withdraw()
            run_tasks.join()
            roll_bar.join()

    global sync_bar
    sync_bar = tk.Tk()
    sync_bar.title('Movefile  -Syncfile Progress')
    sync_bar.geometry('420x115')
    main_progress_label = ttk.Label(sync_bar, text=sf_label_text_dic["main_progress_label2"][language_number])
    main_progress_label.grid(row=0, column=0, padx=10, pady=5, sticky='SW')
    main_progress_bar = ttk.Progressbar(sync_bar)
    main_progress_bar.grid(row=1, column=0, padx=10, pady=0, ipadx=150, sticky='W')
    current_file_label = ttk.Label(sync_bar, text=sf_label_text_dic["current_file_label"][language_number])
    current_file_label.grid(row=2, column=0, padx=10, pady=5, sticky='SW')
    show_running_bar = ttk.Progressbar(sync_bar, mode='indeterminate')
    show_running_bar.grid(row=3, column=0, padx=10, pady=0, ipadx=150, sticky='W')
    sync_bar.protocol('WM_DELETE_WINDOW', lambda: sync_bar_on_exit())
    roll_bar = threading.Thread(target=show_running, daemon=True)
    roll_bar.start()
    run_tasks = threading.Thread(target=run_sync_tasks, daemon=True)
    run_tasks.start()
    sync_bar.mainloop()


def sf_autorun_operation(place, saving_datas=None):
    sf_file = configparser.ConfigParser()
    sf_file.read(sf_data_path + 'Syncfile_data.ini')
    mf_file = configparser.ConfigParser()
    mf_file.read(mf_data_path + 'Movefile_data.ini')

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
            lockfolder = sf_file.get(saving_data[2], 'lock_folder')
            lockfile = sf_file.get(saving_data[2], 'lock_file')
            single_sync = True
            if sf_file.get(saving_data[2], 'mode') == 'double':
                single_sync = False
            sf_sync_dir(path1, path2, single_sync, language_num(mf_file.get('General', 'language')), saving_data[1], lockfile, lockfolder)

    def autorun_local_sf(data_name):
        for saving_data in data_name:
            path1 = sf_file.get(saving_data, 'path_1')
            path2 = sf_file.get(saving_data, 'path_2')
            lockfolder = sf_file.get(saving_data, 'lock_folder')
            lockfile = sf_file.get(saving_data, 'lock_file')
            single_sync = True
            if sf_file.get(saving_data, 'mode') == 'double':
                single_sync = False
            sf_sync_dir(path1, path2, single_sync, language_number=language_num(mf_file.get('General', 'language')), pass_folder_paths=lockfolder, pass_item_rpath=lockfile)

    if place == 'movable':
        autorun_movable_sf(saving_datas)
    elif place == 'local':
        autorun_local_sf(get_sf_startup_savings())


def make_ui(muti_ask=False, first_ask=False, startup_ask=False):
    from LT_Dic import r_label_text_dic
    cf_data = configparser.ConfigParser()
    sf_data = configparser.ConfigParser()
    general_data = configparser.ConfigParser()
    general_data.read(mf_data_path + r'Movefile_data.ini')
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
            sf_entry_select_removable['values'] = [sf_no_disk_text.get()]
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

    def choose_lockitems(mode):
        if mode == 'lockfolder':
            folder_path_ = tkinter.filedialog.askdirectory()
            if folder_path_ != '':
                sf_entry_lock_folder.values.append(folder_path_.replace('/', '\\'))
        elif mode == 'lockfile':
            file_path_ = tkinter.filedialog.askopenfilenames()
            if file_path_ != '':
                for file in file_path_:
                    sf_entry_lock_file.values.append(file.replace('/', '\\'))

    def set_language(lang_number):
        label_choose_state_text.set(r_label_text_dic['label_choose_state'][lang_number])
        option_is_cleanfile_text.set(r_label_text_dic['option_is_cleanfile'][lang_number])
        option_is_syncfile_text.set(r_label_text_dic['option_is_syncfile'][lang_number])
        cf_label_old_path_text.set(r_label_text_dic['cf_label_old_path'][lang_number])
        cf_browse_old_path_button_text.set(r_label_text_dic['cf_browse_old_path_button'][lang_number])
        cf_browse_new_path_button_text.set(r_label_text_dic['cf_browse_new_path_button'][lang_number])
        cf_label_new_path_text.set(r_label_text_dic['cf_label_new_path'][lang_number])
        cf_label_move_options_text.set(r_label_text_dic['cf_label_move_options'][lang_number])
        cf_option_mode_1_text.set(r_label_text_dic['cf_option_mode_1'][lang_number])
        cf_option_mode_2_text.set(r_label_text_dic['cf_option_mode_2'][lang_number])
        cf_option_folder_move_text.set(r_label_text_dic['cf_option_folder_move'][lang_number])
        cf_label_keep_files_text.set(r_label_text_dic['cf_label_keep_files'][lang_number])
        cf_label_keep_formats_text.set(r_label_text_dic['cf_label_keep_formats'][lang_number])
        cf_label_time_text.set(r_label_text_dic['cf_label_time'][lang_number])
        cf_label_start_options_text.set(r_label_text_dic['cf_label_start_options'][lang_number])
        cf_option_is_auto_text.set(r_label_text_dic['cf_option_is_auto'][lang_number])
        sf_label_place_mode_text.set(r_label_text_dic['sf_label_place_mode'][lang_number])
        sf_option_mode_usb_text.set(r_label_text_dic['sf_option_mode_usb'][lang_number])
        sf_option_mode_local_text.set(r_label_text_dic['sf_option_mode_local'][lang_number])
        sf_label_path_1_text.set(r_label_text_dic['sf_label_path_1'][lang_number][0])
        sf_label_path_2_text.set(r_label_text_dic['sf_label_path_2'][lang_number][0])
        sf_browse_path_1_button_text.set(r_label_text_dic['sf_browse_path_1_button'][lang_number])
        sf_browse_path_2_button_text.set(r_label_text_dic['sf_browse_path_2_button'][lang_number])
        sf_no_disk_text.set(r_label_text_dic['sf_no_disk'][lang_number])
        sf_label_mode_text.set(r_label_text_dic['sf_label_mode'][lang_number])
        sf_option_mode_double_text.set(r_label_text_dic['sf_option_mode_double'][lang_number])
        sf_option_mode_single_text.set(r_label_text_dic['sf_option_mode_single'][lang_number])
        sf_label_lock_folder_text.set(r_label_text_dic['sf_label_lock_folder'][lang_number])
        sf_browse_lockfolder_button_text.set(r_label_text_dic['sf_browse_lockfolder_button'][lang_number])
        sf_label_lock_file_text.set(r_label_text_dic['sf_label_lock_file'][lang_number])
        sf_browse_lockfile_button_text.set(r_label_text_dic['sf_browse_lockfile_button'][lang_number])
        sf_label_autorun_text.set(r_label_text_dic['sf_label_autorun'][lang_number])
        sf_option_autorun_text.set(r_label_text_dic['sf_option_autorun'][lang_number])
        save_button_text.set(r_label_text_dic['save_button'][lang_number])
        continue_button_text.set(r_label_text_dic['continue_button'][lang_number])

        file_menu_text.set(r_label_text_dic['file_menu'][lang_number])
        readfile_menu_text.set(r_label_text_dic['readfile_menu'][lang_number])
        savefile_menu_text.set(r_label_text_dic['savefile_menu'][lang_number])
        option_menu_text.set(r_label_text_dic['option_menu'][lang_number])
        autorun_menu_text.set(r_label_text_dic['autorun_menu'][lang_number])
        language_menu_text.set(r_label_text_dic['language_menu'][lang_number])
        help_menu_text.set(r_label_text_dic['help_menu'][lang_number])
        about_menu_text.set(r_label_text_dic['about_menu'][lang_number])
        precautions_menu_text.set(r_label_text_dic['precautions_menu'][lang_number])
        cf_keep_menu_text.set(r_label_text_dic['cf_keep_menu'][lang_number])
        cf_expire_menu_text.set(r_label_text_dic['cf_expire_menu'][lang_number])
        sf_removable_menu_text.set(r_label_text_dic['sf_removable_menu'][lang_number])
        sf_lock_menu_text.set(r_label_text_dic['sf_lock_menu'][lang_number])

        taskbar_setting_text.set(r_label_text_dic['taskbar_setting'][lang_number])
        taskbar_exit_text.set(r_label_text_dic['taskbar_exit'][lang_number])

    class Place:
        def __init__(self, mode=None, sf_place=None):
            label_choose_state.grid(row=0, column=0, pady=5, sticky='E')
            blank.grid(row=0, column=1, padx=321, pady=5, sticky='W')
            option_is_cleanfile.grid(row=0, column=1, padx=10, pady=5, sticky='W')
            option_is_syncfile.grid(row=0, column=1, padx=100, pady=5, sticky='W')
            if mode == 'cf':
                self.cf_state()
            elif mode == 'sf':
                self.sf_state(sf_place)
            self.judge_button_pix()

        @staticmethod
        def sf_change_place_mode(mode):
            if mode == 'movable':
                sf_label_path_1_text.set(r_label_text_dic['sf_label_path_1'][lang_num][0])
                sf_label_path_2_text.set(r_label_text_dic['sf_label_path_2'][lang_num][0])
                sf_option_autorun_text.set(r_label_text_dic['sf_option_autorun'][lang_num][0])
                sf_browse_path_1_button.grid_forget()
                sf_entry_select_removable.grid(row=3, column=1, padx=10, pady=5, ipadx=231, sticky='W')
            else:
                sf_label_path_1_text.set(r_label_text_dic['sf_label_path_1'][lang_num][1])
                sf_label_path_2_text.set(r_label_text_dic['sf_label_path_2'][lang_num][1])
                sf_option_autorun_text.set(r_label_text_dic['sf_option_autorun'][lang_num][1])
                sf_browse_path_1_button.grid(row=3, column=1, ipadx=3, sticky='E', padx=10)
                sf_entry_select_removable.grid_forget()

        @staticmethod
        def judge_button_pix():
            if lang_num == 0:
                save_button.grid(row=8, column=1, ipadx=100, pady=4, padx=10, sticky='W')
                continue_button.grid(row=8, column=1, ipadx=100, pady=4, padx=10, sticky='E')
                cf_option_mode_2.grid(row=3, column=1, padx=180, ipadx=0, sticky='E')
            elif lang_num == 1:
                save_button.grid(row=8, column=1, ipadx=95, pady=4, padx=10, sticky='W')
                continue_button.grid(row=8, column=1, ipadx=70, pady=4, padx=10, sticky='E')
                cf_option_mode_2.grid(row=3, column=1, padx=210, ipadx=0, sticky='W')

        @staticmethod
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
            sf_entry_frame_lock_folder.grid_forget()
            sf_entry_lock_folder.grid_forget()
            sf_browse_lockfolder_button.grid_forget()
            sf_label_lock_file.grid_forget()
            sf_entry_frame_lock_file.grid_forget()
            sf_entry_lock_file.grid_forget()
            sf_browse_lockfile_button.grid_forget()
            sf_label_autorun.grid_forget()
            sf_option_autorun.grid_forget()

            cf_entry_old_path.grid(row=1, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            cf_browse_old_path_button.grid(row=1, column=1, ipadx=3, sticky='E', padx=10)
            cf_entry_new_path.grid(row=2, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            cf_browse_new_path_button.grid(row=2, column=1, ipadx=3, sticky='E', padx=10)
            cf_option_mode_1.grid(row=3, column=1, padx=10, ipadx=0, sticky='W')
            cf_option_mode_2.grid(row=3, column=1, padx=180, ipadx=0, sticky='W')
            cf_option_folder_move.grid(row=3, column=1, padx=10, sticky='E')
            cf_entry_keep_files.grid(row=4, column=1, padx=10, pady=5, ipadx=240, sticky='W')
            cf_entry_keep_formats.grid(row=5, column=1, padx=10, pady=5, ipadx=240, sticky='W')
            cf_entry_frame_keep_files.grid(row=4, column=1, sticky='W')
            cf_entry_frame_keep_formats.grid(row=5, column=1, sticky='W')
            cf_entry_time.grid(row=6, column=1, padx=10, pady=5, ipadx=240, sticky='W')
            cf_option_is_auto.grid(row=7, column=1, padx=10, sticky='NW')
            cf_label_old_path.grid(row=1, column=0, pady=5, sticky='E')
            cf_label_new_path.grid(row=2, column=0, pady=5, sticky='E')
            cf_label_move_options.grid(row=3, column=0, pady=5, sticky='E')
            cf_label_keep_files.grid(row=4, column=0, pady=5, sticky='E')
            cf_label_keep_formats.grid(row=5, column=0, sticky='E')
            cf_label_time.grid(row=6, column=0, sticky='E')
            cf_label_start_options.grid(row=7, column=0, sticky='E')

        @staticmethod
        def sf_state(placemode=None):
            cf_entry_old_path.grid_forget()
            cf_browse_old_path_button.grid_forget()
            cf_entry_new_path.grid_forget()
            cf_browse_new_path_button.grid_forget()
            cf_option_mode_1.grid_forget()
            cf_option_mode_2.grid_forget()
            cf_option_folder_move.grid_forget()
            cf_entry_keep_files.grid_forget()
            cf_entry_keep_formats.grid_forget()
            cf_entry_frame_keep_files.grid_forget()
            cf_entry_frame_keep_formats.grid_forget()
            cf_entry_time.grid_forget()
            cf_option_is_auto.grid_forget()
            cf_label_old_path.grid_forget()
            cf_label_new_path.grid_forget()
            cf_label_move_options.grid_forget()
            cf_label_keep_files.grid_forget()
            cf_label_keep_formats.grid_forget()
            cf_label_time.grid_forget()
            cf_label_start_options.grid_forget()

            if placemode:
                Place.sf_change_place_mode(placemode)
            elif sf_place_mode.get() == 'movable':
                Place.sf_change_place_mode('movable')
            else:
                Place.sf_change_place_mode('local')

            sf_label_place_mode.grid(row=1, column=0, pady=5, sticky='E')
            sf_option_mode_usb.grid(row=1, column=1, padx=10, pady=5, sticky='W')
            sf_option_mode_local.grid(row=1, column=1, padx=200, sticky='W')
            sf_option_mode_double.grid(row=2, column=1, padx=10, ipadx=0, sticky='W')
            sf_option_mode_single.grid(row=2, column=1, padx=200, ipadx=0, sticky='W')
            sf_label_mode.grid(row=2, column=0, pady=5, sticky='E')
            sf_label_path_1.grid(row=3, column=0, pady=5, sticky='E')
            sf_label_path_2.grid(row=4, column=0, pady=5, sticky='E')
            sf_entry_path_1.grid(row=3, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_entry_path_2.grid(row=4, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_browse_path_2_button.grid(row=4, column=1, ipadx=3, sticky='E', padx=10)
            sf_label_lock_folder.grid(row=5, column=0, pady=5, sticky='E')
            sf_entry_frame_lock_folder.grid(row=5, column=1, sticky='W')
            sf_entry_lock_folder.grid(row=5, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_browse_lockfolder_button.grid(row=5, column=1, padx=10, sticky='E', ipadx=3)
            sf_label_lock_file.grid(row=6, column=0, pady=5, sticky='E')
            sf_entry_frame_lock_file.grid(row=6, column=1, sticky='W')
            sf_entry_lock_file.grid(row=6, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_browse_lockfile_button.grid(row=6, column=1, padx=10, sticky='E', ipadx=3)
            sf_label_autorun.grid(row=7, column=0, sticky='E')
            sf_option_autorun.grid(row=7, column=1, padx=10, sticky='W')

    try:
        c_root.quit()
        c_root.destroy()
        startup_root.join()
    except:
        pass

    root = tk.Tk()
    root.iconbitmap(mf_data_path + r'Movefile.ico')
    root.title('Movefile Setting')
    root.geometry("800x287")
    root.resizable(False, False)
    root.attributes('-topmost', True)
    root.attributes('-topmost', False)
    root.update_idletasks()

    oldpath = tk.StringVar()
    newpath = tk.StringVar()
    path_1 = tk.StringVar()
    path_2 = tk.StringVar()
    label_choose_state_text = tk.StringVar()
    option_is_cleanfile_text = tk.StringVar()
    option_is_syncfile_text = tk.StringVar()
    cf_label_old_path_text = tk.StringVar()
    cf_browse_old_path_button_text = tk.StringVar()
    cf_browse_new_path_button_text = tk.StringVar()
    cf_label_new_path_text = tk.StringVar()
    cf_label_move_options_text = tk.StringVar()
    cf_option_mode_1_text = tk.StringVar()
    cf_option_mode_2_text = tk.StringVar()
    cf_option_folder_move_text = tk.StringVar()
    cf_label_keep_files_text = tk.StringVar()
    cf_label_keep_formats_text = tk.StringVar()
    cf_label_time_text = tk.StringVar()
    cf_label_start_options_text = tk.StringVar()
    cf_option_is_auto_text = tk.StringVar()
    sf_label_place_mode_text = tk.StringVar()
    sf_option_mode_usb_text = tk.StringVar()
    sf_option_mode_local_text = tk.StringVar()
    sf_label_path_1_text = tk.StringVar()
    sf_label_path_2_text = tk.StringVar()
    sf_browse_path_1_button_text = tk.StringVar()
    sf_browse_path_2_button_text = tk.StringVar()
    sf_no_disk_text = tk.StringVar()
    sf_label_mode_text = tk.StringVar()
    sf_option_mode_double_text = tk.StringVar()
    sf_option_mode_single_text = tk.StringVar()
    sf_label_lock_folder_text = tk.StringVar()
    sf_browse_lockfolder_button_text = tk.StringVar()
    sf_browse_lockfile_button_text = tk.StringVar()
    sf_label_lock_file_text = tk.StringVar()
    sf_label_autorun_text = tk.StringVar()
    sf_option_autorun_text = tk.StringVar()

    save_button_text = tk.StringVar()
    continue_button_text = tk.StringVar()
    file_menu_text = tk.StringVar()
    readfile_menu_text = tk.StringVar()
    savefile_menu_text = tk.StringVar()
    option_menu_text = tk.StringVar()
    autorun_menu_text = tk.StringVar()
    language_menu_text = tk.StringVar()
    help_menu_text = tk.StringVar()
    about_menu_text = tk.StringVar()
    precautions_menu_text = tk.StringVar()
    cf_keep_menu_text = tk.StringVar()
    cf_expire_menu_text = tk.StringVar()
    sf_removable_menu_text = tk.StringVar()
    sf_lock_menu_text = tk.StringVar()
    taskbar_setting_text = tk.StringVar()
    taskbar_exit_text = tk.StringVar()

    root_language = tk.StringVar()
    root_language.set(general_data.get('General', 'language'))
    lang_num = language_num(root_language.get())
    set_language(lang_num)

    label_choose_state = ttk.Label(root, text=label_choose_state_text, textvariable=label_choose_state_text)
    cf_or_sf = tk.StringVar()
    option_is_cleanfile = ttk.Radiobutton(root, textvariable=option_is_cleanfile_text, variable=cf_or_sf,
                                          value='cf',
                                          command=lambda: Place(cf_or_sf.get()))
    option_is_syncfile = ttk.Radiobutton(root, textvariable=option_is_syncfile_text, variable=cf_or_sf,
                                         value='sf',
                                         command=lambda: Place(cf_or_sf.get()))

    blank = ttk.Label(root, text='')

    cf_label_old_path = ttk.Label(root, textvariable=cf_label_old_path_text)
    cf_entry_old_path = ttk.Entry(root, textvariable=oldpath)
    cf_browse_old_path_button = ttk.Button(root, textvariable=cf_browse_old_path_button_text,
                                           command=lambda: select_path(place='old',
                                                                       ori_content=cf_entry_old_path.get()))

    cf_label_new_path = ttk.Label(root, textvariable=cf_label_new_path_text)
    cf_entry_new_path = ttk.Entry(root, textvariable=newpath)
    cf_browse_new_path_button = ttk.Button(root, textvariable=cf_browse_new_path_button_text,
                                           command=lambda: select_path(place='new',
                                                                       ori_content=cf_entry_new_path.get()))

    cf_label_move_options = ttk.Label(root, textvariable=cf_label_move_options_text)
    cf_entry_mode = tk.IntVar()
    cf_option_mode_1 = ttk.Radiobutton(root, textvariable=cf_option_mode_1_text, variable=cf_entry_mode,
                                       value=1)
    cf_option_mode_2 = ttk.Radiobutton(root, textvariable=cf_option_mode_2_text, variable=cf_entry_mode,
                                       value=2)
    cf_is_folder_move = tk.BooleanVar()
    cf_option_folder_move = ttk.Checkbutton(root, textvariable=cf_option_folder_move_text,
                                            variable=cf_is_folder_move)

    cf_entry_frame_keep_files = tk.Frame(root)
    cf_label_keep_files = ttk.Label(root, textvariable=cf_label_keep_files_text)
    cf_entry_keep_files = Combopicker(master=cf_entry_frame_keep_files, values='', frameheight=120)
    cf_entry_keep_files.bind('<Button-1>', lambda event: cf_refresh_whitelist_entry())

    cf_entry_frame_keep_formats = tk.Frame(root)
    cf_label_keep_formats = ttk.Label(root, textvariable=cf_label_keep_formats_text)
    cf_entry_keep_formats = Combopicker(master=cf_entry_frame_keep_formats, values='', frameheight=90)
    cf_entry_keep_formats.bind('<Button-1>', lambda event: cf_refresh_whitelist_entry())

    cf_label_time = ttk.Label(root, textvariable=cf_label_time_text)
    cf_entry_time = ttk.Entry(root)

    cf_label_start_options = ttk.Label(root, textvariable=cf_label_start_options_text)
    cf_is_autorun = tk.BooleanVar()
    cf_option_is_auto = ttk.Checkbutton(root, textvariable=cf_option_is_auto_text, variable=cf_is_autorun)

    sf_label_place_mode = ttk.Label(root, textvariable=sf_label_place_mode_text)
    sf_place_mode = tk.StringVar()
    sf_option_mode_usb = ttk.Radiobutton(root, textvariable=sf_option_mode_usb_text,
                                         variable=sf_place_mode,
                                         value='movable',
                                         command=lambda: Place('sf', sf_place=sf_place_mode.get()))
    sf_option_mode_local = ttk.Radiobutton(root, textvariable=sf_option_mode_local_text,
                                           variable=sf_place_mode,
                                           value='local',
                                           command=lambda: Place('sf', sf_place=sf_place_mode.get()))
    sf_place_mode.set('movable')

    sf_label_path_1 = ttk.Label(root, textvariable=sf_label_path_1_text)
    sf_entry_path_1 = ttk.Entry(root, textvariable=path_1)
    sf_browse_path_1_button = ttk.Button(root, textvariable=sf_browse_path_1_button_text,
                                         command=lambda: select_path(place='1', ori_content=sf_entry_path_1.get()))

    sf_entry_select_removable = ttk.Combobox(root, values=scan_removable_disks(), state='readonly')
    sf_entry_select_removable.bind('<Button-1>', lambda event: sf_refresh_disk_list())

    sf_label_path_2 = ttk.Label(root, textvariable=sf_label_path_2_text)
    sf_entry_path_2 = ttk.Entry(root, textvariable=path_2)
    sf_browse_path_2_button = ttk.Button(root, textvariable=sf_browse_path_2_button_text,
                                         command=lambda: select_path(place='2', ori_content=sf_entry_path_2.get()))

    sf_label_mode = ttk.Label(root, textvariable=sf_label_mode_text)
    sf_entry_mode = tk.StringVar()
    sf_option_mode_double = ttk.Radiobutton(root, textvariable=sf_option_mode_double_text,
                                            variable=sf_entry_mode,
                                            value='double')
    sf_option_mode_single = ttk.Radiobutton(root, textvariable=sf_option_mode_single_text,
                                            variable=sf_entry_mode,
                                            value='single')

    sf_label_lock_folder = ttk.Label(root, textvariable=sf_label_lock_folder_text)
    sf_entry_frame_lock_folder = tk.Frame(root)
    sf_entry_lock_folder = Combopicker(master=sf_entry_frame_lock_folder, values=['全选'], frameheight=90)
    sf_browse_lockfolder_button = ttk.Button(root, textvariable=sf_browse_lockfolder_button_text,
                                             command=lambda: choose_lockitems('lockfolder'))

    sf_label_lock_file = ttk.Label(root, textvariable=sf_label_lock_file_text)
    sf_entry_frame_lock_file = tk.Frame(root)
    sf_entry_lock_file = Combopicker(master=sf_entry_frame_lock_file, values=['全选'], frameheight=50)
    sf_browse_lockfile_button = ttk.Button(root, textvariable=sf_browse_lockfile_button_text,
                                           command=lambda: choose_lockitems('lockfile'))

    sf_label_autorun = ttk.Label(root, textvariable=sf_label_autorun_text)
    sf_entry_is_autorun = tk.BooleanVar()
    sf_option_autorun = ttk.Checkbutton(root,
                                        textvariable=sf_option_autorun_text,
                                        variable=sf_entry_is_autorun)

    class ZFunc:
        @staticmethod
        def help_main():
            from LT_Dic import help_main_text
            tkinter.messagebox.showinfo(title='Movefile', message=help_main_text[lang_num])

        @staticmethod
        def help_before_use():
            from LT_Dic import help_before_use_text
            tkinter.messagebox.showinfo(title='Movefile',
                                        message=help_before_use_text[lang_num])

        @staticmethod
        def cf_help():
            from LT_Dic import cf_help_text
            tkinter.messagebox.showinfo(title='Movefile', message=cf_help_text[lang_num])

        @staticmethod
        def cf_help_keep():
            from LT_Dic import cf_help_keep_text
            tkinter.messagebox.showinfo(title='Movefile', message=cf_help_keep_text[lang_num])

        @staticmethod
        def cf_help_timeset():
            from LT_Dic import cf_help_timeset_text
            tkinter.messagebox.showinfo(title='Movefile', message=cf_help_timeset_text[lang_num])

        @staticmethod
        def sf_help():
            from LT_Dic import sf_help_text
            tkinter.messagebox.showinfo(title='Movefile', message=sf_help_text[lang_num])

        @staticmethod
        def sf_removable_help():
            from LT_Dic import sf_removable_help_text
            tkinter.messagebox.showinfo(title='Movefile', message=sf_removable_help_text[lang_num])

        @staticmethod
        def sf_lock_help():
            from LT_Dic import sf_lock_help_text
            tkinter.messagebox.showinfo(title='Movefile', message=sf_lock_help_text[lang_num])

        @staticmethod
        def cf_is_num():
            try:
                float(cf_entry_time.get())
            except:
                return False
            else:
                return True

        @staticmethod
        def cf_has_blank():
            blank_num = 0
            if len(cf_entry_old_path.get()) == 0:
                blank_num += 1
            elif len(cf_entry_time.get()) == 0:
                blank_num += 1
            elif cf_entry_mode.get() == 0:
                blank_num += 1
            if blank_num == 0:
                return False
            else:
                return True

        @staticmethod
        def cf_path_error():
            try:
                os.listdir(cf_entry_old_path.get())
                if cf_entry_new_path.get() != '':
                    os.listdir(cf_entry_new_path.get())
                if cf_entry_old_path.get() == cf_entry_new_path.get():
                    return 'same_path_error'
            except:
                return True
            else:
                return False

        @staticmethod
        def sf_has_blank():
            blank_entry_num = 0
            if sf_place_mode.get() == 'movable' and len(sf_entry_select_removable.get()) == 0:
                blank_entry_num += 1
            elif sf_place_mode.get() == 'local' and len(sf_entry_path_1.get()) == 0:
                blank_entry_num += 1
            elif len(sf_entry_path_2.get()) == 0:
                blank_entry_num += 1
            if blank_entry_num == 0:
                return False
            else:
                return True

        @staticmethod
        def sf_path_error():
            try:
                if sf_place_mode.get() == 'movable':
                    os.listdir(sf_entry_select_removable.get().split(':')[0][-1] + ':')
                else:
                    os.listdir(sf_entry_path_1.get())
                os.listdir(sf_entry_path_2.get())
                if sf_entry_path_1.get() == sf_entry_path_2.get() and sf_place_mode.get() != 'movable':
                    return 'same_path_error'
                elif (sf_entry_path_1.get() in sf_entry_path_2.get() or sf_entry_path_2.get() in sf_entry_path_1.get())\
                        and sf_place_mode.get() != 'movable':
                    return 'in_path_error'
                elif (sf_entry_select_removable.get().split(':')[0][-1] + ':') in sf_entry_path_2.get():
                    return 'in_disk_path_error'
            except:
                return True
            else:
                return False

        @staticmethod
        def cf_has_error():
            if not ZFunc.cf_is_num():
                tkinter.messagebox.showwarning('Movefile', r_label_text_dic['num_warning'][lang_num])
                return True
            elif ZFunc.cf_has_blank():
                tkinter.messagebox.showwarning(title='Movefile', message=r_label_text_dic['blank_warning'][lang_num])
                return True
            elif ZFunc.cf_path_error() == 'same_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=r_label_text_dic['same_path_warning'][lang_num])
                return True
            elif ZFunc.cf_path_error():
                tkinter.messagebox.showwarning(title='Movefile', message=r_label_text_dic['path_warning'][lang_num])
                return True
            else:
                return False

        @staticmethod
        def sf_has_error():
            path_error_data = ZFunc.sf_path_error()
            if ZFunc.sf_has_blank():
                tkinter.messagebox.showwarning(title='Movefile', message=r_label_text_dic['blank_warning'][lang_num])
                return True
            elif path_error_data == 'same_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=r_label_text_dic['same_path_warning'][lang_num])
                return True
            elif path_error_data == 'in_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=r_label_text_dic['in_path_warning'][lang_num])
                return True
            elif path_error_data == 'in_disk_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=r_label_text_dic['in_disk_path_warning'][lang_num])
                return True
            elif path_error_data:
                tkinter.messagebox.showwarning(title='Movefile', message=r_label_text_dic['path_warning'][lang_num])
                return True
            else:
                return False

    def initial_entry():
        if not cf_entry_old_path.get():
            cf_entry_old_path.insert(0, desktop_path)
            cf_refresh_whitelist_entry()
        if not cf_entry_mode.get():
            cf_entry_mode.set(1)
        if not cf_entry_time.get():
            cf_entry_time.insert(0, '0')
        if not sf_entry_mode.get():
            sf_entry_mode.set('double')

    def ask_save_name():
        global ask_name_window
        list_saving_data()

        def savefile(function, save_name='New_Setting'):  # 保存文件
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

            if function == 'cf':  # 如果当前界面为cf
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

            if function == 'sf':  # 如果当前界面为sf
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
                sf_data.set(save_name, 'lock_folder', sf_entry_lock_folder.get())
                sf_data.set(save_name, 'lock_file', sf_entry_lock_file.get())
                sf_data.set(save_name, 'autorun', str(sf_entry_is_autorun.get()))
                sf_data.write(open(sf_data_path + r'Syncfile_data.ini', 'w+', encoding='ANSI'))

            tkinter.messagebox.showinfo(title=r_label_text_dic['succ_save'][lang_num][0],
                                        message=r_label_text_dic['succ_save'][lang_num][1])
            continue_button.config(state=tk.NORMAL)

        def sure_save():
            savefile(function=cf_or_sf.get(), save_name=name_entry.get())
            exit_asn()

        def exit_asn():
            ask_name_window.quit()
            ask_name_window.withdraw()

        mode = cf_or_sf.get()
        if mode == 'cf':
            has_error = ZFunc.cf_has_error()
            pri_save_names = cf_save_names
        elif mode == 'sf':
            has_error = ZFunc.sf_has_error()
            pri_save_names = sf_save_names
        else:
            has_error = True
            pri_save_names = []
        if not has_error:
            ask_name_window = tk.Tk()
            ask_name_window.iconbitmap(mf_data_path + r'Movefile.ico')
            ask_name_window.geometry('400x35')
            ask_name_window.title(r_label_text_dic['ask_name_window'][lang_num])
            ask_name_window.focus_force()
            last_edit_name = 'New_Setting'
            if last_saving_data:
                if last_saving_data[0] == mode:
                    last_edit_name = last_saving_data[1]
                else:
                    last_edit_name = last_saving_data[2]
            name_label = ttk.Label(ask_name_window, text=r_label_text_dic['name_label'][lang_num])
            name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')

            name_entry = ttk.Combobox(ask_name_window, values=pri_save_names)
            name_entry.insert(0, last_edit_name)
            name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='W')
            sure_name_button = ttk.Button(ask_name_window, text=r_label_text_dic['sure_name_button'][lang_num],
                                          command=lambda: sure_save())
            sure_name_button.grid(row=0, column=2, sticky='W')
            ask_name_window.bind('<Return>', lambda event: sure_save())
            ask_name_window.protocol('WM_DELETE_WINDOW', exit_asn)
            ask_name_window.mainloop()

    def read_saving(ask_path=False):
        global ask_saving_root
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
            Place('cf')
            cf_or_sf.set('cf')
            if data_error('cf', setting_name):
                tkinter.messagebox.showwarning(title='Movefile', message=r_label_text_dic['ini_error'][lang_num])

        def open_sf_saving(setting_name):
            if sf_entry_path_1.get() != '':
                sf_entry_path_1.delete(0, 'end')
            if sf_entry_path_2.get() != '':
                sf_entry_path_2.delete(0, 'end')
            if sf_entry_lock_folder.get() != '':
                sf_entry_lock_folder.delete(0, 'end')
            if sf_entry_lock_file.get() != '':
                sf_entry_lock_file.delete(0, 'end')

            place_mode = sf_file.get(setting_name, 'place_mode')
            sf_place_mode.set(place_mode)
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
            sf_entry_lock_folder.insert(0, sf_file.get(setting_name, 'lock_folder'))
            sf_entry_lock_file.insert(0, sf_file.get(setting_name, 'lock_file'))
            sf_entry_is_autorun.set(sf_file.get(setting_name, 'autorun'))
            Place('sf', place_mode)
            cf_or_sf.set('sf')
            if data_error('sf', setting_name):
                tkinter.messagebox.showwarning(title='Movefile', message=r_label_text_dic['ini_error'][lang_num])

        def refresh_saving():
            nonlocal new_values
            try:
                list_saving_data()
                if read_mode_entry.get() in ['清理文件(Cleanfile)', 'Cleanfile']:
                    new_values = cf_save_names
                    read_name_entry['value'] = new_values
                elif read_mode_entry.get() in ['同步文件(Syncfile)', 'Syncfile']:
                    new_values = sf_save_names
                    read_name_entry['value'] = new_values
                else:
                    new_values = []
                if read_name_entry.get() not in new_values:
                    read_name_entry.current(0)
            except:
                pass

        def del_saving():
            del_mode = read_mode_entry.get()
            del_name = read_name_entry.get()
            is_continue = tkinter.messagebox.askyesno(title='Movefile', message='确认删除配置 ' + del_name + ' ?')
            ini_file = configparser.ConfigParser()
            if del_mode in ['清理文件(Cleanfile)', 'Cleanfile'] and is_continue:
                ini_file.read(cf_data_path + 'Cleanfile_data.ini')
                ini_file.remove_section(del_name)
                ini_file.write(open(cf_data_path + r'Cleanfile_data.ini', 'w+', encoding='ANSI'))
            elif del_mode in ['同步文件(Syncfile)', 'Syncfile'] and is_continue:
                ini_file.read(sf_data_path + 'Syncfile_data.ini')
                ini_file.remove_section(del_name)
                ini_file.write(open(sf_data_path + r'Syncfile_data.ini', 'w+', encoding='ANSI'))
            exit_asr()

        def sure_open():
            saving_name = read_name_entry.get()
            if read_mode_entry.get() in ['清理文件(Cleanfile)', 'Cleanfile']:
                open_cf_saving(saving_name)
            elif read_mode_entry.get() in ['同步文件(Syncfile)', 'Syncfile']:
                open_sf_saving(saving_name)
            root.title('Movefile   --> ' + saving_name)
            exit_asr()

        def exit_asr():
            ask_saving_root.withdraw()
            ask_saving_root.quit()

        if ask_path:
            ask_saving_root = tk.Tk()
            ask_saving_root.iconbitmap(mf_data_path + r'Movefile.ico')
            if lang_num == 0:
                ask_saving_root.geometry('680x35')
            elif lang_num == 1:
                ask_saving_root.geometry('700x35')
            ask_saving_root.title(r_label_text_dic['readfile_menu'][lang_num])
            ask_saving_root.focus_force()
            last_edit_mode = ''
            last_edit_name = ''
            save_names = []
            if last_saving_data:
                last_edit_mode = last_saving_data[0]
                last_edit_name = last_saving_data[1]
            read_name_label = ttk.Label(ask_saving_root, text=r_label_text_dic['read_name_label'][lang_num])
            read_name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')
            read_mode_entry = ttk.Combobox(ask_saving_root, values=r_label_text_dic['read_mode_entry'][lang_num],
                                           state='readonly')
            read_mode_entry.grid(row=0, column=1, pady=5, padx=5)
            if last_edit_mode == 'sf':
                read_mode_entry.current(1)
            elif last_edit_mode == 'cf':
                read_mode_entry.current(0)
            read_name_entry = ttk.Combobox(ask_saving_root, values=save_names, state='readonly')
            refresh_saving()
            for save_index, name in enumerate(new_values):
                if name == last_edit_name:
                    read_name_entry.current(save_index)
            read_name_entry.grid(row=0, column=2, padx=5, pady=5, ipadx=20, sticky='W')
            del_save_button = ttk.Button(ask_saving_root, text=r_label_text_dic['del_save_button'][lang_num],
                                         command=lambda: del_saving())
            del_save_button.grid(row=0, column=3, padx=5, pady=5)
            sure_name_bottom = ttk.Button(ask_saving_root, text=r_label_text_dic['sure_name_bottom'][lang_num],
                                          command=lambda: sure_open())
            sure_name_bottom.grid(row=0, column=4, pady=5)
            ask_saving_root.bind('<Enter>', lambda event: refresh_saving())
            ask_saving_root.bind('<Return>', lambda event: sure_open())
            ask_saving_root.protocol('WM_DELETE_WINDOW', exit_asr)
            ask_saving_root.mainloop()
        elif mode == 'cf':
            open_cf_saving(save_name)
            root.title('Movefile   --> ' + save_name)
        elif mode == 'sf':
            open_sf_saving(save_name)
            root.title('Movefile   --> ' + save_name)
        initial_entry()

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
        lockfolder = sf_entry_lock_folder.get()
        lockfile = sf_entry_lock_file.get()
        if len(path1) == 2:
            area_name = win32api.GetVolumeInformation(path1)[0]
        if mode == 'single':
            single_sync = True
        else:
            single_sync = False
        sf_sync_dir(path1, path2, single_sync, lang_num, area_name, lockfile, lockfolder)

    def change_language(language):
        nonlocal lang_num
        general_data.set('General', 'language', language)
        general_data.write(open(mf_data_path + r'Movefile_data.ini', "w+", encoding='ANSI'))
        lang_num = language_num(language)
        set_language(lang_num)
        Place(cf_or_sf.get(), sf_place_mode.get())
        tkinter.messagebox.showinfo(title='Movefile', message=r_label_text_dic['change_language'][lang_num])

    def continue_going():
        if cf_or_sf.get() == 'cf' and not ZFunc.cf_has_error():
            cf_operator = threading.Thread(target=lambda: cf_operate_from_root(), daemon=True)
            cf_operator.start()
            root.withdraw()
        elif cf_or_sf.get() == 'sf' and not ZFunc.sf_has_error():
            sf_operator = threading.Thread(target=lambda: sf_operate_from_root(), daemon=True)
            sf_operator.start()
            root.withdraw()

    def exit_program():
        task_menu.stop()
        if 'sync_bar' in globals().keys():
            sync_bar.quit()
            sync_bar.destroy()
        if 'ask_saving_root' in globals().keys():
            ask_saving_root.quit()
            ask_saving_root.destroy()
        if 'ask_name_window' in globals().keys():
            ask_name_window.quit()
            ask_name_window.destroy()
        root.quit()
        root.destroy()
        ask_permit.join()
        butt_icon.join()
        background_detect.join()

    # 创建按键
    blank_pix = ttk.Label(root, text=' ')
    blank_pix.grid(row=8, column=0, ipadx=67, pady=4, padx=0, sticky='E')
    save_button = ttk.Button(root, textvariable=save_button_text, command=lambda: ask_save_name())
    continue_button = ttk.Button(root, textvariable=continue_button_text, command=lambda: continue_going())
    continue_button.config(state=tk.DISABLED)

    # 菜单栏
    main_menu = tk.Menu(root)
    file_menu = tk.Menu(main_menu, tearoff=False)
    file_menu.add_command(label=readfile_menu_text.get(), command=lambda: read_saving(ask_path=True),
                          accelerator="Ctrl+O")
    file_menu.add_command(label=savefile_menu_text.get(), command=lambda: ask_save_name(), accelerator="Ctrl+S")

    option_menu = tk.Menu(main_menu, tearoff=False)
    is_startup_run = tk.BooleanVar()
    is_startup_run.set(general_data.get('General', 'autorun'))
    option_menu.add_checkbutton(label=autorun_menu_text.get(), variable=is_startup_run,
                                command=lambda: set_startup(is_startup_run.get()))

    language_menu = tk.Menu(main_menu, tearoff=False)
    language_menu.add_radiobutton(label='简体中文', variable=root_language, value='Chinese',
                                  command=lambda: change_language('Chinese'))
    language_menu.add_radiobutton(label='English', variable=root_language, value='English',
                                  command=lambda: change_language('English'))

    help_menu = tk.Menu(main_menu, tearoff=False)
    help_menu.add_command(label=about_menu_text.get(), command=ZFunc.help_main)
    help_menu.add_command(label=precautions_menu_text.get(), command=ZFunc.help_before_use)
    help_menu.add_separator()
    help_menu.add_command(label='Cleanfile', command=ZFunc.cf_help)
    help_menu.add_command(label=cf_keep_menu_text.get(), command=ZFunc.cf_help_keep)
    help_menu.add_command(label=cf_expire_menu_text.get(), command=ZFunc.cf_help_timeset)
    help_menu.add_separator()
    help_menu.add_command(label='Syncfile', command=ZFunc.sf_help)
    help_menu.add_command(label=sf_removable_menu_text.get(), command=ZFunc.sf_removable_help)
    help_menu.add_command(label=sf_lock_menu_text.get(), command=ZFunc.sf_lock_help)

    main_menu.add_cascade(label=file_menu_text.get(), menu=file_menu)
    main_menu.add_cascade(label=option_menu_text.get(), menu=option_menu)
    main_menu.add_cascade(label=language_menu_text.get(), menu=language_menu)
    main_menu.add_cascade(label=help_menu_text.get(), menu=help_menu)
    root.config(menu=main_menu)

    # 托盘菜单
    menu = (
        MenuItem(taskbar_setting_text.get(), lambda event: root.deiconify(), default=True), Menu.SEPARATOR,
        MenuItem(taskbar_exit_text.get(), lambda event: exit_program()))
    image = Image.open(mf_data_path + 'Movefile.ico')
    task_menu = pystray.Icon("icon", image, "Movefile", menu)

    root.bind("<Control-o>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-O>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-s>", lambda event: ask_save_name())
    root.bind("<Control-S>", lambda event: ask_save_name())
    root.bind('<Button-1>'), lambda: sf_refresh_disk_list(none_disk=True)
    root.protocol('WM_DELETE_WINDOW', root.withdraw)
    # 重新定义点击关闭按钮的处理

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
                    if str(new_area_data[2]) == autorun_id[0] and tkinter.messagebox.askokcancel(title='Movefile',
                                                                                                 message=f'检测到可移动磁盘{new_area_data[1]} ({new_area_data[0][:-1]})接入，' + '\n' +
                                                                                                         f'确定按配置 "{autorun_id[1]}" 进行同步?'):
                        run_list.append([new_area_data[0], new_area_data[1], autorun_id[1]])
                new_areas_data.remove(new_area_data)
            if run_list:
                sf_autorun_operation('movable', run_list)
            time.sleep(1)

    if first_ask:
        initial_entry()
        cf_or_sf.set('cf')
        Place('cf')
        ZFunc.help_main()
        ZFunc.help_before_use()
    elif muti_ask:
        read_saving()
        cf_refresh_whitelist_entry()
        continue_button.config(state=tk.NORMAL)
        if cf_or_sf.get() == '':
            cf_or_sf.set('cf')
            Place('cf')
        if startup_ask:
            root.withdraw()

    butt_icon = threading.Thread(target=task_menu.run, daemon=True)
    butt_icon.start()
    background_detect = threading.Thread(target=lambda: detect_removable_disks_thread(), daemon=True)
    background_detect.start()
    ask_permit = threading.Thread(target=lambda: ask_sync_disk(), daemon=True)
    ask_permit.start()

    root.mainloop()


def main():
    Initialization()
    if first_visit:
        make_ui(first_ask=True)
    elif boot_time <= 120 and ask_time_today == 1:
        cf_autorun_operation()
        sf_autorun_operation('local')
        make_ui(muti_ask=True, startup_ask=True)
    else:
        make_ui(muti_ask=True)


if __name__ == '__main__':
    main()
