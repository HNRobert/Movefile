# -*- coding: utf-8 -*-
"""
If you have any suggestion for optimizing this program,
it's welcomed to submit that to the author.

Created on Wed Dec 21 17:07:30 2022

@author: Robert He
QQ: 2567466856
GitHub address: https://github.com/HNRobert/Movefile
"""

import base64
import configparser
import logging
import os
import time
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
import winreg
from ctypes import windll
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from shutil import copy2 as shutil_copy2, move as shutil_move, Error as shutil_Error
from threading import Thread

from filecmp import dircmp
from PIL import Image
from mttkinter import mtTkinter as tk
from pathlib import Path
from psutil import disk_partitions, pids, boot_time as psutil_boot_time
from pystray import MenuItem, Menu, Icon
from win32api import GetVolumeInformation
from win32com.client import Dispatch
from win32gui import FindWindow, ShowWindow
from win10toast import ToastNotifier
from winshell import CreateShortcut

import Movefile_icon as icon
from ComBoPicker import Combopicker
from LT_Dic import vision


class Initialization:
    def __init__(self):
        self.boot_time = self.get_boot_time()
        self.roaming_path = None
        self.set_data_path()

        self.mf_data = configparser.ConfigParser()
        self.mf_data.read(os.path.join(mf_data_path, r'Movefile_data.ini'))

        self.log_file_path = os.path.join(mf_data_path, r'Movefile.log')
        self.set_log_writer()

        self.mf_ico = None
        if not os.path.exists(os.path.join(mf_data_path, r'Movefile.ico')):
            self.load_icon()

        self.ask_time_today = 0
        self.asktime_plus()

        self.first_visit = False
        if list_saving_data() == ['', '', '']:  # 判断是否为首次访问
            self.first_visit = True
            logging.info("This is the first visit of this program.")

    def get_system_uptime(self):
        # Call the GetTickCount64 function from the kernel32 library
        tick_count = windll.kernel32.GetTickCount64()
        # Calculate the uptime in seconds
        uptime_seconds = tick_count / 1000.0
        return uptime_seconds        

    def get_boot_time(self):
        boot_t = psutil_boot_time()
        boot_time_obj = datetime.fromtimestamp(boot_t)
        now_time = datetime.now()
        delta_time = now_time - boot_time_obj
        time_since_boot = delta_time.days * 3600 * 24 + delta_time.seconds
        return time_since_boot

    def set_data_path(self):
        """
        The function globalize the route where previous data of this program can be found.
        """

        global mf_data_path, cf_data_path, cf_config_path, sf_data_path, sf_config_path, toaster
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

        if 'Movefile' not in os.listdir(self.roaming_path):
            os.mkdir(mf_data_path)
            time.sleep(0.5)
        if 'Cleanfile' not in os.listdir(mf_data_path):
            os.mkdir(cf_data_path)
        if 'Syncfile' not in os.listdir(mf_data_path):
            os.mkdir(sf_data_path)

    def asktime_plus(self):
        """
        The function "asktime_plus" is not defined in the code provided.
        """

        time_now = datetime.today()
        date = str(time_now.date())

        if not os.path.exists(os.path.join(mf_data_path, r'Movefile_data.ini')):  # 创建配置文件
            file = open(os.path.join(mf_data_path, r'Movefile_data.ini'),
                        'w', encoding="ANSI")
            file.close()

        if not self.mf_data.has_section("General"):
            self.mf_data.add_section("General")

        if not self.mf_data.has_section("General") or self.mf_data.get("General", "date") != str(date):
            self.ask_time_today = 1
            self.mf_data.set("General", "date", date)
            self.mf_data.set("General", "asktime_today", '1')
        else:
            self.ask_time_today = self.mf_data.getint(
                "General", "asktime_today") + 1
            self.mf_data.set("General", "asktime_today",
                             str(self.ask_time_today))

        if not self.mf_data.has_option('General', 'language'):
            import ctypes
            dll_handle = ctypes.windll.kernel32
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
            roaming_path, r"\Microsoft\Windows\Start Menu\Programs\StartUp")

        if not os.path.exists(os.path.join(desktop_path, r"Movefile.lnk")):
            self.mf_data.set('General', 'desktop_path', 'False')
        if not os.path.exists(os.path.join(startup_path, r"Movefile.lnk")):
            self.mf_data.set('General', 'autorun', 'False')

        self.mf_data.write(
            open(os.path.join(mf_data_path, r'Movefile_data.ini'), "w+", encoding='ANSI'))

    def load_icon(self):
        self.mf_ico = open(os.path.join(mf_data_path, r'Movefile.ico'), 'wb')
        self.mf_ico.write(base64.b64decode(icon.Movefile_ico))
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
        from LT_Dic import progress_root_label_dic
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
        if self.opened_proc_root():
            self.continue_this_progress = False

    def opened_proc_root(self):
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
    pile = 0
    while "root" not in globals().keys() and pile < 100:
        time.sleep(0.1)
        pile += 1
    if pile < 100:
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
    from LT_Dic import lnk_desc
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
            Description=desc)
    else:
        gen_cf.set('General', 'autorun', 'False')
    gen_cf.write(
        open(os.path.join(mf_data_path, r'Movefile_data.ini'), "w+", encoding='ANSI'))


def put_desktop_shortcut(state=True, lang_n=0):
    """
    The function `put_desktop_shortcut` allows you to put the shortcut of this program into Windows Start Menu.

    :param state: The state parameter is a boolean value that determines whether the start menu should be displayed or not. If state is set to True, the start menu will be displayed. If state is set to False, the start menu will not be displayed, defaults to True (optional)
    :param lang_n: The `lang_n` parameter is used to specify the language for the start menu. It is an integer value that represents the language code, defaults to 1 (optional)
    """
    from LT_Dic import lnk_desc
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
    global last_saving_data, all_save_names, cf_save_names, sf_save_names
    cf_file = configparser.ConfigParser()
    cf_file.read(cf_config_path)
    cf_save_names = cf_file.sections()
    sf_file = configparser.ConfigParser()
    sf_file.read(sf_config_path)
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
            cf.read(cf_config_path)  # 获取配置文件
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
            cf.read(sf_config_path)
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
                    return [pair[1]]
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
    while True:
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
        time.sleep(2)


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

    from LT_Dic import cf_label_text_dic as cfdic
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
    for cf_name in cf_save_names:
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
            f'Automatically ran Cleanfile operation as config "{save_name}"')


def sf_sync_dir(path1, path2, single_sync, language_number, area_name=None, pass_file_paths='', pass_folder_paths=''):
    from LT_Dic import sf_label_text_dic as sf_ltd

    def sf_show_notice(path_1, path_2, sf_error_name):
        mf_icon_path = os.path.join(mf_data_path, r'Movefile.ico')
        sf_notice_title = sf_ltd["title_p1"][language_number]
        sf_notice_content = sf_ltd["title_p2_1"][language_number] + path_1 + \
            sf_ltd["title_p2_2"][language_number] + path_2 + \
            sf_ltd["title_p2_3"][language_number]
        logging.info("\n" + sf_notice_title + "\n" + sf_notice_content)
        toaster.show_toast(sf_notice_title,
                           sf_notice_content,
                           icon_path=mf_icon_path,
                           duration=10,
                           threaded=False)

        if len(sf_error_name) > 0:
            sf_error_title = sf_ltd["errtitle"][language_number]
            sf_error_content = sf_error_name + \
                sf_ltd['can_not_move_notice'][language_number]
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
        cmp_data = dircmp(folderA_path, folderB_path)
        add_diff_data(0, cmp_data.diff_files)
        add_diff_data(1, cmp_data.left_only)
        add_diff_data(2, cmp_data.right_only, True)
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
        def judge_and_append_task(fileA: str, fileB: str, direct_apd: bool):
            """
            The function `judge_and_append` takes two file names as input and a boolean value indicating
            whether to append the contents of fileB to fileA or not.

            :param fileA: A string representing the path to the first file
            :type fileA: str
            :param fileB: The `fileB` parameter is a string that represents the file name or file path
            of the second file
            :type fileB: str
            :param direct_apd: The `direct_apd` parameter is a boolean value that determines whether the
            contents of `fileB` should be directly appended to `fileA` or if a judgment should be made
            before appending
            :type direct_apd: bool
            """
            if int(os.stat(fileA).st_mtime) < int(os.stat(fileB).st_mtime):
                if single_sync:
                    return
                fileA, fileB = fileB, fileA
            if any(fileB.startswith(p_folder) and p_folder for p_folder in pass_folder_paths.split(',')) or any(
                    fileB == p_file for p_file in pass_file_paths.split(',')):
                return
            sync_tasks.append([fileA, fileB, direct_apd])
            _bar_root.set_label1(
                sf_ltd['main_progress_label'][language_number] + fileA[0].split('\\')[-1])

        sync_tasks = []
        diff_item_data = diff_files_in(path1, path2)
        for a_only_item in diff_item_data[1]:
            sync_tasks.append([a_only_item[0], a_only_item[1], True])
            _bar_root.set_label1(
                sf_ltd['main_progress_label'][language_number] + a_only_item[0].split('\\')[-1])
        if not single_sync:
            for b_only_item in diff_item_data[2]:
                sync_tasks.append([b_only_item[0], b_only_item[1], True])
                _bar_root.set_label1(
                    sf_ltd['main_progress_label'][language_number] + b_only_item[1].split('\\')[-1])
        for diff_item in diff_item_data[0]:
            judge_and_append_task(diff_item[0], diff_item[1], False)

        return sync_tasks

    def synchronize_files(baroot, task):
        """
        The function `synchronize_files` takes two parameters, `baroot` and `task`, and does some kind of file synchronization operation.

        :param baroot: The `baroot` parameter is a string that represents the root directory of the source files. It is the directory from which the files will be synchronized
        :param task: The `task` parameter is a string that represents the specific task or operation that needs to be performed on the files
        """
        baroot.main_progress_bar['value'] += 0
        baroot.set_label2(
            sf_ltd["current_file_label1"][language_number] + task[0].split('\\')[-1])
        source_file_path, dest_file_path, create_folder = task
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
            f'{sf_ltd["main_progress_label1"][language_number][0]}{str(baroot.main_progress_bar["value"])}/{str(len(tasks))}  {sf_ltd["main_progress_label1"][language_number][1]}')
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(
                synchronize_files, baroot, task) for task in tasks]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    sf_error_name += result + ' , '

                baroot.main_progress_bar['value'] += 1
                baroot.set_label1(
                    f'{sf_ltd["main_progress_label1"][language_number][0]}{str(baroot.main_progress_bar["value"])}/{str(len(tasks))}  {sf_ltd["main_progress_label1"][language_number][1]}')
                baroot.progress_root.update_idletasks()

        baroot.progress_root.withdraw()
        path_name_1 = path1.split('\\')[-1]
        if area_name:
            path_name_1 = area_name
        sf_show_notice(path_name_1, path2.split('\\')[-1], sf_error_name)
        baroot.progress_root.destroy()
        sf_progress_done = True

    sync_bar_root = ProgressBar('Movefile  -Syncfile Progress',
                                sf_ltd["main_progress_label2"][language_number],
                                sf_ltd["current_file_label"][language_number],
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
                f'Automatically ran Syncfile operation as config "{data_name}"')

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

    from LT_Dic import r_label_text_dic
    cf_data = configparser.ConfigParser()
    sf_data = configparser.ConfigParser()
    general_data = configparser.ConfigParser()
    general_data.read(os.path.join(mf_data_path, r'Movefile_data.ini'))
    normal_paused = False
    cf_ori_old_path = ''

    def cf_refresh_whitelist_entry():
        def update_values(values_in: list, entry_in: Combopicker, ):
            entry_in.values = values_in
            previous_values = entry_in.get().split(',')
            result = ''
            for pre_value in previous_values:
                if pre_value in values_in:
                    result += pre_value + ','
            entry_in.delete(0, 'end')
            entry_in.insert(0, result)

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

        update_values(['全选'] + folder_names + file_names, cf_entry_keep_files)
        update_values(['全选'] + exist_ends, cf_entry_keep_formats)

        item_names.close()

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
                sf_entry_lock_folder.values.append(
                    folder_path_.replace('/', '\\'))
        elif mode == 'lockfile':
            file_path_ = tkinter.filedialog.askopenfilenames()
            if file_path_ != '':
                for file in file_path_:
                    sf_entry_lock_file.values.append(file.replace('/', '\\'))

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
        save_button_text.set(r_label_text_dic['save_button'][lang_number])
        continue_button_text.set(
            r_label_text_dic['continue_button'][lang_number])

        file_menu_text.set(r_label_text_dic['file_menu'][lang_number])
        readfile_menu_text.set(r_label_text_dic['readfile_menu'][lang_number])
        savefile_menu_text.set(r_label_text_dic['savefile_menu'][lang_number])
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

    global root
    root = tk.Tk()
    root.iconbitmap(os.path.join(mf_data_path, r'Movefile.ico'))
    root.title('Movefile Setting')
    root.geometry("800x287")
    root.resizable(False, False)
    root.attributes('-topmost', True)
    root.attributes('-topmost', False)
    root.update_idletasks()

    current_save_name = tk.StringVar()
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

    save_button_text = tk.StringVar()
    continue_button_text = tk.StringVar()
    file_menu_text = tk.StringVar()
    readfile_menu_text = tk.StringVar()
    savefile_menu_text = tk.StringVar()
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
        master=cf_entry_frame_keep_files, values='', frameheight=120)
    cf_entry_keep_files.bind(
        '<Button-1>', lambda event: cf_refresh_whitelist_entry())

    cf_entry_frame_keep_formats = tk.Frame(root)
    cf_label_keep_formats = ttk.Label(
        root, textvariable=cf_label_keep_formats_text)
    cf_entry_keep_formats = Combopicker(
        master=cf_entry_frame_keep_formats, values='', frameheight=90)
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
        master=sf_entry_frame_lock_folder, values=['全选'], frameheight=90)
    sf_browse_lockfolder_button = ttk.Button(root, textvariable=sf_browse_lockfolder_button_text,
                                             command=lambda: choose_lock_items('lockfolder'))

    sf_label_lock_file = ttk.Label(root, textvariable=sf_label_lock_file_text)
    sf_entry_frame_lock_file = tk.Frame(root)
    sf_entry_lock_file = Combopicker(
        master=sf_entry_frame_lock_file, values=['全选'], frameheight=50)
    sf_browse_lockfile_button = ttk.Button(root, textvariable=sf_browse_lockfile_button_text,
                                           command=lambda: choose_lock_items('lockfile'))

    sf_label_autorun = ttk.Label(root, textvariable=sf_label_autorun_text)
    sf_entry_is_autorun = tk.BooleanVar()
    sf_option_autorun = ttk.Checkbutton(root,
                                        textvariable=sf_option_autorun_text,
                                        variable=sf_entry_is_autorun)

    class ZFunc:
        @staticmethod
        def help_main():
            from LT_Dic import help_main_text
            tkinter.messagebox.showinfo(
                title='Movefile', message=help_main_text[lang_num])

        @staticmethod
        def help_before_use():
            from LT_Dic import help_before_use_text
            tkinter.messagebox.showinfo(title='Movefile',
                                        message=help_before_use_text[lang_num])

        @staticmethod
        def cf_help():
            from LT_Dic import cf_help_text
            tkinter.messagebox.showinfo(
                title='Movefile', message=cf_help_text[lang_num])

        @staticmethod
        def cf_help_keep():
            from LT_Dic import cf_help_keep_text
            tkinter.messagebox.showinfo(
                title='Movefile', message=cf_help_keep_text[lang_num])

        @staticmethod
        def cf_help_timeset():
            from LT_Dic import cf_help_timeset_text
            tkinter.messagebox.showinfo(
                title='Movefile', message=cf_help_timeset_text[lang_num])

        @staticmethod
        def sf_help():
            from LT_Dic import sf_help_text
            tkinter.messagebox.showinfo(
                title='Movefile', message=sf_help_text[lang_num])

        @staticmethod
        def sf_removable_help():
            from LT_Dic import sf_removable_help_text
            tkinter.messagebox.showinfo(
                title='Movefile', message=sf_removable_help_text[lang_num])

        @staticmethod
        def sf_lock_help():
            from LT_Dic import sf_lock_help_text
            tkinter.messagebox.showinfo(
                title='Movefile', message=sf_lock_help_text[lang_num])

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
                    os.listdir(sf_entry_select_removable.get().split(
                        ':')[0][-1] + ':')
                else:
                    os.listdir(sf_entry_path_1.get())
                os.listdir(sf_entry_path_2.get())
                if sf_entry_path_1.get() == sf_entry_path_2.get() and sf_place_mode.get() != 'movable':
                    return 'same_path_error'
                elif (sf_entry_path_1.get() in sf_entry_path_2.get() or sf_entry_path_2.get() in sf_entry_path_1.get()) \
                        and sf_place_mode.get() != 'movable':
                    return 'in_path_error'
                elif sf_place_mode.get() == 'movable':
                    if (sf_entry_select_removable.get().split(':')[0][-1] + ':') in sf_entry_path_2.get():
                        return 'in_disk_path_error'
            except:
                return True
            else:
                return False

        @staticmethod
        def cf_has_error():
            if not ZFunc.cf_is_num():
                tkinter.messagebox.showwarning(
                    'Movefile', r_label_text_dic['num_warning'][lang_num])
                return True
            elif ZFunc.cf_has_blank():
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['blank_warning'][lang_num])
                return True
            elif ZFunc.cf_path_error() == 'same_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=r_label_text_dic['same_path_warning'][lang_num])
                return True
            elif ZFunc.cf_path_error():
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['path_warning'][lang_num])
                return True
            else:
                return False

        @staticmethod
        def sf_has_error():
            path_error_data = ZFunc.sf_path_error()
            if ZFunc.sf_has_blank():
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['blank_warning'][lang_num])
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
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['path_warning'][lang_num])
                return True
            else:
                return False

    def initial_entry():
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
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
            cf_data.read(cf_config_path)
            sf_data.read(sf_config_path)
            list_saving_data()

            if len(cf_save_names) != 0:  # 更改上次修改项
                for cf_save in cf_save_names:
                    try:
                        cf_data.set(cf_save, '_last_edit_', 'False')
                        cf_data.write(
                            open(cf_config_path, 'w+', encoding='ANSI'))
                    except:
                        pass
            if len(sf_save_names) != 0:
                for sf_save in sf_save_names:
                    try:
                        sf_data.set(sf_save, '_last_edit_', 'False')
                        sf_data.write(
                            open(sf_config_path, 'w+', encoding='ANSI'))
                    except:
                        pass

            if function == 'cf':  # 如果当前界面为cf
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

            if function == 'sf':  # 如果当前界面为sf
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
            savefile(function=cf_or_sf.get(), save_name=name_entry.get())
            log_function = 'Syncfile'
            if cf_or_sf.get() == 'cf':
                log_function = 'Cleanfile'
            logging.info(
                f"A config file of {log_function} named {name_entry.get()} is saved")
            current_save_name.set(
                r_label_text_dic['current_save_name'][lang_num] + name_entry.get())
            exit_asn()

        def exit_asn():
            ask_name_window.destroy()

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
            ask_name_window = tk.Toplevel(root)
            ask_name_window.iconbitmap(
                os.path.join(mf_data_path, r'Movefile.ico'))
            ask_name_window.geometry('400x35')
            ask_name_window.title(
                r_label_text_dic['ask_name_window'][lang_num])
            ask_name_window.focus_force()
            last_edit_name = 'New_Setting'
            if last_saving_data:
                if last_saving_data[0] == mode:
                    last_edit_name = last_saving_data[1]
                else:
                    last_edit_name = last_saving_data[2]
            name_label = ttk.Label(
                ask_name_window, text=r_label_text_dic['name_label'][lang_num])
            name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')

            name_entry = ttk.Combobox(ask_name_window, values=pri_save_names)
            name_entry.insert(0, last_edit_name)
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
            cf_entry_keep_files.insert(0, cf_file.get(
                setting_name, 'pass_filename'))  # 设置跳过白名单
            cf_entry_keep_formats.insert(0, cf_file.get(
                setting_name, 'pass_format'))  # 设置跳过格式
            cf_entry_time.insert(0, cf_file.get(
                setting_name, 'set_hour'))  # 设置过期时间(hour)
            cf_entry_mode.set(cf_file.getint(setting_name, 'mode'))  # 设置判断模式
            cf_is_autorun.set(cf_file.get(setting_name, 'autorun') == 'True')
            cf_is_folder_move.set(cf_file.get(
                setting_name, 'move_folder') == 'True')
            Place('cf')
            cf_or_sf.set('cf')
            if data_error('cf', setting_name):
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['ini_error'][lang_num])

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
            sf_entry_lock_folder.insert(
                0, sf_file.get(setting_name, 'lock_folder'))
            sf_entry_lock_file.insert(
                0, sf_file.get(setting_name, 'lock_file'))
            sf_entry_is_autorun.set(sf_file.get(
                setting_name, 'autorun') == 'True')
            Place('sf', place_mode)
            cf_or_sf.set('sf')
            if data_error('sf', setting_name):
                tkinter.messagebox.showwarning(
                    title='Movefile', message=r_label_text_dic['ini_error'][lang_num])

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
            is_continue = tkinter.messagebox.askyesno(
                title='Movefile', message='确认删除配置 ' + del_name + ' ?')
            ini_file = configparser.ConfigParser()
            if del_mode in ['清理文件(Cleanfile)', 'Cleanfile'] and is_continue:
                ini_file.read(cf_config_path)
                ini_file.remove_section(del_name)
                ini_file.write(
                    open(cf_config_path, 'w+', encoding='ANSI'))
                logging.info(
                    f"A config file of Cleanfile named {del_name} is deleted")
            elif del_mode in ['同步文件(Syncfile)', 'Syncfile'] and is_continue:
                ini_file.read(sf_config_path)
                ini_file.remove_section(del_name)
                ini_file.write(
                    open(sf_config_path, 'w+', encoding='ANSI'))
                logging.info(
                    f"A config file of Syncfile named {del_name} is deleted")
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
            ask_saving_root.bind('<Enter>', lambda event: refresh_saving())
            ask_saving_root.bind('<Return>', lambda event: sure_open())
            ask_saving_root.protocol('WM_DELETE_WINDOW', exit_asr)
        elif mode == 'cf':
            open_cf_saving(save_name)
            current_save_name.set(
                r_label_text_dic['current_save_name'][lang_num] + save_name)
        elif mode == 'sf':
            open_sf_saving(save_name)
            current_save_name.set(
                r_label_text_dic['current_save_name'][lang_num] + save_name)
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
            path1 = sf_entry_select_removable.get().split(':')[0][-1] + ':\\'
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
        if cf_or_sf.get() == 'cf' and not ZFunc.cf_has_error():
            cf_operator = Thread(
                target=lambda: cf_operate_from_root(), daemon=True)
            cf_operator.start()
            root.withdraw()
        elif cf_or_sf.get() == 'sf' and not ZFunc.sf_has_error():
            sf_operator = Thread(
                target=lambda: sf_operate_from_root(), daemon=True)
            sf_operator.start()
            root.withdraw()

    # @atexit.register
    def exit_program():
        nonlocal normal_paused
        if not normal_paused:
            normal_paused = True
            task_menu.stop()
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

            root.quit()
            root.destroy()
            logging.info("Movefile Quit \n")
            ask_permit.join()
            butt_icon.join()
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

    help_menu = tk.Menu(main_menu, tearoff=False)
    help_menu.add_command(label=about_menu_text.get(), command=ZFunc.help_main)
    help_menu.add_command(label=precautions_menu_text.get(),
                          command=ZFunc.help_before_use)
    help_menu.add_separator()
    help_menu.add_command(label='Cleanfile', command=ZFunc.cf_help)
    help_menu.add_command(label=cf_keep_menu_text.get(),
                          command=ZFunc.cf_help_keep)
    help_menu.add_command(label=cf_expire_menu_text.get(),
                          command=ZFunc.cf_help_timeset)
    help_menu.add_separator()
    help_menu.add_command(label='Syncfile', command=ZFunc.sf_help)
    help_menu.add_command(label=sf_removable_menu_text.get(),
                          command=ZFunc.sf_removable_help)
    help_menu.add_command(label=sf_lock_menu_text.get(),
                          command=ZFunc.sf_lock_help)

    main_menu.add_cascade(label=file_menu_text.get(), menu=file_menu)
    main_menu.add_cascade(label=option_menu_text.get(), menu=option_menu)
    main_menu.add_cascade(label=language_menu_text.get(), menu=language_menu)
    main_menu.add_cascade(label=help_menu_text.get(), menu=help_menu)
    root.config(menu=main_menu)

    # 托盘菜单
    menu = (
        MenuItem(taskbar_setting_text.get(),
                 lambda event: root.deiconify(), default=True), Menu.SEPARATOR,
        MenuItem(taskbar_exit_text.get(), lambda event: exit_program()))
    image = Image.open(os.path.join(mf_data_path, r'Movefile.ico'))
    task_menu = Icon("icon", image, "Movefile", menu)

    root.bind("<Control-o>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-O>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-s>", lambda event: ask_save_name())
    root.bind("<Control-S>", lambda event: ask_save_name())
    # root.bind('<Button-1>'), lambda: sf_refresh_disk_list(none_disk=True)

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
        while True:
            run_list = []
            for new_area_data in new_areas_data:
                for autorun_id in get_movable_autorun_ids():
                    if str(new_area_data[2]) == autorun_id[0] and tkinter.messagebox.askokcancel(title='Movefile',
                                                                                                 message=f'检测到可移动磁盘{new_area_data[1]} ({new_area_data[0][:-1]})接入，' + '\n' +
                                                                                                         f'确定按配置 "{autorun_id[1]}" 进行同步?'):
                        run_list.append(
                            [new_area_data[0], new_area_data[1], autorun_id[1]])
                new_areas_data.remove(new_area_data)
            if run_list:
                sf_autorun_operation('movable', run_list)
            time.sleep(2)

    if first_visit:
        initial_entry()
        cf_or_sf.set('cf')
        Place('cf')
        ZFunc.help_main()
        ZFunc.help_before_use()
    else:
        read_saving()
        cf_refresh_whitelist_entry()
        continue_button.config(state=tk.NORMAL)
        if cf_or_sf.get() == '':
            cf_or_sf.set('cf')
            Place('cf')
        if startup_visit:
            root.withdraw()

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
    boot_visit = initial_data.boot_time <= 120
    first_visit = initial_data.first_visit
    logging.info(
        f"Movefile Start\nVisits today: {visits_today}\nTime since startup: {initial_data.boot_time}\nStartup visit: {str(boot_visit)}")

    if visits_today == 1 and boot_visit:
        autorun_options = Thread(
            target=lambda: startup_autorun(), daemon=True)
        autorun_options.start()

    make_ui(first_visit=first_visit, startup_visit=boot_visit)


if __name__ == '__main__':
    main()
