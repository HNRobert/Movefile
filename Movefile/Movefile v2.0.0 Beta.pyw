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
    global mf_data_path, cf_data_path, sf_data_path
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
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


'''
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

    if not os.path.exists(sf_data_path + r'Match_data.ini'):
        file = open(sf_data_path + r'Match_data.ini', 'w+', encoding='ANSI')
        file.close()
    cf.read(sf_data_path + r'Match_data.ini', encoding='ANSI')
    section_name = "Match_pairs"
    if not cf.has_section(section_name):
        cf.add_section(section_name)

    for folder_in_path1 in folders_on_surface_path:
        folder_matched = match_item(folder_in_path1, path_2)
        cf.set(section_name, folder_matched[0], folder_matched[1])
        cf.write(open(sf_data_path + r'Syncfile_data.ini', "w+", encoding='ANSI'))
'''


def sync_file(file_1, file_2, no_judge=False):
    new_file, prior_file = '', ''
    pas = False
    last_edit_time_1 = int(os.stat(file_1).st_mtime)
    last_edit_time_2 = int(os.stat(file_2).st_mtime)

    def creat_folder(target_path):
        target = target_path.split('\\')[:-1]
        try_des = ''
        for fold in target:
            try_des += fold + '\\'
            if not os.path.exists(try_des):
                os.mkdir(try_des)

    if no_judge:
        creat_folder(file_2)
        shutil.copyfile(file_1, file_2)
        pas = True
    elif last_edit_time_1 > last_edit_time_2:
        prior_file = file_2
        new_file = file_1
    elif last_edit_time_1 < last_edit_time_2:
        prior_file = file_1
        new_file = file_2
    else:
        pas = True
    if not pas:
        shutil.copyfile(new_file, prior_file)


def sf_operate(path1, path2):
    all_files_1 = sf_scan_files(path1)
    all_files_2 = sf_scan_files(path2)
    for file1 in all_files_1:
        file1_path = path1 + file1
        for file2 in all_files_2:
            file2_path = path2 + file2
            if sf_match_possibility(path1, path2, file1, file2) >= 50:
                sync_file(file1_path, file2_path)
        else:
            sync_file(file1_path, path2 + file1, no_judge=True)
    for file2 in all_files_2:
        file2_path = path2 + file2
        if file2 not in all_files_1:
            sync_file(file2_path, path1 + file2, no_judge=True)


def test_syncfile():
    path_1 = r"C:\Users\25674\Desktop\attempt"
    path_2 = r"C:\Users\25674\Desktop\test"
    sf_operate(path_1, path_2)


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


def ask_info(cf_error=False, cf_muti_ask=False, cf_first_ask=False):
    cf_data = configparser.ConfigParser()

    def cf_refresh_whitelist_entry(folder_names=None):
        if folder_names is None:
            folder_names = []
        try:
            global entry_keep_files
            global entry_keep_formats
            all_ends = []
            file_names = []
            item_names = os.listdir(entry_old_path.get())
            for file in item_names:
                file_end = '.' + file.split('.')[-1]
                if os.path.isfile(entry_old_path.get() + '\\' + file):
                    all_ends.append(file_end)
                    file_names.append(file)
            exist_ends = sorted(set(all_ends))
            entry_keep_files = Combopicker(master=entry_frame_keep_files, values=['全选'] + folder_names + file_names,
                                           frameheight=120)
            entry_keep_files.grid(row=2, column=1, ipadx=240, pady=5, sticky='W')
            entry_keep_formats = Combopicker(master=entry_frame_keep_formats, values=['全选'] + exist_ends,
                                             frameheight=90)
            entry_keep_formats.grid(row=3, column=1, ipadx=240, pady=0, sticky='W')
            entry_keep_files_x.grid_forget()
            entry_keep_formats_x.grid_forget()
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

    def cf_is_folder_move(state):
        if state:
            folders = os.listdir(entry_old_path.get())
            move_folder_names = []
            for folder in folders:
                if os.path.isdir(entry_old_path.get() + '\\' + folder):
                    move_folder_names.append(folder)
            cf_refresh_whitelist_entry(folder_names=move_folder_names)
        else:
            cf_refresh_whitelist_entry()

    root = tk.Tk()
    root.iconbitmap(mf_data_path + r'Movefile.ico')
    oldpath = tk.StringVar()
    newpath = tk.StringVar()
    root.title('Movefile Setting')
    root.geometry("800x280")

    label_old_path = ttk.Label(root, text="原文件夹路径：")
    label_old_path.grid(row=0, column=0, pady=5, sticky='E')
    entry_old_path = ttk.Entry(root, textvariable=oldpath)
    entry_old_path.grid(row=0, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    ttk.Button(root, text="浏览", command=lambda: cf_select_path(place='old', ori_content=entry_old_path.get())).grid(
        row=0,
        column=1,
        ipadx=3,
        sticky='E',
        padx=10)

    label_new_path = ttk.Label(root, text='新文件夹路径：')
    label_new_path.grid(row=1, column=0, pady=5, sticky='E')
    entry_new_path = ttk.Entry(root, textvariable=newpath)
    entry_new_path.grid(row=1, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    ttk.Button(root, text="浏览", command=lambda: cf_select_path(place='new', ori_content=entry_new_path.get())).grid(
        row=1,
        column=1,
        ipadx=3,
        sticky='E',
        padx=10)

    label_move_options = ttk.Label(root, text='文件移动选项：')
    label_move_options.grid(row=2, column=0, pady=5, sticky='E')
    entry_mode = tk.IntVar()
    option_mode_1 = ttk.Radiobutton(root, text="以项目最后修改时间为过期判断依据", variable=entry_mode, value=1)
    option_mode_1.grid(row=2, column=1, padx=10, ipadx=0, sticky='W')
    option_mode_2 = ttk.Radiobutton(root, text="以项目最后访问时间为过期判断依据", variable=entry_mode, value=2)
    option_mode_2.grid(row=2, column=1, padx=175, ipadx=0, sticky='E')
    is_folder_move = tk.BooleanVar()
    entry_folder_move = ttk.Checkbutton(root, text='移动项目包括文件夹', variable=is_folder_move,
                                        command=lambda: cf_is_folder_move(is_folder_move.get()))
    entry_folder_move.grid(row=2, column=1, padx=10, sticky='E')

    entry_frame_keep_files = tk.Frame(root)
    entry_frame_keep_files.grid(row=3, column=1, ipadx=5, sticky='E')
    label_keep_files = ttk.Label(root, text='保留项目选择：')
    label_keep_files.grid(row=3, column=0, pady=5, sticky='E')
    entry_keep_files_x = ttk.Entry(root)
    entry_keep_files_x.grid(row=3, column=1, padx=10, pady=5, ipadx=240, sticky='W')
    entry_keep_files_x.config(state=tk.DISABLED)

    entry_frame_keep_formats = tk.Frame(root)
    entry_frame_keep_formats.grid(row=4, column=1, pady=5, ipadx=5, sticky='E')
    label_keep_formats = ttk.Label(root, text='保留文件格式选择：')
    label_keep_formats.grid(row=4, column=0, sticky='E')
    entry_keep_formats_x = ttk.Entry(root)
    entry_keep_formats_x.grid(row=4, column=1, padx=10, pady=5, ipadx=240, sticky='W')
    entry_keep_formats_x.config(state=tk.DISABLED)

    label_time = ttk.Label(root, text='    过期时间设定(小时)：')
    label_time.grid(row=5, column=0, sticky='E')
    entry_time = ttk.Entry(root)
    entry_time.grid(row=5, column=1, padx=10, pady=5, ipadx=240, sticky='W')

    label_start_options = ttk.Label(root, text='系统选项：')
    label_start_options.grid(row=6, column=0, sticky='E')
    is_autorun = tk.BooleanVar()
    option_is_auto = ttk.Checkbutton(root, text='开机自动运行', variable=is_autorun)
    option_is_auto.grid(row=6, column=1, padx=10, sticky='NW')

    def cf_is_num():
        try:
            float(entry_time.get())
        except:
            return False
        else:
            return True

    def cf_has_blank():
        blank = 0
        if len(entry_old_path.get()) == 0:
            blank += 1
        elif len(entry_new_path.get()) == 0:
            blank += 1
        elif len(entry_time.get()) == 0:
            blank += 1
        elif entry_mode.get() == 0:
            blank += 1
        if blank == 0:
            return False
        else:
            return True

    def cf_path_error():
        try:
            os.listdir(entry_old_path.get())
            os.listdir(entry_new_path.get())
        except:
            return True
        else:
            return False

    def cf_savefile():
        if not cf_is_num():
            tkinter.messagebox.showwarning('Movefile', '警告：请在时间设定栏内输入数字')
        elif cf_has_blank():
            tkinter.messagebox.showwarning(title='Movefile',
                                           message='警告：请填写所有除白名单与开机自启勾选栏外的必填项目！')
        elif cf_path_error():
            tkinter.messagebox.showwarning(title='Movefile', message='警告：请填输入有效路径！（建议使用浏览）')
        else:
            if not os.path.exists(cf_data_path + r'Cleanfile_data.ini'):
                file = open(cf_data_path + r'Cleanfile_data.ini', 'w', encoding='ANSI')
                file.close()
            cf_data.read(cf_data_path + r'Cleanfile_data.ini')
            if not cf_data.has_section("Cleanfile_settings"):
                cf_data.add_section("Cleanfile_settings")
            cf_data.set("Cleanfile_settings", "old_path", entry_old_path.get())
            cf_data.set("Cleanfile_settings", "new_path", entry_new_path.get())
            cf_data.set("Cleanfile_settings", "pass_filename", entry_keep_files.get())
            cf_data.set("Cleanfile_settings", "pass_format", entry_keep_formats.get())
            cf_data.set("Cleanfile_settings", "set_hour", entry_time.get())
            cf_data.set("Cleanfile_settings", "mode", str(entry_mode.get()))
            cf_data.set("Cleanfile_settings", "autorun", str(is_autorun.get()))
            cf_data.set("Cleanfile_settings", "move_folder", str(is_folder_move.get()))
            cf_data.write(open(cf_data_path + r'Cleanfile_data.ini', "w+", encoding='ANSI'))
            tkinter.messagebox.showinfo(title='信息提示', message='信息保存成功！')
            bt2.config(state=tk.NORMAL)

    def cf_open_ini(ask_path=True):
        if ask_path:
            ini_path = tkinter.filedialog.askopenfilename()
        else:
            ini_path = cf_data_path + r'Cleanfile_data.ini'
        cf_file = configparser.ConfigParser()
        cf_file.read(ini_path)  # 获取配置文件
        if entry_old_path.get() != '':
            entry_old_path.delete(0, 'end')
        if entry_new_path.get() != '':
            entry_new_path.delete(0, 'end')
        entry_old_path.insert(0, cf_file.get('Cleanfile_settings', 'old_path'))  # 旧文件夹
        entry_new_path.insert(0, cf_file.get('Cleanfile_settings', 'new_path'))  # 新文件夹
        cf_refresh_whitelist_entry()
        if entry_keep_files.get() != '':
            entry_keep_files.delete(0, 'end')
        if entry_keep_formats.get() != '':
            entry_keep_formats.delete(0, 'end')
        if entry_time.get() != '':
            entry_time.delete(0, 'end')

        entry_keep_files.insert(0, cf_file.get('Cleanfile_settings', 'pass_filename'))  # 设置跳过白名单
        entry_keep_formats.insert(0, cf_file.get('Cleanfile_settings', 'pass_format'))  # 设置跳过格式
        entry_time.insert(0, cf_file.get('Cleanfile_settings', 'set_hour'))  # 设置过期时间(hour)
        entry_mode.set(cf_file.getint("Cleanfile_settings", 'mode'))  # 设置判断模式
        is_autorun.set(cf_file.get("Cleanfile_settings", 'autorun'))
        is_folder_move.set(cf_file.get('Cleanfile_settings', 'move_folder'))

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
            show_notice()

    # 创建按键
    bt1 = ttk.Button(root, text='保存', command=cf_savefile)
    bt1.grid(row=7, column=1, ipadx=100, pady=4, padx=10, sticky='W')
    bt2 = ttk.Button(root, text='继续', command=cf_continue_going)
    bt2.grid(row=7, column=1, ipadx=100, pady=4, padx=10, sticky='E')
    bt2.config(state=tk.DISABLED)

    # 菜单栏
    main_menu = tk.Menu(root)
    file_menu = tk.Menu(main_menu, tearoff=False)
    file_menu.add_command(label="读取配置文件", command=cf_open_ini, accelerator="Ctrl+O")
    file_menu.add_command(label="保存", command=cf_savefile, accelerator="Ctrl+S")
    help_menu = tk.Menu(main_menu, tearoff=False)
    help_menu.add_command(label="关于本软件", command=cf_helpfunc)
    help_menu.add_command(label="使用前注意事项", command=cf_help_before_use)
    help_menu.add_command(label="保留文件/文件格式选择", command=cf_help_keep)
    help_menu.add_command(label="过期时间设定", command=cf_help_timeset)
    main_menu.add_cascade(label="文件", menu=file_menu)
    main_menu.add_cascade(label="帮助", menu=help_menu)
    root.config(menu=main_menu)

    root.bind("<Control-o>", cf_open_ini)
    root.bind("<Control-O>", cf_open_ini)
    root.bind("<Control-s>", cf_savefile)
    root.bind("<Control-S>", cf_savefile)

    if cf_first_ask:
        cf_helpfunc()
        cf_help_before_use()
        entry_old_path.insert(0, get_desktop())
        entry_time.insert(0, '0')
        entry_mode.set(1)
        cf_refresh_whitelist_entry()

    if cf_muti_ask or cf_error:
        cf_refresh_whitelist_entry()
        cf_open_ini(ask_path=False)
        bt2.config(state=tk.NORMAL)

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
            Description=desc
        )
        return True
    except:
        pass
    return False


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


def cf_operate(filename):
    global old_path, new_path
    cf = configparser.ConfigParser()
    cf.read(filename)  # 获取配置文件
    old_path = cf.get('Cleanfile_settings', 'old_path')  # 旧文件夹
    new_path = cf.get('Cleanfile_settings', 'new_path')  # 新文件夹
    pass_file = cf.get('Cleanfile_settings', 'pass_filename').split(',')  # 设置跳过白名单
    pass_format = cf.get('Cleanfile_settings', 'pass_format').split(',')  # 设置跳过格式
    time_ = cf.getint('Cleanfile_settings', 'set_hour') * 3600  # 设置过期时间(hour)
    mode = cf.getint('Cleanfile_settings', 'mode')  # 设置判断模式
    is_move_folder = cf.get('Cleanfile_settings', 'move_folder')  # 设置是否移动文件夹
    if cf.get('Cleanfile_settings', 'autorun') == 'True':
        cf_set_startup(True)
    else:
        cf_set_startup(False)
    cf_move_dir(old__path=old_path, new__path=new_path, pass__file=pass_file, pass__format=pass_format, t=time_,
                check__mode=mode, is__move__folder=is_move_folder)


def show_notice():
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


def ending_code():
    pass


def mainprocess():
    cf = configparser.ConfigParser()
    mf = configparser.ConfigParser()
    set_data_path()
    asktime_plus()
    load_icon()
    cf.read(cf_data_path + r'Cleanfile_data.ini')
    mf.read(mf_data_path + r"Movefile_data.ini")
    from_root = False
    if not cf.has_section("Cleanfile_settings"):
        ask_info(cf_first_ask=True)
        from_root = True
    elif cf_data_error():
        ask_info(cf_error=True)
        from_root = True
    elif mf.getint("General", "asktime_today") > 1:
        ask_info(cf_muti_ask=True)
        from_root = True

    if not from_root:
        try:
            cf_operate(cf_data_path + r'Cleanfile_data.ini')
            show_notice()
        except:
            pass
        finally:
            ending_code()
    else:
        ending_code()


if __name__ == '__main__':
    test_syncfile()
