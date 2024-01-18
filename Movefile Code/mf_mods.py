
import configparser
import logging
import os
import sys
import time
import tkinter.messagebox
from base64 import b64decode
from ctypes import windll
from datetime import datetime

import LT_Dic
import mf_icon as icon
from mf_const import (CF_CONFIG_PATH, CF_DATA_PATH, DESKTOP_PATH,
                      MF_CONFIG_PATH, MF_DATA_PATH, MF_ICON_PATH, MF_LOG_PATH,
                      ROAMING_PATH, SF_CONFIG_PATH, SF_DATA_PATH, STARTUP_PATH)
from mttkinter.mtTkinter import Tk
from psutil import disk_partitions
from win10toast_edited import ToastNotifier
from win32api import GetVolumeInformation
from win32com.client import Dispatch
from win32gui import FindWindow, ShowWindow
from winshell import CreateShortcut

from Movefile import gvar

mf_toaster = ToastNotifier()


# The MFProgressChecker class is used to check if the program is already running.
# If it's running, it will display a message box to inform the user, and put the window on the top.
class MFProgressChecker:

    def __init__(self):
        self.continue_this_progress = True
        if self.proc_root_on():
            self.continue_this_progress = False

    def proc_root_on(self):
        mfs_hwnd = FindWindow(None, 'Movefile Setting')
        if mfs_hwnd:
            return self.display_root(mfs_hwnd)
        return False

    def display_root(self, mf_hwnd):
        temp_root = Tk()
        temp_root.withdraw()
        try:
            ShowWindow(mf_hwnd, 5)
            tkinter.messagebox.showinfo(
                title="Movefile", message="The app's running!")
            temp_root.quit()
            temp_root.destroy()
            return True
        except:
            temp_root.quit()
            temp_root.destroy()
            return False

# The Initialization class is used for initializing the Movefile programme.


class Initialization:
    def __init__(self):
        self.startup_visit = self.get_startup_state()
        self.first_visit = False
        self.quit_after_autorun = False
        self.check_data_path()

        self.mf_data = configparser.ConfigParser()
        self.mf_data.read(MF_CONFIG_PATH)

        # self.log_file_path = os.path.join(MF_DATA_PATH, r'Movefile.log')
        self.set_log_writer()

        self.mf_ico = None
        if not os.path.exists(MF_ICON_PATH):
            self.load_icon()

        self.ask_time_today = 0
        self.init_config()

        if self.first_visit:  # 判断是否为首次访问
            logging.info("\nThis is the first visit of this program.")

    def get_startup_state(self):
        if "--startup_visit" in sys.argv:
            return True
        return False

    def check_data_path(self):
        """
        This function ensures that the route where previous data of this program could be found.
        """

        if 'Movefile' not in os.listdir(ROAMING_PATH):
            self.first_visit = True
            os.mkdir(MF_DATA_PATH)
            time.sleep(0.1)

        if 'Cleanfile' not in os.listdir(MF_DATA_PATH):
            os.mkdir(CF_DATA_PATH)
        if 'Syncfile' not in os.listdir(MF_DATA_PATH):
            os.mkdir(SF_DATA_PATH)

    def init_config(self):

        time_now = datetime.today()
        date = str(time_now.date())

        if not os.path.exists(MF_CONFIG_PATH):  # 创建配置文件
            file = open(MF_CONFIG_PATH,
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
        if not self.mf_data.has_option('General', 'quit_after_autorun'):
            self.mf_data.set('General', 'quit_after_autorun', 'False')
        else:
            self.quit_after_autorun = self.mf_data.getboolean(
                'General', 'quit_after_autorun')

        if not self.mf_data.has_option('General', 'desktop_shortcut'):
            self.mf_data.set('General', 'desktop_shortcut', 'False')

        if os.path.exists(os.path.join(DESKTOP_PATH, r"Movefile.lnk")):
            self.mf_data.set('General', 'desktop_path', 'True')
        else:
            self.mf_data.set('General', 'desktop_path', 'False')
        if os.path.exists(os.path.join(STARTUP_PATH, r"Movefile.lnk")):
            self.mf_data.set('General', 'autorun', 'True')
        else:
            self.mf_data.set('General', 'autorun', 'False')

        self.mf_data.write(
            open(MF_CONFIG_PATH, "w+", encoding='ANSI'))

    def load_icon(self):
        self.mf_ico = open(MF_ICON_PATH, 'wb')
        self.mf_ico.write(b64decode(icon.Movefile_ico))
        self.mf_ico.close()

    def set_log_writer(self):
        if not os.path.exists(MF_LOG_PATH):
            logfile = open(MF_LOG_PATH, 'a')
            logfile.close()
        formatter = "[%(asctime)s] - [%(levelname)s]: %(message)s"
        logging.basicConfig(level=logging.INFO,
                            filename=MF_LOG_PATH,
                            filemode='a+',
                            format=formatter)


def mf_log(content):
    logging.info(content)


def set_startup(state=True, lang_n=0):
    """
    The function sets the auto startup state to either True or False.

    :param state: The `state` parameter is a boolean value that determines whether the startup process
    should be enabled or disabled. If `state` is `True`, the startup process will be enabled. If `state`
    is `False`, the startup process will be disabled, defaults to True (optional)
    """
    # 将快捷方式添加到自启动目录
    bin_path = r"Movefile.exe"
    shortcut_path = os.path.join(STARTUP_PATH, r"Movefile.lnk")
    desc = LT_Dic.lnk_desc[lang_n]
    gen_cf = configparser.ConfigParser()
    gen_cf.read(MF_CONFIG_PATH)
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
    if state:
        gen_cf.set('General', 'autorun', 'True')
        CreateShortcut(
            Path=shortcut_path,
            Target=bin_path,
            Icon=(MF_ICON_PATH, 0),
            Description=desc,
            Arguments="--startup_visit")
    else:
        gen_cf.set('General', 'autorun', 'False')
    gen_cf.write(
        open(MF_CONFIG_PATH, "w+", encoding='ANSI'))


def put_desktop_shortcut(state=True, lang_n=0):
    """
    The function `put_desktop_shortcut` allows you to put the shortcut of this program on Desktop.

    :param state: The state parameter is a boolean value that determines whether the start menu should be displayed or not. If state is set to True, the start menu will be displayed. If state is set to False, the start menu will not be displayed, defaults to True (optional)
    :param lang_n: The `lang_n` parameter is used to specify the language for the start menu. It is an integer value that represents the language code, defaults to 1 (optional)
    """

    bin_path = r"Movefile.exe"
    shortcut_path = os.path.join(DESKTOP_PATH, r"Movefile.lnk")
    desc = LT_Dic.lnk_desc[lang_n]
    gen_cf = configparser.ConfigParser()
    gen_cf.read(MF_CONFIG_PATH)
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
    if state:
        gen_cf.set('General', 'desktop_shortcut', 'True')
        CreateShortcut(
            Path=shortcut_path,
            Target=bin_path,
            Icon=(MF_ICON_PATH, 0),
            Description=desc)
    else:
        gen_cf.set('General', 'desktop_shortcut', 'False')
    gen_cf.write(
        open(MF_CONFIG_PATH, "w+", encoding='ANSI'))


def set_auto_quit(state=True):
    """
    The function `set_close_after_autorun` sets the value of the `quit_after_autorun` variable in the `gvar` module to the specified value.

    :param state: The `state` parameter is a boolean value that determines whether the program should quit after the autorun process is completed. If `state` is `True`, the program will quit after the autorun process is completed. If `state` is `False`, the program will not quit after the autorun process is completed, defaults to True (optional)
    """

    ca_cf = configparser.ConfigParser()
    ca_cf.read(MF_CONFIG_PATH)
    ca_cf.set('General', 'quit_after_autorun', str(state))
    mf_log(f"Set quit-after-autorun to {state}")


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
    cf_file.read(CF_CONFIG_PATH)
    cf_save_names = cf_file.sections()
    sf_file = configparser.ConfigParser()
    sf_file.read(SF_CONFIG_PATH)
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


def get_movable_autorun_infos():
    from syncfile import fixed_sf_config
    sf_dat = configparser.ConfigParser()
    sf_dat.read(SF_CONFIG_PATH)
    savings = sf_dat.sections()
    autorun_ids = []
    for saving in savings:
        if fixed_sf_config(sf_dat, saving) and sf_dat.get(saving, 'place_mode') == 'movable' and sf_dat.getboolean(saving, 'autorun'):
            autorun_ids.append([sf_dat.get(saving, 'disk_number'), saving, sf_dat.getboolean(saving, 'direct_sync')])
    return autorun_ids


def detect_removable_disks_thread(master_root, lang_num):
    """
    The function detects removable disks using threading.
    """
    disk_list = []
    area_data_list = []
    number_book = {}
    while not gvar.get('program_finished'):
        for item in disk_partitions():
            # 判断是不是可移动磁盘 获取可移动磁盘的盘符
            if "removable" in item.opts and item.mountpoint not in disk_list:
                disk_list.append(item.mountpoint)
        if not disk_list:
            time.sleep(0.5)
            continue
        for pf in disk_list:
            if not os.path.exists(pf):
                disk_list.remove(pf)
                area_data_list.remove(number_book[pf])
            else:
                seria_number = GetVolumeInformation(pf)
                area_name = seria_number[0]
                area_uuid = seria_number[1]
                if area_uuid not in area_data_list:
                    area_data_list.append(area_uuid)
                    number_book[pf] = area_uuid
                    ask_sync_disk(master_root, lang_num, [
                                  pf, area_name, area_uuid])
        time.sleep(0.5)


def ask_sync_disk(master_root, lang_num, new_area_data):
    """
        The function "ask_sync_disk" is used to prompt the user to input whether they want to
        synchronize their disk.
        """
    from syncfile import sf_autorun_operation
    for autorun_info in get_movable_autorun_infos():
        msg_ps = LT_Dic.sfdic['new_disk_detected'][lang_num]
        msg_content = f'{msg_ps[0]}{new_area_data[1]} ({new_area_data[0][:-1]}){msg_ps[1]}{msg_ps[2]}{autorun_info[1]}{msg_ps[3]}'
        if str(new_area_data[2]) == autorun_info[0] and autorun_info[2] or tkinter.messagebox.askokcancel(title='Movefile',
                                                                                     message=msg_content):
            sf_autorun_operation(master_root, 'movable', [
                                 new_area_data[0], new_area_data[1], autorun_info[1]])


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
