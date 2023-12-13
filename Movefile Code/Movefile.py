# -*- coding: utf-8 -*-
"""
If you have any suggestion for optimizing this program,
it's welcomed to submit that to the author.

Created on Wed Dec 21 17:07:30 2022

@author: Robert He
QQ: 2567466856
GitHub address: https://github.com/HNRobert/Movefile
"""

import configparser
import logging
import os
import sys
import time
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
import winreg
from base64 import b64decode
from ctypes import windll
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from shutil import copy2 as shutil_copy2, move as shutil_move, Error as shutil_Error
from threading import Thread

from filecmp import dircmp
from PIL import Image
from mttkinter import mtTkinter as tk
from pathlib import Path
from psutil import disk_partitions, pids
from pystray import MenuItem, Menu, Icon
from win32api import GetVolumeInformation
from win32com.client import Dispatch
from win32gui import FindWindow, ShowWindow
from winshell import CreateShortcut

import Movefile_icon as icon
from ComBoPicker import Combopicker
from LT_Dic import *
from win10toast_edited import ToastNotifier


class Initialization:
    def __init__(self):
        self.startup_visit = self.get_startup_state()
        self.roaming_path = None
        self.first_visit = False
        self.set_data_path()

        self.mf_data = configparser.ConfigParser()
        self.mf_data.read(os.path.join(mf_data_path, r'Movefile_data.ini'))

        self.log_file_path = os.path.join(mf_data_path, r'Movefile.log')
        self.set_log_writer()

        self.mf_ico = None
        if not os.path.exists(os.path.join(mf_data_path, r'Movefile.ico')):
            self.load_icon()

        self.ask_time_today = 0
        self.init_config()

        if self.first_visit:  # 判断是否为首次访问
            logging.info("\nThis is the first visit of this program.")

    def get_startup_state(self):
        if "--startup_visit" in sys.argv:
            return True
        return False

    def set_data_path(self):
        """
        The function globalize the route where previous data of this program can be found.
        """

        global mf_data_path, cf_data_path, cf_config_path, sf_data_path, sf_config_path, toaster, program_finished
        toaster = ToastNotifier()
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        self.roaming_path = os.path.join(
            winreg.QueryValueEx(key, 'AppData')[0])
        mf_data_path = os.path.join(self.roaming_path, r'Movefile')
        cf_data_path = os.path.join(mf_data_path, r'Cleanfile')
        cf_config_path = os.path.join(cf_data_path, r'Cleanfile_data.ini')
        sf_data_path = os.path.join(mf_data_path, r'Syncfile')
        sf_config_path = os.path.join(sf_data_path, r'Syncfile_data.ini')
        program_finished = False

        if 'Movefile' not in os.listdir(self.roaming_path):
            self.first_visit = True
            os.mkdir(mf_data_path)
            time.sleep(0.1)
        if 'Cleanfile' not in os.listdir(mf_data_path):
            os.mkdir(cf_data_path)
        if 'Syncfile' not in os.listdir(mf_data_path):
            os.mkdir(sf_data_path)

    def init_config(self):

        time_now = datetime.today()
        date = str(time_now.date())

        if not os.path.exists(os.path.join(mf_data_path, r'Movefile_data.ini')):  # 创建配置文件
            file = open(os.path.join(mf_data_path, r'Movefile_data.ini'),
                        'w', encoding="ANSI")
            file.close()

        if not self.mf_data.has_section("General"):
            self.mf_data.add_section("General")

        if not self.mf_data.has_option("General", "date") or self.mf_data.get("General", "date") != str(date):
            self.ask_time_today = 1
            self.mf_data.set("General", "date", date)
            self.mf_data.set("General", "asktime_today", '1')
        else:
            self.ask_time_today = self.mf_data.getint(
                "General", "asktime_today") + 1
            self.mf_data.set("General", "asktime_today",
                             str(self.ask_time_today))

        if not self.mf_data.has_option('General', 'language'):
            dll_handle = windll.kernel32
            if hex(dll_handle.GetSystemDefaultUILanguage()) == '0x804':
                self.mf_data.set('General', 'language', 'Chinese')
            else:
                self.mf_data.set('General', 'language', 'English')

        if not self.mf_data.has_option('General', 'autorun'):
            self.mf_data.set('General', 'autorun', 'False')
        if not self.mf_data.has_option('General', 'desktop_shortcut'):
            self.mf_data.set('General', 'desktop_shortcut', 'False')

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
        desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
        startup_path = os.path.join(
            roaming_path, r"Microsoft\Windows\Start Menu\Programs\StartUp")

        if os.path.exists(os.path.join(desktop_path, r"Movefile.lnk")):
            self.mf_data.set('General', 'desktop_path', 'True')
        else:
            self.mf_data.set('General', 'desktop_path', 'False')
        if os.path.exists(os.path.join(startup_path, r"Movefile.lnk")):
            self.mf_data.set('General', 'autorun', 'True')
        else:
            self.mf_data.set('General', 'autorun', 'False')

        self.mf_data.write(
            open(os.path.join(mf_data_path, r'Movefile_data.ini'), "w+", encoding='ANSI'))

    def load_icon(self):
        self.mf_ico = open(os.path.join(mf_data_path, r'Movefile.ico'), 'wb')
        self.mf_ico.write(b64decode(icon.Movefile_ico))
        self.mf_ico.close()

    def set_log_writer(self):
        log_file_path = self.log_file_path
        if not os.path.exists(log_file_path):
            logfile = open(log_file_path, 'a')
            logfile.close()
        formatter = "[%(asctime)s] - [%(levelname)s]: %(message)s"
        logging.basicConfig(level=logging.INFO,
                            filename=log_file_path,
                            filemode='a+',
                            format=formatter)


# The ProgressBar class generate a root used to display the progress of a task.
class ProgressBar:
    def __init__(self, title, label1, label2, lang_num):
        self.initialization_done = False

        self.title = title
        self.label1 = label1
        self.label2 = label2
        self.label_dic = progress_root_label_dic
        self.lang_num = lang_num

        """
        self.main_progress_label = None
        self.main_progress_bar = None
        self.current_file_label = None
        self.show_running_bar = None
        self.progress_root = None
        self.roll_bar = None
        """

    def set_label1(self, content):
        self.main_progress_label['text'] = content

    def set_label2(self, content):
        self.current_file_label['text'] = content

    def launch(self):
        self.progress_root = tk.Toplevel(root)
        self.progress_root.title(self.title)
        self.progress_root.geometry('420x115')
        self.progress_root.iconbitmap(
            os.path.join(mf_data_path, r'Movefile.ico'))
        self.main_progress_label = ttk.Label(
            self.progress_root, text=self.label1)
        self.main_progress_label.grid(
            row=0, column=0, padx=10, pady=5, sticky='SW')
        self.main_progress_bar = ttk.Progressbar(self.progress_root)
        self.main_progress_bar.grid(
            row=1, column=0, padx=10, pady=0, ipadx=150, sticky='W')
        self.current_file_label = ttk.Label(
            self.progress_root, text=self.label2)
        self.current_file_label.grid(
            row=2, column=0, padx=10, pady=5, sticky='SW')
        self.show_running_bar = ttk.Progressbar(
            self.progress_root, mode='indeterminate')
        self.show_running_bar.grid(
            row=3, column=0, padx=10, pady=0, ipadx=150, sticky='W')
        self.progress_root.protocol(
            'WM_DELETE_WINDOW', lambda: self.sync_bar_on_exit())
        self.roll_bar = Thread(target=self.show_running, daemon=True)
        self.roll_bar.start()
        self.initialization_done = True

    def show_running(self):
        self.show_running_bar.start(10)

    def sync_bar_on_exit(self):
        if tkinter.messagebox.askyesno(title='Syncfile', message=self.label_dic['confirm_exit_text'][self.lang_num]):
            self.progress_root.destroy()
            self.roll_bar.join()
            return True
        else:
            return False

    def progress_root_destruction(self):
        self.progress_root.destroy()


# The CheckMFProgress class is used to check if the program is already running.
# If it's running, it will display a message box to inform the user, and put the window on the top.
class CheckMFProgress:

    def __init__(self):
        self.continue_this_progress = True
        self.pl = pids()
        self.classname = None
        if self.proc_root_on():
            self.continue_this_progress = False

    def proc_root_on(self):
        hwnd = FindWindow(self.classname, 'Movefile Setting')
        if hwnd:
            temp_root = tk.Tk()
            temp_root.withdraw()
            ShowWindow(hwnd, 5)
            tkinter.messagebox.showinfo(
                title="Movefile", message="The app's running!")
            temp_root.quit()
            temp_root.destroy()
            return True
        return False


def startup_autorun():
    time.sleep(1)
    cf_autorun_operation()
    sf_autorun_operation('local')


def get_start_menu_path():
    # 获取用户名
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
    start_menu_path = os.path.join(
        roaming_path, r"Microsoft\Windows\Start Menu\Programs")
    return start_menu_path


def set_startup(state=True, lang_n=0):
    """
    The function sets the auto startup state to either True or False.

    :param state: The `state` parameter is a boolean value that determines whether the startup process
    should be enabled or disabled. If `state` is `True`, the startup process will be enabled. If `state`
    is `False`, the startup process will be disabled, defaults to True (optional)
    """
    # 将快捷方式添加到自启动目录
    startup_path = os.path.join(get_start_menu_path(), r"StartUp")
    bin_path = r"Movefile.exe"
    shortcut_path = os.path.join(startup_path, r"Movefile.lnk")
    desc = lnk_desc[lang_n]
    icon_ = os.path.join(mf_data_path, r'Movefile.ico')
    gen_cf = configparser.ConfigParser()
    gen_cf.read(os.path.join(mf_data_path, r'Movefile_data.ini'))
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
    if state:
        gen_cf.set('General', 'autorun', 'True')
        CreateShortcut(
            Path=shortcut_path,
            Target=bin_path,
            Icon=(icon_, 0),
            Description=desc,
            Arguments="--startup_visit")
    else:
        gen_cf.set('General', 'autorun', 'False')
    gen_cf.write(
        open(os.path.join(mf_data_path, r'Movefile_data.ini'), "w+", encoding='ANSI'))


def put_desktop_shortcut(state=True, lang_n=0):
    """
    The function `put_desktop_shortcut` allows you to put the shortcut of this program on Desktop.

    :param state: The state parameter is a boolean value that determines whether the start menu should be displayed or not. If state is set to True, the start menu will be displayed. If state is set to False, the start menu will not be displayed, defaults to True (optional)
    :param lang_n: The `lang_n` parameter is used to specify the language for the start menu. It is an integer value that represents the language code, defaults to 1 (optional)
    """
    # 将快捷方式添加到桌面
    # 获取用户名
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
    bin_path = r"Movefile.exe"
    shortcut_path = os.path.join(desktop_path, r"Movefile.lnk")
    desc = lnk_desc[lang_n]
    icon_ = os.path.join(mf_data_path, r'Movefile.ico')
    gen_cf = configparser.ConfigParser()
    gen_cf.read(os.path.join(mf_data_path, r'Movefile_data.ini'))
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
    if state:
        gen_cf.set('General', 'desktop_shortcut', 'True')
        CreateShortcut(
            Path=shortcut_path,
            Target=bin_path,
            Icon=(icon_, 0),
            Description=desc)
    else:
        gen_cf.set('General', 'desktop_shortcut', 'False')
    gen_cf.write(
        open(os.path.join(mf_data_path, r'Movefile_data.ini'), "w+", encoding='ANSI'))


def language_num(language_name):
    """
    The function takes a string as input, and returns the corresponding language number.

    :param language_name: The `language_name` parameter is a string that represents the language name.
    :return: The function returns the language number as an integer.
    """
    if language_name == 'Chinese':
        l_num = 0
    elif language_name == 'English':
        l_num = 1
    else:
        l_num = 2
    return l_num


def list_saving_data():

    def get_last_edit_in(configer, savings):
        for saving_name in savings:
            if configer.get(saving_name, '_last_edit_') == 'True':
                return saving_name
        return ''

    cf_file = configparser.ConfigParser()
    cf_file.read(cf_config_path)
    cf_save_names = cf_file.sections()
    sf_file = configparser.ConfigParser()
    sf_file.read(sf_config_path)
    sf_save_names = sf_file.sections()

    cf_latest_saving = get_last_edit_in(cf_file, cf_save_names)
    sf_latest_saving = get_last_edit_in(sf_file, sf_save_names)
    last_saving_data = ['cf', cf_latest_saving, sf_latest_saving]

    return last_saving_data, cf_save_names, sf_save_names


def scan_removable_disks(s_uuid=None):
    """
    This function scans for removable disks and returns their UUIDs.

    :param s_uuid: The s_uuid parameter is an optional parameter that represents the UUID (Universally
    Unique Identifier) of a specific removable disk. If provided, the function will only scan and return
    information about the removable disk with the specified UUID. If not provided, the function will
    scan and return information about all available removable disks
    """
    disk_list = []
    show_list = []
    uuid_disk_pairs = []
    for item in disk_partitions():
        # 判断是不是可移动磁盘
        if "removable" in item.opts:
            # 获取可移动磁盘的盘符
            if item.mountpoint not in disk_list:
                disk_list.append(item.mountpoint)
    if disk_list:
        for pf in disk_list:
            seria_data = GetVolumeInformation(pf)
            area_name = seria_data[0]
            area_number = seria_data[1]
            fso = Dispatch("Scripting.FileSystemObject")
            drv = fso.GetDrive(pf)
            total_space = drv.TotalSize / 2 ** 30
            show_name = area_name + \
                ' (' + pf[:-1] + ')' + '   ' + \
                str(total_space // 0.01 / 100) + ' GB'
            show_list.append(show_name)
            uuid_disk_pairs.append([str(area_number), show_name])
        if s_uuid is None:
            return show_list
        else:
            for pair in uuid_disk_pairs:
                if pair[0] == s_uuid:
                    return pair[1]
    return []


def detect_removable_disks_thread():
    """
    The function detects removable disks using threading.
    """
    global new_areas_data
    disk_list = []
    area_data_list = []
    number_book = {}
    new_areas_data = []
    while not program_finished:
        for item in disk_partitions():
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
                    seria_number = GetVolumeInformation(pf)
                    area_name = seria_number[0]
                    area_number = seria_number[1]
                    if area_number not in area_data_list:
                        area_data_list.append(area_number)
                        number_book[pf] = area_number
                        new_areas_data.append([pf, area_name, area_number])
        time.sleep(0.5)


def scan_items(folder_path):  # 扫描路径下所有文件夹
    def scan_folders_in(f_path):  # 扫描目录下所有的文件夹，并返回路径列表
        surf_items = os.scandir(f_path)
        folders = [f_path]
        for item_data in surf_items:
            if item_data.is_dir():
                # 继续遍历文件夹内文件夹，直到记下全部文件夹路径
                folders.extend(scan_folders_in(item_data.path))
        folders = sorted(set(folders))  # 排序 + 排除重复项
        surf_items.close()
        return folders

    file_store = []
    folder_store = scan_folders_in(folder_path)
    for folder in folder_store:  # 遍历所有文件夹
        files = [dI.path for dI in os.scandir(folder) if dI.is_file()]
        # 如上只生成本文件夹内 文件的路径
        file_store.extend(files)  # 存储上面文件路径
    for i in range(len(file_store)):
        file_store[i] = file_store[i][len(folder_path):]  # 返回相对位置
    return folder_store, file_store


def cf_move_dir(old__path, new__path, pass__file, pass__format, overdue_time, check__mode, is__move__folder):
    """
    The function `cf_move_dir` is used to move files or folders from one directory to another, with
    options for specifying file formats, checking modes, and handling overdue files.

    :param old__path: The current path or location of the file or folder that needs to be moved
    :param new__path: The new path where the file or folder will be moved to
    :param pass__file: The parameter "pass__file" is used to specify whether to pass files or not. It is
    a boolean value where True means files will be passed and False means files will not be passed
    :param pass__format: The pass__format parameter is used to specify the format of the files that
    should be moved. It can be a string or a list of strings representing the file formats. For example,
    if you want to move only text files, you can set pass__format to "txt" or ["txt"]
    :param overdue_time: The parameter "overdue_time" is used to specify the time in seconds after which
    a file or folder is considered overdue
    :param check__mode: The check__mode parameter is used to specify the type of check to be performed.
    It can have one of the following values:
    :param is__move__folder: A boolean value indicating whether the operation is to move a folder or not
    """
    mf_file = configparser.ConfigParser()
    mf_file.read(os.path.join(mf_data_path, r'Movefile_data.ini'))
    lang_num = language_num(mf_file.get('General', 'language'))

    def cf_show_notice(old_path, new_path, move_name, error_name):
        new_folder = new_path.split('\\')[-1]
        old_folder = old_path.split('\\')[-1]
        mf_icon_path = os.path.join(mf_data_path, r'Movefile.ico')
        if len(move_name) > 0:
            notice_title = cfdic['title_p1'][lang_num] + old_folder + \
                cfdic['title_p2_1'][lang_num] + new_folder + ':'
            if new_path == '':
                notice_title = cfdic['title_p1'][lang_num] + \
                    old_folder + cfdic['title_p2_2'][lang_num]
            logging.info("\n" + notice_title + "\n" + move_name[:-3])
            toaster.show_toast(notice_title, move_name[:-3],
                               icon_path=mf_icon_path,
                               duration=10,
                               threaded=False)
        else:
            notice_title = old_folder + cfdic['cltitle'][lang_num]
            notice_content = cfdic['clcontent'][lang_num]
            logging.info("\n" + notice_title + "\n" + notice_content)
            toaster.show_toast(notice_title, notice_content,
                               icon_path=mf_icon_path,
                               duration=10,
                               threaded=False)
        if len(error_name) > 0:
            notice_title = cfdic['errtitle'][lang_num]
            notice_content = error_name[:-3] + \
                '\n' + cfdic['errcontent'][lang_num]
            logging.warning("\n" + notice_title + "\n" + notice_content)
            toaster.show_toast(notice_title, notice_content,
                               icon_path=mf_icon_path,
                               duration=10,
                               threaded=False)

    def del_item(path):  # 递归删除文件夹或单个文件, 代替shutil.rmtree和os.remove  (shutil.rmtree会莫名报错)
        error_files = ''
        moved_files = ''
        if os.path.isdir(path):
            del_data = scan_items(path)  # 扫描文件夹里所有子文件夹和文件
            for dfile in del_data[1]:
                try:
                    os.remove(os.path.join(path, dfile))
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

    def get_cf_tasks(baroot):
        """
        The function "get_cf_tasks" decide what to clean in a directory.

        :param baroot: The progress bar object
        """
        tasks = []
        item_datas = os.scandir(old__path)  # 获取文件夹下所有文件和文件夹
        now = int(time.time())  # 当前时间
        for item_data in item_datas:
            if ('.' + item_data.name.split('.')[-1] in pass__format and not item_data.is_dir()
                    or item_data.name in pass__file):
                continue
            if item_data.name == 'Movefile.exe' or item_data.name == new__path.split('\\')[-1]:
                continue
            if check__mode == 1:
                # 最后一次修改的时间 (Option 1)
                last = int(os.stat(item_data.path).st_mtime)
            elif check__mode == 2:
                # 最后一次访问的时间 (Option 2)
                last = int(os.stat(item_data.path).st_atime)
            else:
                raise
            if item_data.is_dir() and not is__move__folder or now - last < overdue_time:  # 判断移动条件
                continue
            tasks.append([item_data.name, item_data.path, new__path])
            baroot.set_label1(cfdic['main_progress_label']
                              [lang_num] + item_data.name)
            baroot.progress_root.update_idletasks()
        item_datas.close()
        return tasks

    def run_cleanfile(baroot):
        cf_move_name = ''
        cf_error_name = ''
        baroot.main_progress_bar['value'] = 0
        baroot.progress_root.update_idletasks()
        tasks = get_cf_tasks(baroot)
        task_len = str(len(tasks))
        baroot.main_progress_bar['maximum'] = len(tasks)
        baroot.set_label1(
            f'{cfdic["main_progress_label1"][lang_num][0]}{str(baroot.main_progress_bar["value"])}/{task_len}  {cfdic["main_progress_label1"][lang_num][1]}')
        for task in tasks:
            item = task[0]
            item_path = task[1]
            for_path = task[2]
            baroot.set_label2(cfdic["current_file_label1"]
                              [lang_num] + item.split('\\')[-1])
            for_item = os.path.join(for_path, item)
            if os.path.exists(for_item):
                del_item(for_item)
            if for_path != '':  # 如果 new path 有内容就移动到 new path, 否则删除
                try:
                    shutil_move(item_path, for_path)
                except:
                    cf_error_name += (item + ',  ')
                else:
                    cf_move_name += (item + ',  ')
            else:
                result = del_item(item_path)
                cf_move_name += result[0]
                cf_error_name += result[1]
            baroot.main_progress_bar['value'] += 1
            baroot.set_label1(
                f'{cfdic["main_progress_label1"][lang_num][0]}{str(baroot.main_progress_bar["value"])}/{task_len}  {cfdic["main_progress_label1"][lang_num][1]}')
            baroot.progress_root.update_idletasks()
        baroot.progress_root.withdraw()
        cf_show_notice(old__path, new__path, cf_move_name, cf_error_name)
        baroot.progress_root.withdraw()

    global clean_bar_root, clean_bar_root_task
    if new__path != '' and not os.path.exists(new__path):
        os.mkdir(new__path)
    clean_bar_root = ProgressBar('Movefile  -Syncfile Progress',
                                 cfdic["main_progress_label2"][lang_num],
                                 cfdic["current_file_label"][lang_num],
                                 lang_num)
    clean_bar_root_task = Thread(
        target=lambda: clean_bar_root.launch(), daemon=True)
    clean_bar_root_task.start()
    while not clean_bar_root.initialization_done:
        time.sleep(0.01)
    run_tasks = Thread(
        target=lambda: run_cleanfile(clean_bar_root), daemon=True)
    run_tasks.start()


def cf_autorun_operation():
    """
    The function cf_autorun_operation is used to perform an cleanfile operation automatically.
    """
    cf_file = configparser.ConfigParser()
    cf_file.read(cf_config_path)

    autorun_savings = []
    for cf_name in cf_file.sections():
        if cf_file.get(cf_name, 'autorun') == 'True':
            autorun_savings.append(cf_name)

    for save_name in autorun_savings:
        cf_move_dir(old__path=cf_file.get(save_name, 'old_path'),
                    new__path=cf_file.get(save_name, 'new_path'),
                    pass__file=cf_file.get(
                        save_name, 'pass_filename').split(','),
                    pass__format=cf_file.get(
                        save_name, 'pass_format').split(','),
                    overdue_time=cf_file.getint(save_name, 'set_hour') * 3600,
                    check__mode=cf_file.getint(save_name, 'mode'),
                    is__move__folder=cf_file.get(save_name, 'move_folder'))
        logging.info(
            f'\nAutomatically ran Cleanfile operation as config "{save_name}"')


def sf_sync_dir(path1, path2, single_sync, language_number, area_name=None, pass_file_paths='', pass_folder_paths=''):

    def sf_show_notice(path_1, path_2, sf_error_name):
        mf_icon_path = os.path.join(mf_data_path, r'Movefile.ico')
        sf_notice_title = sfdic["title_p1"][language_number]
        sf_notice_content = sfdic["title_p2_1"][language_number] + path_1 + \
            sfdic["title_p2_2"][language_number] + path_2 + \
            sfdic["title_p2_3"][language_number]
        logging.info("\n" + sf_notice_title + "\n" + sf_notice_content)
        toaster.show_toast(sf_notice_title,
                           sf_notice_content,
                           icon_path=mf_icon_path,
                           duration=10,
                           threaded=False)

        if len(sf_error_name) > 0:
            sf_error_title = sfdic["errtitle"][language_number]
            sf_error_content = sf_error_name + \
                sfdic['can_not_move_notice'][language_number]
            logging.warning("\n" + sf_error_title + "\n" + sf_error_content)
            toaster.show_toast(sf_error_title,
                               sf_error_content,
                               icon_path=mf_icon_path,
                               duration=10,
                               threaded=False)

    def diff_files_in(folderA_path, folderB_path):
        """
        The function takes two folder paths as input and returns the files that are present in one
        folder but not in the other.

        :param folderA_path: The path to the first folder that you want to compare
        :param folderB_path: The path to the second folder that you want to compare
        """

        def all_files_in(item_dir: str, B_side: bool):
            all_files = []
            ort_path, opp_path = folderA_path, folderB_path
            if B_side:
                opp_path, ort_path = ort_path, opp_path
            for itroot, itdirs, itfiles in os.walk(item_dir):
                for itfile in itfiles:
                    itfile_path = os.path.join(itroot, itfile)
                    if ort_path[-1] == '\\':
                        ort_path = ort_path[:-1]
                    opp_file_path = itfile_path.replace(ort_path, opp_path)
                    '''
                    print(itfile_path)
                    print(ort_path + ' | '+ opp_path)
                    print(opp_file_path)
                    print(" ")
                    '''
                    all_files.append([itfile_path, opp_file_path])

            return all_files

        def add_diff_data(index, data_list, r_only=False):
            for item in data_list:
                if r_only and os.path.isdir(os.path.join(folderB_path, item)):
                    diff_data[index].extend(all_files_in(
                        os.path.join(folderB_path, item), True))
                elif os.path.isdir(os.path.join(folderA_path, item)):
                    diff_data[index].extend(all_files_in(
                        os.path.join(folderA_path, item), False))
                elif r_only:
                    diff_data[index].append(
                        [os.path.join(folderB_path, item), os.path.join(folderA_path, item)])
                else:
                    diff_data[index].append(
                        [os.path.join(folderA_path, item), os.path.join(folderB_path, item)])

        diff_data = [[], [], []]
        cmp_data = dircmp(folderA_path, folderB_path, ignore=[])
        add_diff_data(0, cmp_data.diff_files)
        add_diff_data(1, cmp_data.left_only)
        add_diff_data(2, cmp_data.right_only, True)
        """
        print("--------------------------------\n" + folderA_path + "\n" + folderB_path)
        print(cmp_data.diff_files)
        print(cmp_data.left_only)
        print(cmp_data.right_only)
        print("\n")
        """
        for com_dir in cmp_data.common_dirs:
            dir_data = diff_files_in(os.path.join(
                folderA_path, com_dir), os.path.join(folderB_path, com_dir))
            for i in range(3):
                diff_data[i].extend(dir_data[i])
        return diff_data

    def get_task(_bar_root):
        """
        The function "get_task" compares the two folder and decides which file need to be moved or replaced.

        :param _bar_root: The parameter `_bar_root` is likely a variable or object that represents the
        root node or starting point of a tree or hierarchy structure. It could be used to navigate or
        perform operations on the tree or hierarchy
        """
        def judged_task(fileA: str, fileB: str, only_one: bool = False):
            """
            The function `judge_and_append` takes two file names as input and a boolean value indicating
            whether to append the contents of fileB to fileA or not.

            :param fileA: A string representing the path to the first file
            :type fileA: str
            :param fileB: The `fileB` parameter is a string that represents the file name or file path
            of the second file
            :type fileB: str
            """

            if not only_one and int(os.stat(fileA).st_mtime) < int(os.stat(fileB).st_mtime):
                if single_sync:
                    return None
                fileA, fileB = fileB, fileA
            if any(fileB.startswith(p_folder) and p_folder != '' for p_folder in pass_folder_paths.split(',')) or any(
                    fileB == p_file for p_file in pass_file_paths.split(',')):
                return None
            _bar_root.set_label1(
                sfdic['main_progress_label'][language_number] + fileA[0].split('\\')[-1])
            return [fileA, fileB]

        sync_tasks = []  # task items' format: [source_file_path, dest_file_path]
        diff_item_data = diff_files_in(path1, path2)
        for a_only_item in diff_item_data[1]:
            sync_tasks.append(judged_task(
                a_only_item[0], a_only_item[1], True))
        if not single_sync:
            for b_only_item in diff_item_data[2]:
                sync_tasks.append(judged_task(
                    b_only_item[0], b_only_item[1], True))
        for diff_item in diff_item_data[0]:
            sync_tasks.append(judged_task(diff_item[0], diff_item[1]))

        sync_tasks = list(filter(None, sync_tasks))
        return sync_tasks

    def synchronize_files(baroot, task):
        """
        The function `synchronize_files` takes two parameters, `baroot` and `task`, and does some kind of file synchronization operation.

        :param baroot: The `baroot` parameter is a string that represents the root directory of the source files. It is the directory from which the files will be synchronized
        :param task: The `task` parameter is a string that represents the specific task or operation that needs to be performed on the files
        """
        baroot.main_progress_bar['value'] += 0
        baroot.set_label2(
            sfdic["current_file_label1"][language_number] + task[0].split('\\')[-1])
        source_file_path, dest_file_path = task
        dest_path = Path(dest_file_path)
        # Create parent directories if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil_copy2(source_file_path, dest_file_path)
        except shutil_Error:
            return source_file_path
        return None

    def run_sync_tasks(baroot):
        """
        The function "run_sync_tasks" performs synchronous tasks.

        :param baroot: The progress bar root object
        """
        nonlocal sf_progress_done
        sf_error_name = ''
        baroot.main_progress_bar['value'] = 0
        baroot.progress_root.update_idletasks()
        tasks = get_task(baroot)
        baroot.main_progress_bar['maximum'] = len(tasks)
        baroot.set_label1(
            f'{sfdic["main_progress_label1"][language_number][0]}{str(baroot.main_progress_bar["value"])}/{str(len(tasks))}  {sfdic["main_progress_label1"][language_number][1]}')
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(
                synchronize_files, baroot, task) for task in tasks]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    sf_error_name += result + ' , '

                baroot.main_progress_bar['value'] += 1
                baroot.set_label1(
                    f'{sfdic["main_progress_label1"][language_number][0]}{str(baroot.main_progress_bar["value"])}/{str(len(tasks))}  {sfdic["main_progress_label1"][language_number][1]}')
                baroot.progress_root.update_idletasks()

        baroot.progress_root.withdraw()
        path_name_1 = path1.split('\\')[-1]
        if area_name:
            path_name_1 = area_name
        sf_show_notice(path_name_1, path2.split('\\')[-1], sf_error_name)
        baroot.progress_root.destroy()
        sf_progress_done = True

    if path1[-1] != ':' and not os.path.exists(path1):
        os.mkdir(path1)
    if not os.path.exists(path2):
        os.mkdir(path2)
    sync_bar_root = ProgressBar('Movefile  -Syncfile Progress',
                                sfdic["main_progress_label2"][language_number],
                                sfdic["current_file_label"][language_number],
                                language_number)
    sync_bar_root_task = Thread(
        target=lambda: sync_bar_root.launch(), daemon=True)
    sync_bar_root_task.start()
    while not sync_bar_root.initialization_done:
        time.sleep(0.01)
    sf_progress_done = False
    run_tasks = Thread(
        target=lambda: run_sync_tasks(sync_bar_root), daemon=True)
    run_tasks.start()
    while not sf_progress_done:
        time.sleep(1.0)
    sync_bar_root.progress_root_destruction()
    sync_bar_root_task.join()
    run_tasks.join()


def sf_autorun_operation(place, saving_datas=None):
    """
    The function `sf_autorun_operation` performs an sync operation on a given place and optional saving data.

    :param place: The place parameter is a string that represents the location or context in which the
    operation is being performed. It could be a specific folder, directory, or any other relevant
    location
    :param saving_datas: The `saving_datas` parameter is an optional parameter that allows you to pass
    in a dictionary of data that you want to save. If you don't provide a value for this parameter, it
    will default to `None`
    """
    sf_file = configparser.ConfigParser()
    sf_file.read(sf_config_path)
    mf_file = configparser.ConfigParser()
    mf_file.read(os.path.join(mf_data_path, r'Movefile_data.ini'))

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
            sf_sync_dir(path1, path2, single_sync, language_num(mf_file.get('General', 'language')), saving_data[1],
                        lockfile, lockfolder)

    def autorun_local_sf(data_name):
        for saving_data in data_name:
            path1 = sf_file.get(saving_data, 'path_1')
            path2 = sf_file.get(saving_data, 'path_2')
            lockfolder = sf_file.get(saving_data, 'lock_folder')
            lockfile = sf_file.get(saving_data, 'lock_file')
            single_sync = True
            if sf_file.get(saving_data, 'mode') == 'double':
                single_sync = False
            sf_sync_dir(path1, path2, single_sync, language_number=language_num(mf_file.get('General', 'language')),
                        pass_folder_paths=lockfolder, pass_file_paths=lockfile)
            logging.info(
                f'\nAutomatically ran Syncfile operation as config "{data_name}"')

    if place == 'movable':
        autorun_movable_sf(saving_datas)
    elif place == 'local':
        autorun_local_sf(get_sf_startup_savings())


def make_ui(first_visit=False, startup_visit=False):
    """
    The function "make_ui" creates a user interface.

    :param multi_visit: A boolean parameter that indicates whether the user is making more than one visits to the UI today. If set to True, it means the user has already visited the UI before and is returning for
    another visit. If set to False, it means this is the user's first visit to the UI today, defaults to False (optional)
    :param first_visit: A boolean parameter that indicates whether it is the user's first time using this software. If set to True, it means that the user is visiting the UI for the first time, defaults to False (optional)
    :param startup_visit: A boolean parameter that indicates whether it is the first time the user is visiting the application after booting the computer, defaults to False (optional)
    """

    cf_data = configparser.ConfigParser()
    sf_data = configparser.ConfigParser()
    general_data = configparser.ConfigParser()
    general_data.read(os.path.join(mf_data_path, r'Movefile_data.ini'))
    cf_ori_old_path = ''

    def cf_refresh_whitelist_entry():
        nonlocal cf_ori_old_path
        all_ends = []
        file_names = []
        folder_names = []
        item_names = os.scandir(cf_entry_old_path.get())
        if cf_ori_old_path != cf_entry_old_path.get():
            cf_entry_keep_files.delete(0, 'end')
            cf_entry_keep_formats.delete(0, 'end')
            cf_ori_old_path = cf_entry_old_path.get()
        for item in item_names:
            if item.is_file():
                file_end = '.' + item.name.split('.')[-1]
                all_ends.append(file_end)
                file_names.append(item.name)
            elif item.is_dir() and cf_is_folder_move.get():
                folder_names.append(item.name)
        exist_ends = sorted(set(all_ends))

        cf_entry_keep_files.update_values(folder_names + file_names)
        cf_entry_keep_formats.update_values(exist_ends)

        item_names.close()

    def sf_refresh_disk_list(blank_entry=False):
        disk_list = scan_removable_disks()
        if disk_list:
            sf_entry_select_removable['values'] = disk_list
        else:
            sf_entry_select_removable['values'] = [sf_no_disk_text.get()]
            if blank_entry:
                sf_entry_select_removable.delete(0, 'end')

    def select_path(place, ori_content):
        path_ = tkinter.filedialog.askdirectory()
        path_ = path_.replace("/", "\\")
        if path_ != '' and path_ != ori_content:
            if place == 'old':
                source_path.set(path_)
                cf_refresh_whitelist_entry()
            elif place == 'new':
                dest_path.set(path_)
            elif place == '1':
                path_1.set(path_)
            elif place == '2':
                path_2.set(path_)

    def choose_lock_items(mode):
        if mode == 'lockfolder':
            folder_path_ = tkinter.filedialog.askdirectory()
            if folder_path_ != '':
                sf_entry_lock_folder.append_value(
                    folder_path_.replace('/', '\\'))
        elif mode == 'lockfile':
            file_path_ = tkinter.filedialog.askopenfilenames()
            if file_path_ != '':
                for file in file_path_:
                    sf_entry_lock_file.append_value(file.replace('/', '\\'))

    def set_language(lang_number):
        label_choose_state_text.set(
            r_label_text_dic['label_choose_state'][lang_number])
        option_is_cleanfile_text.set(
            r_label_text_dic['option_is_cleanfile'][lang_number])
        option_is_syncfile_text.set(
            r_label_text_dic['option_is_syncfile'][lang_number])
        current_save_name.set(
            r_label_text_dic['current_save_name'][lang_number])
        cf_label_old_path_text.set(
            r_label_text_dic['cf_label_old_path'][lang_number])
        cf_browse_old_path_button_text.set(
            r_label_text_dic['cf_browse_old_path_button'][lang_number])
        cf_browse_new_path_button_text.set(
            r_label_text_dic['cf_browse_new_path_button'][lang_number])
        cf_label_new_path_text.set(
            r_label_text_dic['cf_label_new_path'][lang_number])
        cf_label_move_options_text.set(
            r_label_text_dic['cf_label_move_options'][lang_number])
        cf_option_mode_1_text.set(
            r_label_text_dic['cf_option_mode_1'][lang_number])
        cf_option_mode_2_text.set(
            r_label_text_dic['cf_option_mode_2'][lang_number])
        cf_option_folder_move_text.set(
            r_label_text_dic['cf_option_folder_move'][lang_number])
        cf_label_keep_files_text.set(
            r_label_text_dic['cf_label_keep_files'][lang_number])
        cf_label_keep_formats_text.set(
            r_label_text_dic['cf_label_keep_formats'][lang_number])
        cf_label_time_text.set(r_label_text_dic['cf_label_time'][lang_number])
        cf_label_start_options_text.set(
            r_label_text_dic['cf_label_start_options'][lang_number])
        cf_option_is_auto_text.set(
            r_label_text_dic['cf_option_is_auto'][lang_number])
        sf_label_place_mode_text.set(
            r_label_text_dic['sf_label_place_mode'][lang_number])
        sf_option_mode_usb_text.set(
            r_label_text_dic['sf_option_mode_usb'][lang_number])
        sf_option_mode_local_text.set(
            r_label_text_dic['sf_option_mode_local'][lang_number])
        sf_label_path_1_text.set(
            r_label_text_dic['sf_label_path_1'][lang_number][0])
        sf_label_path_2_text.set(
            r_label_text_dic['sf_label_path_2'][lang_number][0])
        sf_browse_path_1_button_text.set(
            r_label_text_dic['sf_browse_path_1_button'][lang_number])
        sf_browse_path_2_button_text.set(
            r_label_text_dic['sf_browse_path_2_button'][lang_number])
        sf_no_disk_text.set(r_label_text_dic['sf_no_disk'][lang_number])
        sf_label_mode_text.set(r_label_text_dic['sf_label_mode'][lang_number])
        sf_option_mode_double_text.set(
            r_label_text_dic['sf_option_mode_double'][lang_number])
        sf_option_mode_single_text.set(
            r_label_text_dic['sf_option_mode_single'][lang_number])
        sf_label_lock_folder_text.set(
            r_label_text_dic['sf_label_lock_folder'][lang_number])
        sf_browse_lockfolder_button_text.set(
            r_label_text_dic['sf_browse_lockfolder_button'][lang_number])
        sf_label_lock_file_text.set(
            r_label_text_dic['sf_label_lock_file'][lang_number])
        sf_browse_lockfile_button_text.set(
            r_label_text_dic['sf_browse_lockfile_button'][lang_number])
        sf_label_autorun_text.set(
            r_label_text_dic['sf_label_autorun'][lang_number])
        sf_option_autorun_text.set(
            r_label_text_dic['sf_option_autorun'][lang_number])
        select_all_text.set(r_label_text_dic['select_all'][lang_number])

        save_button_text.set(r_label_text_dic['save_button'][lang_number])
        continue_button_text.set(
            r_label_text_dic['continue_button'][lang_number])

        file_menu_text.set(r_label_text_dic['file_menu'][lang_number])
        readfile_menu_text.set(r_label_text_dic['readfile_menu'][lang_number])
        savefile_menu_text.set(r_label_text_dic['savefile_menu'][lang_number])
        exit_menu_text.set(r_label_text_dic['exit_menu'][lang_number])
        option_menu_text.set(r_label_text_dic['option_menu'][lang_number])
        autorun_menu_text.set(r_label_text_dic['autorun_menu'][lang_number])
        desktop_shortcut_text.set(
            r_label_text_dic['desktop_shortcut'][lang_number])
        language_menu_text.set(r_label_text_dic['language_menu'][lang_number])
        help_menu_text.set(r_label_text_dic['help_menu'][lang_number])
        about_menu_text.set(r_label_text_dic['about_menu'][lang_number])
        precautions_menu_text.set(
            r_label_text_dic['precautions_menu'][lang_number])
        cf_keep_menu_text.set(r_label_text_dic['cf_keep_menu'][lang_number])
        cf_expire_menu_text.set(
            r_label_text_dic['cf_expire_menu'][lang_number])
        sf_removable_menu_text.set(
            r_label_text_dic['sf_removable_menu'][lang_number])
        sf_lock_menu_text.set(r_label_text_dic['sf_lock_menu'][lang_number])

        taskbar_setting_text.set(
            r_label_text_dic['taskbar_setting'][lang_number])
        taskbar_exit_text.set(r_label_text_dic['taskbar_exit'][lang_number])

    class Place:
        def __init__(self, mode=None, sf_place=None):
            self.mode = mode
            label_choose_state.grid(row=0, column=0, pady=5, sticky='E')
            blank.grid(row=3, column=1, padx=321, pady=5, sticky='W')
            option_is_cleanfile.grid(
                row=0, column=1, padx=10, pady=5, sticky='W')
            option_is_syncfile.grid(
                row=0, column=1, padx=100, pady=5, sticky='W')
            label_current_save_name.grid(row=0, column=1, padx=10, sticky='E')
            if self.mode == 'cf':
                self.cf_state()
            elif self.mode == 'sf':
                self.sf_state(sf_place)
            self.judge_button_pix()

        @staticmethod
        def sf_change_place_mode(mode):
            if mode == 'movable':
                sf_label_path_1_text.set(
                    r_label_text_dic['sf_label_path_1'][lang_num][0])
                sf_label_path_2_text.set(
                    r_label_text_dic['sf_label_path_2'][lang_num][0])
                sf_option_autorun_text.set(
                    r_label_text_dic['sf_option_autorun'][lang_num][0])
                sf_browse_path_1_button.grid_forget()
                sf_entry_select_removable.grid(
                    row=3, column=1, padx=10, pady=5, ipadx=231, sticky='W')
            else:
                sf_label_path_1_text.set(
                    r_label_text_dic['sf_label_path_1'][lang_num][1])
                sf_label_path_2_text.set(
                    r_label_text_dic['sf_label_path_2'][lang_num][1])
                sf_option_autorun_text.set(
                    r_label_text_dic['sf_option_autorun'][lang_num][1])
                sf_browse_path_1_button.grid(
                    row=3, column=1, ipadx=3, sticky='E', padx=10)
                sf_entry_select_removable.grid_forget()

        @staticmethod
        def judge_button_pix():
            if lang_num == 0:
                save_button.grid(row=8, column=1, ipadx=100,
                                 pady=4, padx=10, sticky='W')
                continue_button.grid(
                    row=8, column=1, ipadx=100, pady=4, padx=10, sticky='E')
                cf_option_mode_2.grid(
                    row=3, column=1, padx=180, ipadx=0, sticky='E')
            elif lang_num == 1:
                save_button.grid(row=8, column=1, ipadx=95,
                                 pady=4, padx=10, sticky='W')
                continue_button.grid(
                    row=8, column=1, ipadx=70, pady=4, padx=10, sticky='E')
                cf_option_mode_2.grid(
                    row=3, column=1, padx=210, ipadx=0, sticky='W')

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

            cf_entry_old_path.grid(
                row=1, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            cf_browse_old_path_button.grid(
                row=1, column=1, ipadx=3, sticky='E', padx=10)
            cf_entry_new_path.grid(
                row=2, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            cf_browse_new_path_button.grid(
                row=2, column=1, ipadx=3, sticky='E', padx=10)
            cf_option_mode_1.grid(
                row=3, column=1, padx=10, ipadx=0, sticky='W')
            cf_option_mode_2.grid(
                row=3, column=1, padx=180, ipadx=0, sticky='W')
            cf_option_folder_move.grid(row=3, column=1, padx=10, sticky='E')
            cf_entry_keep_files.grid(
                row=4, column=1, padx=10, pady=5, ipadx=240, sticky='W')
            cf_entry_keep_formats.grid(
                row=5, column=1, padx=10, pady=5, ipadx=240, sticky='W')
            cf_entry_frame_keep_files.grid(row=4, column=1, sticky='W')
            cf_entry_frame_keep_formats.grid(row=5, column=1, sticky='W')
            cf_entry_time.grid(row=6, column=1, padx=10,
                               pady=5, ipadx=240, sticky='W')
            cf_option_is_auto.grid(row=7, column=1, padx=10, sticky='NW')
            cf_label_old_path.grid(row=1, column=0, pady=5, sticky='E')
            cf_label_new_path.grid(row=2, column=0, pady=5, sticky='E')
            cf_label_move_options.grid(row=3, column=0, pady=5, sticky='E')
            cf_label_keep_files.grid(row=4, column=0, pady=5, sticky='E')
            cf_label_keep_formats.grid(row=5, column=0, sticky='E')
            cf_label_time.grid(row=6, column=0, sticky='E')
            cf_label_start_options.grid(row=7, column=0, sticky='E')

            current_save_name.set(
                r_label_text_dic['current_save_name'][lang_num] + current_cf_save_name.get())

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
            sf_option_mode_usb.grid(
                row=1, column=1, padx=10, pady=5, sticky='W')
            sf_option_mode_local.grid(row=1, column=1, padx=200, sticky='W')
            sf_option_mode_double.grid(
                row=2, column=1, padx=10, ipadx=0, sticky='W')
            sf_option_mode_single.grid(
                row=2, column=1, padx=200, ipadx=0, sticky='W')
            sf_label_mode.grid(row=2, column=0, pady=5, sticky='E')
            sf_label_path_1.grid(row=3, column=0, pady=5, sticky='E')
            sf_label_path_2.grid(row=4, column=0, pady=5, sticky='E')
            sf_entry_path_1.grid(row=3, column=1, padx=10,
                                 pady=5, ipadx=190, sticky='W')
            sf_entry_path_2.grid(row=4, column=1, padx=10,
                                 pady=5, ipadx=190, sticky='W')
            sf_browse_path_2_button.grid(
                row=4, column=1, ipadx=3, sticky='E', padx=10)
            sf_label_lock_folder.grid(row=5, column=0, pady=5, sticky='E')
            sf_entry_frame_lock_folder.grid(row=5, column=1, sticky='W')
            sf_entry_lock_folder.grid(
                row=5, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_browse_lockfolder_button.grid(
                row=5, column=1, padx=10, sticky='E', ipadx=3)
            sf_label_lock_file.grid(row=6, column=0, pady=5, sticky='E')
            sf_entry_frame_lock_file.grid(row=6, column=1, sticky='W')
            sf_entry_lock_file.grid(
                row=6, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_browse_lockfile_button.grid(
                row=6, column=1, padx=10, sticky='E', ipadx=3)
            sf_label_autorun.grid(row=7, column=0, sticky='E')
            sf_option_autorun.grid(row=7, column=1, padx=10, sticky='W')

            current_save_name.set(
                r_label_text_dic['current_save_name'][lang_num] + current_sf_save_name.get())

    global root
    root = tk.Tk()
    if startup_visit:
        root.withdraw()
    root.iconbitmap(os.path.join(mf_data_path, r'Movefile.ico'))
    root.title('Movefile Setting')
    root.geometry("800x287")
    root.resizable(False, False)
    root.attributes('-topmost', True)
    root.attributes('-topmost', False)
    root.update_idletasks()

    current_save_name = tk.StringVar()
    current_cf_save_name = tk.StringVar()
    current_sf_save_name = tk.StringVar()
    source_path = tk.StringVar()
    dest_path = tk.StringVar()
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
    select_all_text = tk.StringVar()

    save_button_text = tk.StringVar()
    continue_button_text = tk.StringVar()
    file_menu_text = tk.StringVar()
    readfile_menu_text = tk.StringVar()
    savefile_menu_text = tk.StringVar()
    exit_menu_text = tk.StringVar()
    option_menu_text = tk.StringVar()
    autorun_menu_text = tk.StringVar()
    desktop_shortcut_text = tk.StringVar()
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

    label_choose_state = ttk.Label(
        root, text=label_choose_state_text.get(), textvariable=label_choose_state_text)
    cf_or_sf = tk.StringVar()
    option_is_cleanfile = ttk.Radiobutton(root, textvariable=option_is_cleanfile_text, variable=cf_or_sf,
                                          value='cf',
                                          command=lambda: Place(cf_or_sf.get()))
    option_is_syncfile = ttk.Radiobutton(root, textvariable=option_is_syncfile_text, variable=cf_or_sf,
                                         value='sf',
                                         command=lambda: Place(cf_or_sf.get()))

    label_current_save_name = ttk.Label(
        root, text=current_save_name.get(), textvariable=current_save_name)

    blank = ttk.Label(root)

    cf_label_old_path = ttk.Label(root, textvariable=cf_label_old_path_text)
    cf_entry_old_path = ttk.Entry(root, textvariable=source_path)
    cf_browse_old_path_button = ttk.Button(root, textvariable=cf_browse_old_path_button_text,
                                           command=lambda: select_path(place='old',
                                                                       ori_content=cf_entry_old_path.get()))

    cf_label_new_path = ttk.Label(root, textvariable=cf_label_new_path_text)
    cf_entry_new_path = ttk.Entry(root, textvariable=dest_path)
    cf_browse_new_path_button = ttk.Button(root, textvariable=cf_browse_new_path_button_text,
                                           command=lambda: select_path(place='new',
                                                                       ori_content=cf_entry_new_path.get()))

    cf_label_move_options = ttk.Label(
        root, textvariable=cf_label_move_options_text)
    cf_entry_mode = tk.IntVar()
    cf_option_mode_1 = ttk.Radiobutton(root, textvariable=cf_option_mode_1_text, variable=cf_entry_mode,
                                       value=1)
    cf_option_mode_2 = ttk.Radiobutton(root, textvariable=cf_option_mode_2_text, variable=cf_entry_mode,
                                       value=2)
    cf_is_folder_move = tk.BooleanVar()
    cf_option_folder_move = ttk.Checkbutton(root, textvariable=cf_option_folder_move_text,
                                            variable=cf_is_folder_move)

    cf_entry_frame_keep_files = tk.Frame(root)
    cf_label_keep_files = ttk.Label(
        root, textvariable=cf_label_keep_files_text)
    cf_entry_keep_files = Combopicker(
        master=cf_entry_frame_keep_files, frameheight=120, allname_textvariable=select_all_text)
    cf_entry_keep_files.bind(
        '<Button-1>', lambda event: cf_refresh_whitelist_entry())

    cf_entry_frame_keep_formats = tk.Frame(root)
    cf_label_keep_formats = ttk.Label(
        root, textvariable=cf_label_keep_formats_text)
    cf_entry_keep_formats = Combopicker(
        master=cf_entry_frame_keep_formats, frameheight=90, allname_textvariable=select_all_text)
    cf_entry_keep_formats.bind(
        '<Button-1>', lambda event: cf_refresh_whitelist_entry())

    cf_label_time = ttk.Label(root, textvariable=cf_label_time_text)
    cf_entry_time = ttk.Entry(root)

    cf_label_start_options = ttk.Label(
        root, textvariable=cf_label_start_options_text)
    cf_is_autorun = tk.BooleanVar()
    cf_option_is_auto = ttk.Checkbutton(
        root, textvariable=cf_option_is_auto_text, variable=cf_is_autorun)

    sf_label_place_mode = ttk.Label(
        root, textvariable=sf_label_place_mode_text)
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

    sf_entry_select_removable = ttk.Combobox(
        root, values=scan_removable_disks(), state='readonly')
    sf_entry_select_removable.bind(
        '<Button-1>', lambda event: sf_refresh_disk_list())

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

    sf_label_lock_folder = ttk.Label(
        root, textvariable=sf_label_lock_folder_text)
    sf_entry_frame_lock_folder = tk.Frame(root)
    sf_entry_lock_folder = Combopicker(
        master=sf_entry_frame_lock_folder, frameheight=90, allname_textvariable=select_all_text)
    sf_browse_lockfolder_button = ttk.Button(root, textvariable=sf_browse_lockfolder_button_text,
                                             command=lambda: choose_lock_items('lockfolder'))

    sf_label_lock_file = ttk.Label(root, textvariable=sf_label_lock_file_text)
    sf_entry_frame_lock_file = tk.Frame(root)
    sf_entry_lock_file = Combopicker(
        master=sf_entry_frame_lock_file, frameheight=50, allname_textvariable=select_all_text)
    sf_browse_lockfile_button = ttk.Button(root, textvariable=sf_browse_lockfile_button_text,
                                           command=lambda: choose_lock_items('lockfile'))

    sf_label_autorun = ttk.Label(root, textvariable=sf_label_autorun_text)
    sf_entry_is_autorun = tk.BooleanVar()
    sf_option_autorun = ttk.Checkbutton(root,
                                        textvariable=sf_option_autorun_text,
                                        variable=sf_entry_is_autorun)

    class MF_Help:
        def __init__(self):
            pass

        def show_help(self, mf_message):
            tkinter.messagebox.showinfo(title='Movefile', message=mf_message)

        def help_main(self):
            self.show_help(help_main_text[lang_num])

        def help_before_use(self):
            self.show_help(help_before_use_text[lang_num])

        def cf_help(self):
            self.show_help(cf_help_text[lang_num])

        def cf_help_keep(self):
            self.show_help(cf_help_keep_text[lang_num])

        def cf_help_timeset(self):
            self.show_help(cf_help_timeset_text[lang_num])

        def sf_help(self):
            self.show_help(sf_help_text[lang_num])

        def sf_removable_help(self):
            self.show_help(sf_removable_help_text[lang_num])

        def sf_lock_help(self):
            self.show_help(sf_lock_help_text[lang_num])

    class MF_Info_Checker:
        def __init__(self):
            pass

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
        def try_create_path(noexist_path):
            if tkinter.messagebox.askokcancel(title="Movefile",
                                              message=r_label_text_dic["path_not_exist_notice"][lang_num] + noexist_path + r_label_text_dic["create_path_notice"][lang_num]):
                try:
                    os.makedirs(noexist_path)
                except:
                    return True
                else:
                    return False
            return None  # if cancelled

        def cf_path_error(self):
            try:
                os.listdir(cf_entry_old_path.get())
                if cf_entry_new_path.get() == '':
                    return False
                if cf_entry_old_path.get() == cf_entry_new_path.get():
                    return 'same_path_error'
                if not os.path.isdir(cf_entry_new_path.get()):
                    return self.try_create_path(cf_entry_new_path.get())
                os.listdir(cf_entry_new_path.get())
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

        def sf_path_error(self):
            has_cancelled = False
            if sf_place_mode.get() == 'movable':  # moveable check
                try:
                    os.listdir(sf_entry_select_removable.get().split(
                        ':')[0][-1] + ':')
                except:
                    return True
            elif not os.path.isdir(sf_entry_path_1.get()):  # local route A check
                result = self.try_create_path(sf_entry_path_1.get())
                if not (result is None):
                    return result
                has_cancelled = True  # passed
            else:
                try:
                    os.listdir(sf_entry_path_1.get())
                except:
                    return True

            if not os.path.isdir(sf_entry_path_2.get()):  # local route B Check
                result = self.try_create_path(sf_entry_path_2.get())
                if has_cancelled or (result is None):
                    return None
                return result
            else:
                try:
                    os.listdir(sf_entry_path_2.get())
                except:
                    return True

            if sf_entry_path_1.get() == sf_entry_path_2.get() and sf_place_mode.get() != 'movable':
                return 'same_path_error'
            elif (sf_entry_path_1.get() in sf_entry_path_2.get() or sf_entry_path_2.get() in sf_entry_path_1.get()) \
                    and sf_place_mode.get() != 'movable':
                return 'in_path_error'
            elif sf_place_mode.get() == 'movable':
                if (sf_entry_select_removable.get().split(':')[0][-1] + ':') in sf_entry_path_2.get():
                    return 'in_disk_path_error'
            return False

        def get_cf_error_state(self):
            cf_path_error_info = self.cf_path_error()
            if not self.cf_is_num():
                tkinter.messagebox.showwarning(
                    'Movefile', r_label_text_dic['num_warning'][lang_num])
                return True
            elif self.cf_has_blank():
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['blank_warning'][lang_num])
                return True
            elif cf_path_error_info == 'same_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=r_label_text_dic['same_path_warning'][lang_num])
                return True
            elif cf_path_error_info is None:
                return True
            elif cf_path_error_info:
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['path_warning'][lang_num])
                return True
            else:
                return False

        def get_sf_error_state(self):
            sf_path_error_info = self.sf_path_error()
            if self.sf_has_blank():
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['blank_warning'][lang_num])
                return True
            elif sf_path_error_info == 'same_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=r_label_text_dic['same_path_warning'][lang_num])
                return True
            elif sf_path_error_info == 'in_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=r_label_text_dic['in_path_warning'][lang_num])
                return True
            elif sf_path_error_info == 'in_disk_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=r_label_text_dic['in_disk_path_warning'][lang_num])
                return True
            elif sf_path_error_info is None:
                return True
            elif sf_path_error_info:
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['path_warning'][lang_num])
                return True
            else:
                return False

    def initial_entry(set_cf_dest=False):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
        default_dest_path = os.path.join(desktop_path, r'Previous Files')
        if not cf_entry_old_path.get():
            cf_entry_old_path.insert(0, desktop_path)
            cf_refresh_whitelist_entry()
        if set_cf_dest and not cf_entry_new_path.get():
            cf_entry_new_path.insert(0, default_dest_path)
        if not cf_entry_mode.get():
            cf_entry_mode.set(1)
        if not cf_entry_time.get():
            cf_entry_time.insert(0, '0')
        if not sf_entry_mode.get():
            sf_entry_mode.set('double')

    def ask_save_name():
        global ask_name_window
        last_saving_data, cf_save_names, sf_save_names = list_saving_data()

        def remove_last_edit(mode_data: configparser.ConfigParser, config_file_path):
            if not mode_data.sections():  # 更改上次修改项
                return
            for save_name in mode_data.sections():
                try:
                    mode_data.set(save_name, '_last_edit_', 'False')
                    mode_data.write(
                        open(config_file_path, 'w+', encoding='ANSI'))
                except:
                    logging.info(f'remove_last_edit error: {save_name}')

        def savefile(function, save_name='New_Setting'):  # 保存文件
            cf_data.read(cf_config_path)
            sf_data.read(sf_config_path)

            if function == 'cf':  # 如果当前界面为cf
                remove_last_edit(cf_data, cf_config_path)
                if not os.path.exists(cf_config_path):
                    file = open(cf_config_path,
                                'w', encoding='ANSI')
                    file.close()
                cf_data.read(cf_config_path)
                if not cf_data.has_section(str(save_name)):
                    cf_data.add_section(str(save_name))
                cf_data.set(save_name, '_last_edit_', 'True')
                cf_data.set(save_name, "old_path", cf_entry_old_path.get())
                cf_data.set(save_name, "new_path", cf_entry_new_path.get())
                cf_data.set(save_name, "pass_filename",
                            cf_entry_keep_files.get())
                cf_data.set(save_name, "pass_format",
                            cf_entry_keep_formats.get())
                cf_data.set(save_name, "set_hour", cf_entry_time.get())
                cf_data.set(save_name, "mode", str(cf_entry_mode.get()))
                cf_data.set(save_name, "autorun", str(cf_is_autorun.get()))
                cf_data.set(save_name, "move_folder",
                            str(cf_is_folder_move.get()))
                cf_data.write(
                    open(cf_config_path, "w+", encoding='ANSI'))

            elif function == 'sf':  # 如果当前界面为sf
                remove_last_edit(sf_data, sf_config_path)
                if not os.path.exists(sf_config_path):
                    file = open(sf_config_path,
                                'w', encoding='ANSI')
                    file.close()
                sf_data.read(sf_config_path)
                if not sf_data.has_section(str(save_name)):
                    sf_data.add_section(str(save_name))
                sf_data.set(save_name, '_last_edit_', 'True')
                sf_data.set(save_name, 'place_mode', sf_place_mode.get())
                if sf_place_mode.get() == 'local':
                    sf_data.set(save_name, 'path_1', sf_entry_path_1.get())
                else:
                    disk_data = sf_entry_select_removable.get()
                    sf_data.set(save_name, 'disk_number',
                                str(GetVolumeInformation(disk_data.split(':')[0][-1] + ':')[1]))
                sf_data.set(save_name, 'path_2', sf_entry_path_2.get())
                sf_data.set(save_name, 'mode', sf_entry_mode.get())
                sf_data.set(save_name, 'lock_folder',
                            sf_entry_lock_folder.get())
                sf_data.set(save_name, 'lock_file', sf_entry_lock_file.get())
                sf_data.set(save_name, 'autorun', str(
                    sf_entry_is_autorun.get()))
                sf_data.write(
                    open(sf_config_path, 'w+', encoding='ANSI'))

            tkinter.messagebox.showinfo(title=r_label_text_dic['succ_save'][lang_num][0],
                                        message=r_label_text_dic['succ_save'][lang_num][1])
            continue_button.config(state=tk.NORMAL)

        def sure_save():
            ask_name_window.withdraw()
            savefile(function=cf_or_sf.get(), save_name=name_entry.get())
            log_function = 'Syncfile'
            if cf_or_sf.get() == 'cf':
                log_function = 'Cleanfile'
            logging.info(
                f"\nA config file of {log_function} named {name_entry.get()} is saved")
            current_save_name.set(
                r_label_text_dic['current_save_name'][lang_num] + name_entry.get())
            exit_asn()

        def exit_asn():
            ask_name_window.destroy()

        mode = cf_or_sf.get()
        current_mode_savings = []
        if mode == 'cf':
            error_state = root_info_checker.get_cf_error_state()
            current_mode_savings = cf_save_names
        elif mode == 'sf':
            error_state = root_info_checker.get_sf_error_state()
            current_mode_savings = sf_save_names
        else:
            error_state = True

        if not error_state:
            ask_name_window = tk.Toplevel(root)
            ask_name_window.iconbitmap(
                os.path.join(mf_data_path, r'Movefile.ico'))
            ask_name_window.geometry('400x35')
            ask_name_window.title(
                r_label_text_dic['ask_name_window'][lang_num])
            ask_name_window.focus_force()
            autofill_name = 'New_Setting'
            if mode == 'cf' and current_cf_save_name.get() != '':
                autofill_name = current_cf_save_name.get()
            elif mode == 'sf' and current_sf_save_name.get() != '':
                autofill_name = current_sf_save_name.get()
            elif last_saving_data != ['', '', '']:
                if last_saving_data[0] == mode:
                    autofill_name = last_saving_data[1]
                else:
                    autofill_name = last_saving_data[2]
            name_label = ttk.Label(
                ask_name_window, text=r_label_text_dic['name_label'][lang_num])
            name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')

            name_entry = ttk.Combobox(
                ask_name_window, values=current_mode_savings)
            name_entry.insert(0, autofill_name)
            name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='W')
            sure_name_button = ttk.Button(ask_name_window, text=r_label_text_dic['sure_name_button'][lang_num],
                                          command=lambda: sure_save())
            sure_name_button.grid(row=0, column=2, sticky='W')
            ask_name_window.bind('<Return>', lambda event: sure_save())
            ask_name_window.protocol('WM_DELETE_WINDOW', exit_asn)

    def read_saving(ask_path=False):
        global ask_saving_root
        cf_file = configparser.ConfigParser()
        cf_file.read(cf_config_path)  # 获取配置文件
        sf_file = configparser.ConfigParser()
        sf_file.read(sf_config_path)
        new_values = []

        last_data = list_saving_data()[0]
        cf_save_name = last_data[1]
        sf_save_name = last_data[2]

        def open_cf_saving(setting_name):
            if setting_name == '':
                return
            if not cf_file.has_section(setting_name):
                return
            nonlocal cf_ori_old_path
            if cf_entry_old_path.get() != '':
                cf_entry_old_path.delete(0, 'end')
            if cf_entry_new_path.get() != '':
                cf_entry_new_path.delete(0, 'end')
            cf_entry_old_path.insert(0, cf_file.get(
                setting_name, 'old_path'))  # 旧文件夹
            cf_ori_old_path = cf_entry_old_path.get()
            cf_entry_new_path.insert(0, cf_file.get(
                setting_name, 'new_path'))  # 新文件夹
            cf_refresh_whitelist_entry()
            if cf_entry_keep_files.get() != '':
                cf_entry_keep_files.delete(0, 'end')
            if cf_entry_keep_formats.get() != '':
                cf_entry_keep_formats.delete(0, 'end')
            if cf_entry_time.get() != '':
                cf_entry_time.delete(0, 'end')
            for file in cf_file.get(setting_name, 'pass_filename').split(','):
                if file != '':
                    cf_entry_keep_files.append_value(file)  # 设置跳过白名单
            for format in cf_file.get(setting_name, 'pass_format').split(','):
                if format != '':
                    cf_entry_keep_formats.append_value(format)  # 设置跳过格式
            cf_entry_time.insert(0, cf_file.get(
                setting_name, 'set_hour'))  # 设置过期时间(hour)
            cf_entry_mode.set(cf_file.getint(setting_name, 'mode'))  # 设置判断模式
            cf_is_autorun.set(cf_file.get(setting_name, 'autorun') == 'True')
            cf_is_folder_move.set(cf_file.get(
                setting_name, 'move_folder') == 'True')
            Place('cf')
            cf_or_sf.set('cf')
            current_cf_save_name.set(setting_name)
            current_save_name.set(
                r_label_text_dic['current_save_name'][lang_num] + setting_name)
            root_info_checker.get_cf_error_state()

        def open_sf_saving(setting_name):
            if setting_name == '':
                return
            if not sf_file.has_section(setting_name):
                return

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
                sf_refresh_disk_list()
                time.sleep(0.1)
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
            for folder in sf_file.get(setting_name, 'lock_folder').split(','):
                if folder != '':
                    sf_entry_lock_folder.append_value(folder)
            for file in sf_file.get(setting_name, 'lock_file').split(','):
                if file != '':
                    sf_entry_lock_file.append_value(file)
            sf_entry_is_autorun.set(sf_file.get(
                setting_name, 'autorun') == 'True')
            Place('sf', place_mode)
            cf_or_sf.set('sf')
            current_sf_save_name.set(setting_name)
            current_save_name.set(
                r_label_text_dic['current_save_name'][lang_num] + setting_name)
            root_info_checker.get_sf_error_state()

        def refresh_saving():
            nonlocal new_values
            try:
                last_saving_data, cf_save_names, sf_save_names = list_saving_data()
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
            is_continue = tkinter.messagebox.askyesno(
                title='Movefile', message='确认删除配置 ' + del_name + ' ?')
            ini_file = configparser.ConfigParser()
            if del_mode in ['清理文件(Cleanfile)', 'Cleanfile'] and is_continue:
                ini_file.read(cf_config_path)
                ini_file.remove_section(del_name)
                ini_file.write(
                    open(cf_config_path, 'w+', encoding='ANSI'))
                logging.info(
                    f"\nA config file of Cleanfile named {del_name} is deleted")
            elif del_mode in ['同步文件(Syncfile)', 'Syncfile'] and is_continue:
                ini_file.read(sf_config_path)
                ini_file.remove_section(del_name)
                ini_file.write(
                    open(sf_config_path, 'w+', encoding='ANSI'))
                logging.info(
                    f"\nA config file of Syncfile named {del_name} is deleted")
            exit_asr()

        def sure_open():
            saving_name = read_name_entry.get()
            if read_mode_entry.get() in ['清理文件(Cleanfile)', 'Cleanfile']:
                open_cf_saving(saving_name)
            elif read_mode_entry.get() in ['同步文件(Syncfile)', 'Syncfile']:
                open_sf_saving(saving_name)
            current_save_name.set(
                r_label_text_dic['current_save_name'][lang_num] + saving_name)
            exit_asr()

        def exit_asr():
            ask_saving_root.destroy()

        if ask_path:
            ask_saving_root = tk.Toplevel(root)
            ask_saving_root.iconbitmap(
                os.path.join(mf_data_path, r'Movefile.ico'))
            if lang_num == 0:
                ask_saving_root.geometry('680x35')
            elif lang_num == 1:
                ask_saving_root.geometry('700x35')
            ask_saving_root.title(r_label_text_dic['readfile_menu'][lang_num])
            ask_saving_root.focus_force()
            last_edit_mode = ''
            last_edit_name = ''
            save_names = []
            last_saving_data = list_saving_data()[0]
            if last_saving_data:
                last_edit_mode = last_saving_data[0]
                last_edit_name = last_saving_data[1]
            read_name_label = ttk.Label(
                ask_saving_root, text=r_label_text_dic['read_name_label'][lang_num])
            read_name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')
            read_mode_entry = ttk.Combobox(ask_saving_root, values=r_label_text_dic['read_mode_entry'][lang_num],
                                           state='readonly')
            read_mode_entry.grid(row=0, column=1, pady=5, padx=5)
            if last_edit_mode == 'sf':
                read_mode_entry.current(1)
            elif last_edit_mode == 'cf':
                read_mode_entry.current(0)
            read_name_entry = ttk.Combobox(
                ask_saving_root, values=save_names, state='readonly')
            refresh_saving()
            for save_index, name in enumerate(new_values):
                if name == last_edit_name:
                    read_name_entry.current(save_index)
            read_name_entry.grid(row=0, column=2, padx=5,
                                 pady=5, ipadx=20, sticky='W')
            del_save_button = ttk.Button(ask_saving_root, text=r_label_text_dic['del_save_button'][lang_num],
                                         command=lambda: del_saving())
            del_save_button.grid(row=0, column=3, padx=5, pady=5)
            sure_name_bottom = ttk.Button(ask_saving_root, text=r_label_text_dic['sure_name_bottom'][lang_num],
                                          command=lambda: sure_open())
            sure_name_bottom.grid(row=0, column=4, pady=5)
            read_mode_entry.bind('<<ComboboxSelected>>',
                                 lambda event: refresh_saving())
            ask_saving_root.bind('<Return>', lambda event: sure_open())
            ask_saving_root.protocol('WM_DELETE_WINDOW', exit_asr)
        else:
            open_sf_saving(sf_save_name)
            open_cf_saving(cf_save_name)

        initial_entry(set_cf_dest=cf_save_name == '')

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
        if path1[-1] == ":":
            area_name = GetVolumeInformation(path1)[0]
        if mode == 'single':
            single_sync = True
        else:
            single_sync = False
        sf_sync_dir(path1, path2, single_sync, lang_num,
                    area_name, lockfile, lockfolder)

    def change_language(language):
        nonlocal lang_num
        general_data.set('General', 'language', language)
        general_data.write(
            open(os.path.join(mf_data_path, r'Movefile_data.ini'), "w+", encoding='ANSI'))
        lang_num = language_num(language)
        set_language(lang_num)
        Place(cf_or_sf.get(), sf_place_mode.get())
        tkinter.messagebox.showinfo(
            title='Movefile', message=r_label_text_dic['change_language'][lang_num])

    def continue_going():
        if cf_or_sf.get() == 'cf' and not root_info_checker.get_cf_error_state():
            cf_operator = Thread(
                target=lambda: cf_operate_from_root(), daemon=True)
            cf_operator.start()
            root.withdraw()
        elif cf_or_sf.get() == 'sf' and not root_info_checker.get_sf_error_state():
            sf_operator = Thread(
                target=lambda: sf_operate_from_root(), daemon=True)
            sf_operator.start()
            root.withdraw()

    # @atexit.register
    def exit_program():
        global program_finished
        program_finished = True
        root.withdraw()
        toaster.stop_notification_thread()
        if 'clean_bar_root' in globals().keys():
            clean_bar_root.progress_root_destruction()
            clean_bar_root_task.join()
        if 'ask_saving_root' in globals().keys():
            ask_saving_root.quit()
            ask_saving_root.destroy()
        if 'ask_name_window' in globals().keys():
            ask_name_window.quit()
            ask_name_window.destroy()

        task_menu.stop()
        root.quit()
        root.destroy()

        logging.info("\nMovefile Quit\n")
        butt_icon.join()
        ask_permit.join()
        background_detect.join()

    # 创建按键
    blank_pix = ttk.Label(root, text=' ')
    blank_pix.grid(row=8, column=0, ipadx=67, pady=4, padx=0, sticky='E')
    save_button = ttk.Button(
        root, textvariable=save_button_text, command=lambda: ask_save_name())
    continue_button = ttk.Button(
        root, textvariable=continue_button_text, command=lambda: continue_going())
    continue_button.config(state=tk.DISABLED)

    # 菜单栏
    main_menu = tk.Menu(root)
    file_menu = tk.Menu(main_menu, tearoff=False)
    file_menu.add_command(label=readfile_menu_text.get(), command=lambda: read_saving(ask_path=True),
                          accelerator="Ctrl+O")
    file_menu.add_command(label=savefile_menu_text.get(
    ), command=lambda: ask_save_name(), accelerator="Ctrl+S")
    file_menu.add_separator()
    file_menu.add_command(label=exit_menu_text.get(),
                          command=lambda: exit_program())

    option_menu = tk.Menu(main_menu, tearoff=False)
    is_startup_run = tk.BooleanVar()
    is_startup_run.set(general_data.get('General', 'autorun') == "True")
    is_desktop_shortcut = tk.BooleanVar()
    is_desktop_shortcut.set(general_data.get(
        'General', 'desktop_shortcut') == "True")
    option_menu.add_checkbutton(label=autorun_menu_text.get(), variable=is_startup_run,
                                command=lambda: set_startup(is_startup_run.get(), lang_num))
    option_menu.add_checkbutton(label=desktop_shortcut_text.get(
    ), variable=is_desktop_shortcut, command=lambda: put_desktop_shortcut(is_desktop_shortcut.get(), lang_num))

    language_menu = tk.Menu(main_menu, tearoff=False)
    language_menu.add_radiobutton(label='简体中文', variable=root_language, value='Chinese',
                                  command=lambda: change_language('Chinese'))
    language_menu.add_radiobutton(label='English', variable=root_language, value='English',
                                  command=lambda: change_language('English'))

    help_shower = MF_Help()
    help_menu = tk.Menu(main_menu, tearoff=False)
    help_menu.add_command(label=about_menu_text.get(),
                          command=help_shower.help_main)
    help_menu.add_command(label=precautions_menu_text.get(),
                          command=help_shower.help_before_use)
    help_menu.add_separator()
    help_menu.add_command(label='Cleanfile', command=help_shower.cf_help)
    help_menu.add_command(label=cf_keep_menu_text.get(),
                          command=help_shower.cf_help_keep)
    help_menu.add_command(label=cf_expire_menu_text.get(),
                          command=help_shower.cf_help_timeset)
    help_menu.add_separator()
    help_menu.add_command(label='Syncfile', command=help_shower.sf_help)
    help_menu.add_command(label=sf_removable_menu_text.get(),
                          command=help_shower.sf_removable_help)
    help_menu.add_command(label=sf_lock_menu_text.get(),
                          command=help_shower.sf_lock_help)

    main_menu.add_cascade(label=file_menu_text.get(), menu=file_menu)
    main_menu.add_cascade(label=option_menu_text.get(), menu=option_menu)
    main_menu.add_cascade(label=language_menu_text.get(), menu=language_menu)
    main_menu.add_cascade(label=help_menu_text.get(), menu=help_menu)
    root.config(menu=main_menu)

    # 托盘菜单
    menu = (
        MenuItem(taskbar_setting_text.get(),
                 lambda event: root.deiconify(), default=True), Menu.SEPARATOR,
        MenuItem(taskbar_exit_text.get(), action=lambda: exit_program()))
    image = Image.open(os.path.join(mf_data_path, r'Movefile.ico'))
    task_menu = Icon("icon", image, "Movefile", menu)

    root.bind("<Control-o>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-O>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-s>", lambda event: ask_save_name())
    root.bind("<Control-S>", lambda event: ask_save_name())
    # root.bind('<Button-1>'), lambda: sf_refresh_disk_list(none_disk=True)

    root_info_checker = MF_Info_Checker()

    root.protocol('WM_DELETE_WINDOW', root.withdraw)
    # 重新定义点击关闭按钮的处理

    def get_movable_autorun_ids():
        sf_dat = configparser.ConfigParser()
        sf_dat.read(sf_config_path)
        savings = sf_dat.sections()
        autorun_ids = []
        for saving in savings:
            if sf_dat.get(saving, 'place_mode') == 'movable' and sf_dat.get(saving, 'autorun') == 'True':
                autorun_ids.append([sf_dat.get(saving, 'disk_number'), saving])
        return autorun_ids

    def ask_sync_disk():
        """
        The function "ask_sync_disk" is used to prompt the user to input whether they want to
        synchronize their disk.
        """
        while not program_finished:
            run_list = []
            for new_area_data in new_areas_data:
                for autorun_id in get_movable_autorun_ids():
                    msg_ps = sfdic['new_disk_detected'][lang_num]
                    msg_content = f'{msg_ps[0]}{new_area_data[1]} ({new_area_data[0][:-1]}){msg_ps[1]}{msg_ps[2]}{autorun_id[1]}{msg_ps[3]}'
                    if str(new_area_data[2]) == autorun_id[0] and tkinter.messagebox.askokcancel(title='Movefile',
                                                                                                 message=msg_content):
                        run_list.append(
                            [new_area_data[0], new_area_data[1], autorun_id[1]])
                new_areas_data.remove(new_area_data)
            if run_list:
                sf_autorun_operation('movable', run_list)
            time.sleep(1)

    if first_visit:
        initial_entry(set_cf_dest=True)
        cf_or_sf.set('cf')
        Place('cf')
        help_shower.help_main()
        help_shower.help_before_use()
    else:
        read_saving()
        cf_refresh_whitelist_entry()
        continue_button.config(state=tk.NORMAL)
        if cf_or_sf.get() == '':
            cf_or_sf.set('cf')
            Place('cf')

    butt_icon = Thread(target=task_menu.run, daemon=True)
    butt_icon.start()
    background_detect = Thread(
        target=lambda: detect_removable_disks_thread(), daemon=True)
    background_detect.start()
    ask_permit = Thread(target=lambda: ask_sync_disk(), daemon=True)
    ask_permit.start()

    root.mainloop()


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

    if visits_today == 1 and boot_visit:
        autorun_options = Thread(
            target=lambda: startup_autorun(), daemon=True)
        autorun_options.start()

    make_ui(first_visit=first_visit, startup_visit=boot_visit)


if __name__ == '__main__':
    main()
