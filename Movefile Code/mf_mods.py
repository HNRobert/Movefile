
import configparser
from base64 import b64decode
from ctypes import windll
from datetime import datetime
import logging
import os
import sys
import time

from psutil import disk_partitions
from win32api import GetVolumeInformation
from win32com.client import Dispatch
from winshell import CreateShortcut

import LT_Dic
from Movefile import gvar
from mf_const import ROAMING_PATH, MF_DATA_PATH, CF_DATA_PATH, SF_DATA_PATH, CF_CONFIG_PATH, SF_CONFIG_PATH, DESKTOP_PATH, START_MENU_PATH, STARTUP_PATH
import Movefile_icon as icon
from win10toast_edited import ToastNotifier

mf_toaster = ToastNotifier()


class Initialization:
    def __init__(self):
        self.startup_visit = self.get_startup_state()
        self.first_visit = False
        self.check_data_path()

        self.mf_data = configparser.ConfigParser()
        self.mf_data.read(os.path.join(MF_DATA_PATH, r'Movefile_data.ini'))

        self.log_file_path = os.path.join(MF_DATA_PATH, r'Movefile.log')
        self.set_log_writer()

        self.mf_ico = None
        if not os.path.exists(os.path.join(MF_DATA_PATH, r'Movefile.ico')):
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

        if not os.path.exists(os.path.join(MF_DATA_PATH, r'Movefile_data.ini')):  # 创建配置文件
            file = open(os.path.join(MF_DATA_PATH, r'Movefile_data.ini'),
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

        if os.path.exists(os.path.join(DESKTOP_PATH, r"Movefile.lnk")):
            self.mf_data.set('General', 'desktop_path', 'True')
        else:
            self.mf_data.set('General', 'desktop_path', 'False')
        if os.path.exists(os.path.join(STARTUP_PATH, r"Movefile.lnk")):
            self.mf_data.set('General', 'autorun', 'True')
        else:
            self.mf_data.set('General', 'autorun', 'False')

        self.mf_data.write(
            open(os.path.join(MF_DATA_PATH, r'Movefile_data.ini'), "w+", encoding='ANSI'))

    def load_icon(self):
        self.mf_ico = open(os.path.join(MF_DATA_PATH, r'Movefile.ico'), 'wb')
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
    startup_path = os.path.join(START_MENU_PATH, r"StartUp")
    bin_path = r"Movefile.exe"
    shortcut_path = os.path.join(startup_path, r"Movefile.lnk")
    desc = LT_Dic.lnk_desc[lang_n]
    icon_ = os.path.join(MF_DATA_PATH, r'Movefile.ico')
    gen_cf = configparser.ConfigParser()
    gen_cf.read(os.path.join(MF_DATA_PATH, r'Movefile_data.ini'))
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
        open(os.path.join(MF_DATA_PATH, r'Movefile_data.ini'), "w+", encoding='ANSI'))


def put_desktop_shortcut(state=True, lang_n=0):
    """
    The function `put_desktop_shortcut` allows you to put the shortcut of this program on Desktop.

    :param state: The state parameter is a boolean value that determines whether the start menu should be displayed or not. If state is set to True, the start menu will be displayed. If state is set to False, the start menu will not be displayed, defaults to True (optional)
    :param lang_n: The `lang_n` parameter is used to specify the language for the start menu. It is an integer value that represents the language code, defaults to 1 (optional)
    """

    bin_path = r"Movefile.exe"
    shortcut_path = os.path.join(DESKTOP_PATH, r"Movefile.lnk")
    desc = LT_Dic.lnk_desc[lang_n]
    icon_ = os.path.join(MF_DATA_PATH, r'Movefile.ico')
    gen_cf = configparser.ConfigParser()
    gen_cf.read(os.path.join(MF_DATA_PATH, r'Movefile_data.ini'))
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
        open(os.path.join(MF_DATA_PATH, r'Movefile_data.ini'), "w+", encoding='ANSI'))


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


def detect_removable_disks_thread():
    """
    The function detects removable disks using threading.
    """
    disk_list = []
    area_data_list = []
    number_book = {}
    while not gvar.get('program_finished'):
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
                        new_areas_data = gvar.get('new_areas_data')
                        new_areas_data.append([pf, area_name, area_number])
                        gvar.set('new_areas_data', new_areas_data)
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
