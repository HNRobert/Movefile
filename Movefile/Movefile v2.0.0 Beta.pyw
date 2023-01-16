# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 17:07:30 2022

@author: Robert He
"""

vision = 'v2.0.0'
update_time = '2023/1/14-night'

import base64
import configparser
import os
import shutil
import time
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
import winreg
from datetime import datetime

import winshell
from win10toast import ToastNotifier

import Movefile_icon as icon
from ComBoPicker import Combopicker


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


def cf_data_error():
    try:
        cf = configparser.ConfigParser()
        cf.read(cf_data_path + r'Cleanfile_data.ini')  # 获取配置文件
        old_path_ = cf.get('Cleanfile_settings', 'old_path')  # 旧文件夹
        new_path_ = cf.get('Cleanfile_settings', 'new_path')  # 新文件夹
        pass_file = cf.get('Cleanfile_settings', 'pass_filename').split(',')  # 设置跳过白名单
        pass_format = cf.get('Cleanfile_settings', 'pass_format').split(',')  # 设置跳过格式
        time_ = cf.getint('Cleanfile_settings', 'set_hour') * 3600  # 设置过期时间(hour)
        mode_ = cf.getint('Cleanfile_settings', 'mode')
        move_folder = cf.get('Cleanfile_settings', 'move_folder')
        autorun_ = cf.get('Cleanfile_settings', 'autorun')
        cf_move_dir(old__path=old_path_, new__path=new_path_, pass__file=pass_file, pass__format=pass_format, t=time_,
                    check__mode=mode_, is__move__folder=False, test=True)
        if (move_folder == 'True' or move_folder == 'False') and (autorun_ == 'True' or autorun_ == 'False'):
            return False
        else:
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


def find_last_edit():
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
            last_edit = ['cf', cf_save_name, all_save_names]
            break
    else:
        for sf_save_name in sf_save_names:
            if sf_file.get(sf_save_name, '_last_edit_') == 'True':
                last_edit = ['sf', sf_save_name, all_save_names]
                break
        else:
            last_edit = []
    return last_edit


def ask_info(cf_error=False, cf_muti_ask=False, cf_first_ask=False):
    cf_data = configparser.ConfigParser()
    sf_data = configparser.ConfigParser()

    def cf_refresh_whitelist_entry(folder_names=None):
        if folder_names is None:
            folder_names = []
        try:
            global cf_entry_keep_files
            global cf_entry_keep_formats
            all_ends = []
            file_names = []
            item_names = os.listdir(cf_entry_old_path.get())
            for file in item_names:
                file_end = '.' + file.split('.')[-1]
                if os.path.isfile(cf_entry_old_path.get() + '\\' + file):
                    all_ends.append(file_end)
                    file_names.append(file)
            exist_ends = sorted(set(all_ends))
            cf_entry_keep_files = Combopicker(master=cf_entry_frame_keep_files,
                                              values=['全选'] + folder_names + file_names,
                                              frameheight=120)
            cf_entry_keep_files.grid(row=2, column=1, ipadx=240, pady=5, sticky='W')
            cf_entry_keep_formats = Combopicker(master=cf_entry_frame_keep_formats, values=['全选'] + exist_ends,
                                                frameheight=90)
            cf_entry_keep_formats.grid(row=3, column=1, ipadx=240, pady=0, sticky='W')
            cf_entry_keep_files_x.grid_forget()
            cf_entry_keep_formats_x.grid_forget()
        except:
            pass

    def cf_select_path(place, ori_content):
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

    def cf_folder_move(state):
        if state:
            folders = os.listdir(cf_entry_old_path.get())
            move_folder_names = []
            for folder in folders:
                if os.path.isdir(cf_entry_old_path.get() + '\\' + folder):
                    move_folder_names.append(folder)
            cf_refresh_whitelist_entry(folder_names=move_folder_names)
        else:
            cf_refresh_whitelist_entry()

    def change_active_mode(mode):
        def cf_state():
            sf_label_path_1.grid_forget()
            sf_label_path_2.grid_forget()
            sf_entry_path_1.grid_forget()
            sf_entry_path_2.grid_forget()
            sf_browse_path_1_button.grid_forget()
            sf_browse_path_2_button.grid_forget()
            sf_option_mode_double.grid_forget()
            sf_option_mode_single.grid_forget()
            sf_label_mode.grid_forget()
            sf_label_lock_folder.grid_forget()
            sf_entry_lock_files_x.grid_forget()

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

            sf_label_path_1.grid(row=1, column=0, pady=5, sticky='E')
            sf_label_path_2.grid(row=2, column=0, pady=5, sticky='E')
            sf_entry_path_1.grid(row=1, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_entry_path_2.grid(row=2, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            sf_browse_path_1_button.grid(row=1, column=1, ipadx=3, sticky='E', padx=10)
            sf_browse_path_2_button.grid(row=2, column=1, ipadx=3, sticky='E', padx=10)
            sf_option_mode_double.grid(row=3, column=1, padx=10, ipadx=0, sticky='W')
            sf_option_mode_single.grid(row=3, column=1, padx=145, ipadx=0, sticky='E')
            sf_label_mode.grid(row=3, column=0, pady=5, sticky='E')
            sf_label_lock_folder.grid(row=4, column=0, pady=5, sticky='E')
            sf_entry_lock_files_x.grid(row=4, column=1, padx=10, pady=5, ipadx=240, sticky='W')

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
    cf_browse_old_path_button = ttk.Button(root, text="浏览", command=lambda: cf_select_path(place='old',
                                                                                             ori_content=cf_entry_old_path.get()))
    cf_browse_old_path_button.grid(row=1, column=1, ipadx=3, sticky='E', padx=10)

    cf_label_new_path = ttk.Label(root, text='新文件夹路径：')
    cf_label_new_path.grid(row=2, column=0, pady=5, sticky='E')
    cf_entry_new_path = ttk.Entry(root, textvariable=newpath)
    cf_entry_new_path.grid(row=2, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    cf_browse_new_path_button = ttk.Button(root, text="浏览", command=lambda: cf_select_path(place='new',
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
    cf_option_folder_move = ttk.Checkbutton(root, text='移动项目包括文件夹', variable=cf_is_folder_move,
                                            command=lambda: cf_folder_move(cf_is_folder_move.get()))
    cf_option_folder_move.grid(row=3, column=1, padx=10, sticky='E')

    cf_entry_frame_keep_files = tk.Frame(root)
    cf_entry_frame_keep_files.grid(row=4, column=1, ipadx=5, sticky='E')
    cf_label_keep_files = ttk.Label(root, text='保留项目(选填)：')
    cf_label_keep_files.grid(row=4, column=0, pady=5, sticky='E')
    cf_entry_keep_files_x = ttk.Entry(root)
    cf_entry_keep_files_x.grid(row=4, column=1, padx=10, pady=5, ipadx=240, sticky='W')
    cf_entry_keep_files_x.config(state=tk.DISABLED)

    cf_entry_frame_keep_formats = tk.Frame(root)
    cf_entry_frame_keep_formats.grid(row=5, column=1, pady=5, ipadx=5, sticky='E')
    cf_label_keep_formats = ttk.Label(root, text='     保留文件格式(选填)：')
    cf_label_keep_formats.grid(row=5, column=0, sticky='E')
    cf_entry_keep_formats_x = ttk.Entry(root)
    cf_entry_keep_formats_x.grid(row=5, column=1, padx=10, pady=5, ipadx=240, sticky='W')
    cf_entry_keep_formats_x.config(state=tk.DISABLED)

    cf_label_time = ttk.Label(root, text='过期时间设定(小时)：')
    cf_label_time.grid(row=6, column=0, sticky='E')
    cf_entry_time = ttk.Entry(root)
    cf_entry_time.grid(row=6, column=1, padx=10, pady=5, ipadx=240, sticky='W')

    cf_label_start_options = ttk.Label(root, text='系统选项：')
    cf_label_start_options.grid(row=7, column=0, sticky='E')
    cf_is_autorun = tk.BooleanVar()
    cf_option_is_auto = ttk.Checkbutton(root, text='开机自动运行 Cleanfile', variable=cf_is_autorun)
    cf_option_is_auto.grid(row=7, column=1, padx=10, sticky='NW')

    sf_label_path_1 = ttk.Label(root, text="文件夹路径-A：")
    sf_label_path_1.grid(row=1, column=0, pady=5, sticky='E')
    sf_entry_path_1 = ttk.Entry(root, textvariable=path_1)
    sf_entry_path_1.grid(row=1, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    sf_browse_path_1_button = ttk.Button(root, text="浏览",
                                         command=lambda: cf_select_path(place='1', ori_content=sf_entry_path_1.get()))
    sf_browse_path_1_button.grid(row=1, column=1, ipadx=3, sticky='E', padx=10)

    sf_label_path_2 = ttk.Label(root, text='文件夹路径-B：')
    sf_label_path_2.grid(row=2, column=0, pady=5, sticky='E')
    sf_entry_path_2 = ttk.Entry(root, textvariable=path_2)
    sf_entry_path_2.grid(row=2, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    sf_browse_path_2_button = ttk.Button(root, text="浏览",
                                         command=lambda: cf_select_path(place='2', ori_content=sf_entry_path_2.get()))
    sf_browse_path_2_button.grid(row=2, column=1, ipadx=3, sticky='E', padx=10)

    sf_label_mode = ttk.Label(root, text='             同步模式选择：')
    sf_label_mode.grid(row=3, column=0, pady=5, sticky='E')
    sf_entry_mode = tk.StringVar()
    sf_option_mode_double = ttk.Radiobutton(root, text="双向同步（皆保留最新版本）", variable=sf_entry_mode,
                                            value='double')
    sf_option_mode_double.grid(row=3, column=1, padx=10, ipadx=0, sticky='W')
    sf_option_mode_single = ttk.Radiobutton(root, text="单向同步（来自路径B的新数据不会同步到路径A）", variable=sf_entry_mode,
                                            value='single')
    sf_option_mode_single.grid(row=3, column=1, padx=145, ipadx=0, sticky='E')

    sf_label_lock_folder = ttk.Label(root, text='锁定文件夹(选填)：')
    sf_label_lock_folder.grid(row=4, column=0, pady=5, sticky='E')
    sf_entry_lock_files_x = ttk.Entry(root)
    sf_entry_lock_files_x.grid(row=4, column=1, padx=10, pady=5, ipadx=240, sticky='W')
    sf_entry_lock_files_x.config(state=tk.DISABLED)

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

    def savefile(mode, save_name='New_Setting'):  # 保存文件
        cf_data.read(cf_data_path + r'Cleanfile.ini')
        sf_data.read(sf_data_path + r'Syncfile.ini')
        cf_savings = cf_data.sections()
        sf_savings = sf_data.sections()
        if len(cf_savings) != 0:
            for cf_save in cf_savings:
                try:
                    cf_data.set(cf_save, '_last_edit_', 'False')
                    cf_data.write(open(cf_data_path + r'Cleanfile_data.ini', 'w+', encoding='ANSI'))
                except:
                    pass
        if len(sf_savings) != 0:
            for sf_save in sf_savings:
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
            if not cf_data.has_section(save_name):
                cf_data.add_section(save_name)
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
            if not sf_data.has_section(save_name):
                sf_data.add_section(save_name)
            sf_data.set(save_name, '_last_edit_', 'True')
            sf_data.set(save_name, 'path_1', sf_entry_path_1.get())
            sf_data.set(save_name, 'path_2', sf_entry_path_2.get())
            sf_data.set(save_name, 'mode', sf_entry_mode.get())
            sf_data.set(save_name, 'lock_path', '114514')
            sf_data.write(open(sf_data_path + r'Syncfile_data.ini', 'w+', encoding='ANSI'))

        tkinter.messagebox.showinfo(title='信息提示', message='信息保存成功！')
        bt2.config(state=tk.NORMAL)

    def cf_open_ini(ask_path=False):
        cf_store_path = cf_data_path + r'Cleanfile_data.ini'
        sf_store_path = sf_data_path + r'Syncfile_data.ini'
        cf_file = configparser.ConfigParser()
        cf_file.read(cf_store_path)  # 获取配置文件
        sf_file = configparser.ConfigParser()
        sf_file.read(sf_store_path)
        last_edit = find_last_edit()
        if last_edit[0] == 'cf' and not ask_path:
            save_name = last_edit[1]
            if cf_entry_old_path.get() != '':
                cf_entry_old_path.delete(0, 'end')
            if cf_entry_new_path.get() != '':
                cf_entry_new_path.delete(0, 'end')
            cf_entry_old_path.insert(0, cf_file.get(save_name, 'old_path'))  # 旧文件夹
            cf_entry_new_path.insert(0, cf_file.get(save_name, 'new_path'))  # 新文件夹
            cf_refresh_whitelist_entry()
            if cf_entry_keep_files.get() != '':
                cf_entry_keep_files.delete(0, 'end')
            if cf_entry_keep_formats.get() != '':
                cf_entry_keep_formats.delete(0, 'end')
            if cf_entry_time.get() != '':
                cf_entry_time.delete(0, 'end')
            cf_entry_keep_files.insert(0, cf_file.get(save_name, 'pass_filename'))  # 设置跳过白名单
            cf_entry_keep_formats.insert(0, cf_file.get(save_name, 'pass_format'))  # 设置跳过格式
            cf_entry_time.insert(0, cf_file.get(save_name, 'set_hour'))  # 设置过期时间(hour)
            cf_entry_mode.set(cf_file.getint(save_name, 'mode'))  # 设置判断模式
            cf_is_autorun.set(cf_file.get(save_name, 'autorun'))
            cf_is_folder_move.set(cf_file.get(save_name, 'move_folder'))
            change_active_mode('cf')
            cf_or_sf.set('cf')

    def cf_helpfunc():
        tkinter.messagebox.showinfo(title='Movefile', message="""软件名称： Movefile
软件版本： """ + vision + """               更新时间： """ + update_time + """

功能概述：
本程序可将某个文件夹中
一定时间未修改或者未访问
且满足其他一些设定要求的文件
转移到另一个文件夹
使你可以方便地整理文件

如果对本软件功能有任何疑惑，可以查看菜单栏中的 "帮助" 选项

作者：Robert He
如果对本软件有任何改进意见，请联系作者
如果意见被采纳，新版本中会进行更改
作者QQ：2567466856
""")

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

    def cf_help_before_use():
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
  且无法按上面的解释修复
  请联系作者（QQ:2567466856）,我会尽快尝试帮你修复""")

    def cf_continue_going(only_quit=False):
        root.quit()
        root.destroy()
        if not only_quit:
            cf_operate(cf_data_path + r'Cleanfile_data.ini')
            cf_show_notice()

    def ask_save_name(last_edit_data):
        def cf_has_error():
            if not cf_is_num():
                tkinter.messagebox.showwarning('Movefile', '警告：请在时间设定栏内输入数字')
                return True
            elif cf_has_blank():
                tkinter.messagebox.showwarning(title='Movefile',
                                               message='警告：请填写所有除白名单与开机自启勾选栏外的必填项目！')
                return True
            elif cf_path_error():
                tkinter.messagebox.showwarning(title='Movefile', message='警告：请填输入有效路径！（建议使用浏览）')
                return True
            else:
                return False

        def sf_has_error():
            return False

        def sure_save():
            savefile(mode=cf_or_sf.get(), save_name=name_entry.get())
            ask_name_window.quit()
            ask_name_window.destroy()

        mode = cf_or_sf.get()
        if mode == 'cf':
            has_error = cf_has_error()
        elif mode == 'sf':
            has_error = sf_has_error()
        else:
            has_error = True
        if not has_error:
            ask_name_window = tk.Tk()
            ask_name_window.iconbitmap(mf_data_path + r'Movefile.ico')
            ask_name_window.geometry('400x35')
            ask_name_window.title('设置配置存档名称')
            last_edit_name = 'New_Setting'
            all_savings_names = []
            if last_edit_data:
                last_edit_name = last_edit_data[1]
                all_savings_names = last_edit_data[2]
            name_label = ttk.Label(ask_name_window, text='  请输入存档的名称：')
            name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')

            name_entry = ttk.Combobox(ask_name_window, values=all_savings_names)
            name_entry.insert(0, last_edit_name)
            name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='W')
            sure_name_bottom = ttk.Button(ask_name_window, text='确定保存', command=lambda: sure_save())
            sure_name_bottom.grid(row=0, column=2, sticky='W')
            ask_name_window.mainloop()

    # 创建按键
    bt1 = ttk.Button(root, text='保存', command=lambda: ask_save_name(last_edit_data=find_last_edit()))
    bt1.grid(row=14, column=1, ipadx=100, pady=4, padx=10, sticky='W')
    bt2 = ttk.Button(root, text='继续', command=cf_continue_going)
    bt2.grid(row=14, column=1, ipadx=100, pady=4, padx=10, sticky='E')
    bt2.config(state=tk.DISABLED)

    # 菜单栏
    main_menu = tk.Menu(root)
    file_menu = tk.Menu(main_menu, tearoff=False)
    file_menu.add_command(label="读取配置文件", command=lambda: cf_open_ini(ask_path=True), accelerator="Ctrl+O")
    file_menu.add_command(label="保存", command=lambda: savefile(mode=cf_or_sf.get(), save_name=ask_save_name(last_edit_data=find_last_edit())),
                          accelerator="Ctrl+S")
    help_menu = tk.Menu(main_menu, tearoff=False)
    help_menu.add_command(label="关于本软件", command=cf_helpfunc)
    help_menu.add_command(label="使用前注意事项", command=cf_help_before_use)
    help_menu.add_command(label="保留文件/文件格式选择", command=cf_help_keep)
    help_menu.add_command(label="过期时间设定", command=cf_help_timeset)
    main_menu.add_cascade(label="文件", menu=file_menu)
    main_menu.add_cascade(label="帮助", menu=help_menu)
    root.config(menu=main_menu)

    root.bind("<Control-o>", lambda: cf_open_ini(ask_path=True))
    root.bind("<Control-O>", lambda: cf_open_ini(ask_path=True))
    root.bind("<Control-s>", lambda: ask_save_name(last_edit_data=find_last_edit()))
    root.bind("<Control-S>", lambda: ask_save_name(last_edit_data=find_last_edit()))

    if cf_first_ask:
        cf_entry_old_path.insert(0, get_desktop())
        cf_entry_time.insert(0, '0')
        cf_entry_mode.set(1)
        cf_refresh_whitelist_entry()
        cf_or_sf.set('cf')
        change_active_mode('cf')
        cf_helpfunc()
        cf_help_before_use()

    if cf_muti_ask or cf_error:
        cf_refresh_whitelist_entry()
        cf_open_ini(ask_path=False)
        bt2.config(state=tk.NORMAL)
        if cf_or_sf.get() == '':
            cf_or_sf.set('cf')
            change_active_mode('cf')
        if cf_error:
            tkinter.messagebox.showwarning(title='Movefile', message='''错误：配置信息无效！
请尽量不要手动更改ini配置文件''')

    root.mainloop()


def cf_move_dir(old__path, new__path, pass__file, pass__format, t, check__mode, is__move__folder, test=False):
    global Movename, Errorname
    Movename = ''
    Errorname = ''
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
            if (now - last >= t) and not test:  # 移动过期文件
                try:
                    shutil.move(file_path, new__path)
                    Movename += (file + ',  ')
                except:
                    Errorname += (file + ',  ')


def cf_create_shortcut(bin_path: str, name: str, _icon: str, desc: str):
    try:
        shortcut = name + ".lnk"
        winshell.CreateShortcut(
            Path=shortcut,
            Target=bin_path,
            Icon=(_icon, 0),
            Description=desc)
    except:
        pass


def cf_set_startup(autorun):
    # 将快捷方式添加到自启动目录
    # 获取用户名
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
    startup_path = os.path.join(roaming_path + r"Microsoft\Windows\Start Menu\Programs\Startup")
    bin_path = r"Movefile " + vision + ".exe"
    link_path = startup_path + "\\Movefile"
    desc = "自动转移文件程序"
    icon_ = mf_data_path + r'Movefile.ico'
    if autorun:
        cf_create_shortcut(bin_path, link_path, icon_, desc)
    else:
        if os.path.exists(link_path + '.lnk'):
            os.remove(link_path + '.lnk')


def cf_operate(save_name):
    global old_path, new_path
    cf = configparser.ConfigParser()
    cf.read(cf_data_path + r'Cleanfile_data.ini')  # 获取配置文件
    old_path = cf.get(save_name, 'old_path')  # 旧文件夹
    new_path = cf.get(save_name, 'new_path')  # 新文件夹
    pass_file = cf.get(save_name, 'pass_filename').split(',')  # 设置跳过白名单
    pass_format = cf.get(save_name, 'pass_format').split(',')  # 设置跳过格式
    time_ = cf.getint(save_name, 'set_hour') * 3600  # 设置过期时间(hour)
    mode = cf.getint(save_name, 'mode')  # 设置判断模式
    is_move_folder = cf.get(save_name, 'move_folder')  # 设置是否移动文件夹
    if cf.get(save_name, 'autorun') == 'True':
        cf_set_startup(True)
    else:
        cf_set_startup(False)
    cf_move_dir(old__path=old_path, new__path=new_path, pass__file=pass_file, pass__format=pass_format, t=time_,
                check__mode=mode, is__move__folder=is_move_folder)

    pass
def cf_show_notice():
    toaster = ToastNotifier()
    new_folder = new_path.split('\\')[-1]
    old_folder = old_path.split('\\')[-1]
    if len(Movename) > 0:
        toaster.show_toast('These Files from ' + old_folder + ' are moved to ' + new_folder + ':',
                           Movename,
                           icon_path=mf_data_path + r'Movefile.ico',
                           duration=10,
                           threaded=False)
    else:
        toaster.show_toast(old_folder + ' is pretty clean now',
                           'Nothing is moved away',
                           icon_path=mf_data_path + r'Movefile.ico',
                           duration=10,
                           threaded=False)
    if len(Errorname) > 0:
        toaster.show_toast("Couldn't move files",
                           Errorname + """
无法被移动，请在关闭文件或移除重名文件后重试""",
                           icon_path=mf_data_path + r'Movefile.ico',
                           duration=10,
                           threaded=False)


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
    last_edit_time_1 = int(os.stat(file1_path).st_mtime)
    if os.path.exists(file2_path):
        last_edit_time_2 = int(os.stat(file2_path).st_mtime)
    else:
        last_edit_time_2 = 0
    new_file, prior_file = '', ''
    pas = False
    if no_judge:
        sf_creat_folder(file2_path)
        shutil.copyfile(file1_path, file2_path)
        pas = True
    elif last_edit_time_1 > last_edit_time_2:
        new_file = file1_path
        prior_file = file2_path
    elif last_edit_time_1 < last_edit_time_2:
        new_file = file2_path
        prior_file = file1_path
        if single_way:
            pas = True
    else:
        pas = True
    if not pas:
        shutil.copyfile(new_file, prior_file)


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


def sf_operate(path1, path2):
    all_files_1 = sf_scan_files(path1)
    all_files_2 = sf_scan_files(path2)
    for file1 in all_files_1:
        file1_path = path1 + file1
        for file2 in all_files_2:
            file2_path = path2 + file2
            match_possibility = sf_match_possibility(path1, path2, file1, file2)
            if match_possibility > 50:
                sf_sync_file(file1_path, file2_path)
                break
            elif match_possibility == 50:
                sf_ask_operation()

        else:
            sf_sync_file(file1_path, path2 + file1, no_judge=True)
    for file2 in all_files_2:
        file2_path = path2 + file2
        if file2 not in all_files_1:
            sf_sync_file(file2_path, path1 + file2, no_judge=True)


def test_syncfile():
    path_1 = r"C:\Users\25674\Desktop\attempt"
    path_2 = r"C:\Users\25674\Desktop\test"
    sf_operate(path_1, path_2)


def ending_code():
    pass


def mainprocess():
    cf = configparser.ConfigParser()
    sf = configparser.ConfigParser()
    mf = configparser.ConfigParser()
    set_data_path()
    first_visit = False
    if not find_last_edit():
        first_visit = True
    asktime_plus()
    load_icon()
    cf.read(cf_data_path + r'Cleanfile_data.ini')
    sf.read(sf_data_path + r'Syncfile_data.ini')
    mf.read(mf_data_path + r"Movefile_data.ini")

    if first_visit:
        ask_info(cf_first_ask=True)
    elif cf_data_error():
        ask_info(cf_error=True)
    elif mf.getint("General", "asktime_today") > 1:
        ask_info(cf_muti_ask=True)
    else:
        try:
            cf_operate(cf_data_path + r'Cleanfile_data.ini')
            cf_show_notice()
        except:
            pass
        finally:
            ending_code()

if __name__ == '__main__':
    mainprocess()
