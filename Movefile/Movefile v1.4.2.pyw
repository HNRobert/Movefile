# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 17:07:30 2022

@author: Robert He
"""

vision = 'v1.4.2'
update_time = '2023/1/12-noon'

import os
import time
import shutil
import base64
import winreg
import winshell
import configparser
import tkinter as tk
from typing import Any
import tkinter.filedialog
import tkinter.ttk as ttk
import tkinter.messagebox
import Movefile_icon as icon

from datetime import datetime
from win10toast import ToastNotifier


class Picker(ttk.Frame):

    def __init__(self, master=None, activebackground='#b1dcfb', values=None, entry_wid=None, activeforeground='black',
                 selectbackground='#003eff', selectforeground='white', command=None, borderwidth=1, relief="solid",
                 frameheight=120):

        if values is None:
            values = []
        self._selected_item = None
        self._frameheight = frameheight
        self._values = values

        self._entry_wid = entry_wid

        self._sel_bg = selectbackground
        self._sel_fg = selectforeground

        self._act_bg = activebackground
        self._act_fg = activeforeground

        self._command = command
        self.index = 0
        ttk.Frame.__init__(self, master, borderwidth=borderwidth, height=10, relief=relief)

        self.bind("<FocusIn>", lambda event: self.event_generate('<<PickerFocusIn>>'))
        self.bind("<FocusOut>", lambda event: self.event_generate('<<PickerFocusOut>>'))
        f = tk.LabelFrame(self)
        f.pack(fill='x')
        self.canvas = tk.Canvas(f, scrollregion=(0, 0, 500, (len(self._values) * 23 + 3)))
        vbar = tk.Scrollbar(f, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        frame = tk.Frame(self.canvas)
        vbar.config(command=self.canvas.yview)
        self.canvas.create_window((0, 0,), window=frame, anchor='nw', tags='frame')

        self.canvas.config(highlightthickness=0)  # 去掉选中边框
        vbar.config(command=self.canvas.yview)
        self.canvas.config(width=300, height=self._frameheight)
        self.canvas.config(yscrollcommand=vbar.set)
        self.dict_checkbutton = {}
        self.dict_checkbutton_var = {}
        self.dict_intvar_item = {}
        for index, item in enumerate(self._values):
            self.dict_intvar_item[item] = tk.IntVar()
            self.dict_checkbutton[item] = ttk.Checkbutton(frame, text=item, variable=self.dict_intvar_item[item],
                                                          command=lambda ITEM=item: self._command(ITEM))
            self.dict_checkbutton[item].grid(row=index, column=0, sticky=tk.NSEW, padx=5)
            self.dict_intvar_item[item].set(0)
            if item in self._entry_wid.get().split(','):
                self.dict_intvar_item[item].set(1)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas.bind("<MouseWheel>", self.processwheel)
        frame.bind("<MouseWheel>", self.processwheel)
        for i in self.dict_checkbutton:
            self.dict_checkbutton[i].bind("<MouseWheel>", self.processwheel)
        self.bind("<MouseWheel>", self.processwheel)

    def processwheel(self, event):
        a = int(-event.delta)
        if a > 0:
            self.canvas.yview_scroll(1, tk.UNITS)
        else:
            self.canvas.yview_scroll(-1, tk.UNITS)


class Combopicker(ttk.Entry, Picker):
    values: list[Any] | Any

    def __init__(self, master, values=None, entryvar=None, entrywidth=None, entrystyle=None, onselect=None,
                 activebackground='#b1dcfb', activeforeground='black', selectbackground='#003eff',
                 selectforeground='white', borderwidth=1, relief="solid", frameheight=50):
        self.onselect = onselect
        self.relief = relief
        self.borderwidth = borderwidth
        if values is None:
            values = []
        self.values = values
        self.master = master
        self.activeforeground = activeforeground
        self.activebackground = activebackground
        self.selectbackground = selectbackground
        self.selectforeground = selectforeground
        self.frameheight = frameheight
        if entryvar is not None:
            self.entry_var = entryvar
        else:
            self.entry_var = tk.StringVar()
        self.show_var = tk.StringVar()
        entry_config = {}
        if entrywidth is not None:
            entry_config["width"] = entrywidth

        if entrystyle is not None:
            entry_config["style"] = entrystyle

        ttk.Entry.__init__(self, master, textvariable=self.show_var, **entry_config, state="")

        self._is_menuoptions_visible = False

        self.picker_frame = Picker(self.winfo_toplevel(), values=self.values, entry_wid=self.entry_var,
                                   activebackground=activebackground,
                                   activeforeground=activeforeground, selectbackground=selectbackground,
                                   selectforeground=selectforeground, command=self._on_selected_check,
                                   frameheight=self.frameheight)

        self.bind_all("<1>", self._on_click, "+")

        self.bind("<Escape>", lambda event: self.hide_picker())

    @property
    def current_value(self):
        try:

            value = self.entry_var.get()
            return value
        except ValueError:
            return None

    @current_value.setter
    def current_value(self, INDEX):
        self.entry_var.set(self.values.index(INDEX))

    def _on_selected_check(self, SELECTED):
        value = []
        all_name = '全选'

        if self.entry_var.get() != "" and self.entry_var.get() is not None:
            temp_value = self.entry_var.get()
            value = temp_value.split(",")
        if str(SELECTED) in value:
            if all_name == str(SELECTED):
                value.clear()  # 清空选项
            else:
                if all_name in value:
                    value.remove(all_name)
                value.remove(str(SELECTED))
                value.sort()
        else:
            if all_name == str(SELECTED):
                value = self.values
            else:
                value.append(str(SELECTED))
                value.sort()
        temp_value = ""
        for index, item in enumerate(value):
            if item != "":
                if index != 0:
                    temp_value += ","
                temp_value += str(item)
        self.entry_var.set(temp_value)
        if '全选' in self.entry_var.get().split(','):
            self.show_var.set(self.entry_var.get()[3::])
        else:
            self.show_var.set(self.entry_var.get())
        # 全选刷新
        if all_name == str(SELECTED):
            self.hide_picker()
            self.show_picker()

    def _on_click(self, event):
        str_widget = str(event.widget)

        if str_widget == str(self):
            if not self._is_menuoptions_visible:
                self.show_picker()
        else:
            if not str_widget.startswith(str(self.picker_frame)) and self._is_menuoptions_visible:
                self.hide_picker()

    def show_picker(self):

        if not self._is_menuoptions_visible:
            self.picker_frame = Picker(self.winfo_toplevel(), values=self.values, entry_wid=self.entry_var,
                                       frameheight=self.frameheight, activebackground=self.activebackground,
                                       activeforeground=self.activeforeground, selectbackground=self.selectbackground,
                                       selectforeground=self.selectforeground, command=self._on_selected_check)

            self.bind_all("<1>", self._on_click, "+")

            self.bind("<Escape>", lambda event: self.hide_picker())
            self.picker_frame.lift()
            self.picker_frame.place(in_=self, relx=0, rely=1, relwidth=1)
        self._is_menuoptions_visible = True

    def hide_picker(self):
        if self._is_menuoptions_visible:
            self.picker_frame.place_forget()
            # self.picker_frame.destroy()   # mac下直接销毁控件
        self._is_menuoptions_visible = False


def get_data():
    global data_path
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
    data_path = roaming_path + '\\Movefile\\'
    if 'Movefile' not in os.listdir(roaming_path):
        first_ask = True
        os.mkdir(data_path)
    else:
        first_ask = False
    return first_ask


def asktime_plus():
    gencf = configparser.ConfigParser()
    get_data()
    time_now = datetime.today()
    date = str(time_now.date())
    if not os.path.exists(data_path + r'Movefile_data.ini'):  # 创建配置文件
        file = open(data_path + r'Movefile_data.ini', 'w', encoding="ANSI")
        file.close()
    gencf.read(data_path + r'Movefile_data.ini')
    if not gencf.has_section("General"):
        gencf.add_section("General")
        gencf.set("General", "date", date)
        gencf.set("General", "asktime_today", '0')
    if gencf.get("General", "date") != str(date):
        gencf.set("General", "asktime_today", '0')
        gencf.set("General", "date", date)
    asktime_pre = gencf.getint("General", "asktime_today") + 1
    gencf.set("General", "asktime_today", str(asktime_pre))
    gencf.write(open(data_path + r'Movefile_data.ini', "w+", encoding='ANSI'))


def data_error():
    try:
        cf = configparser.ConfigParser()
        cf.read(data_path + r'Movefile_data.ini')  # 获取配置文件
        old_path_ = cf.get('Movefile_settings', 'old_path')  # 旧文件夹
        new_path_ = cf.get('Movefile_settings', 'new_path')  # 新文件夹
        passfile = cf.get('Movefile_settings', 'pass_filename').split(',')  # 设置跳过白名单
        passformat = cf.get('Movefile_settings', 'pass_format').split(',')  # 设置跳过格式
        time_ = cf.getint('Movefile_settings', 'set_hour') * 3600  # 设置过期时间(hour)
        mode_ = cf.getint('Movefile_settings', 'mode')
        move_folder = cf.get('Movefile_settings', 'move_folder')
        autorun_ = cf.get('Movefile_settings', 'autorun')
        move_dir(old__path=old_path_, new__path=new_path_, passfile=passfile, pass__format=passformat, t=time_,
                 mode=mode_, is__movefolder=False, test=True)
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


def loadicon():
    image = open(data_path + r'Movefile.ico', 'wb')
    image.write(base64.b64decode(icon.Movefile_ico))
    image.close()


def askinfo(error=False, muti_ask=False, first_ask=False):
    cf = configparser.ConfigParser()

    def refresh_whitelist_entry(folder_names=None):
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
            entry_keep_files = Combopicker(master=entryframe_keep_files, values=['全选'] + folder_names + file_names,
                                           frameheight=120)
            entry_keep_files.grid(row=2, column=1, ipadx=240, pady=5, sticky='W')
            entry_keep_formats = Combopicker(master=entryframe_keep_formats, values=['全选'] + exist_ends,
                                             frameheight=90)
            entry_keep_formats.grid(row=3, column=1, ipadx=240, pady=0, sticky='W')
            entry_keep_files_x.grid_forget()
            entry_keep_formats_x.grid_forget()
        except:
            pass

    def selectpath(place, ori_content):
        path_ = tkinter.filedialog.askdirectory()
        path_ = path_.replace("/", "\\")
        if path_ != '' and path_ != ori_content:
            if place == 'old':
                oldpath.set(path_)
                refresh_whitelist_entry()
            elif place == 'new':
                newpath.set(path_)

    def movefolder(state):
        if state:
            folders = os.listdir(entry_old_path.get())
            move_folder_names = []
            for folder in folders:
                if os.path.isdir(entry_old_path.get() + '\\' + folder):
                    move_folder_names.append(folder)
            refresh_whitelist_entry(folder_names=move_folder_names)
        else:
            refresh_whitelist_entry()

    root = tk.Tk()
    root.iconbitmap(data_path + r'Movefile.ico')
    oldpath = tk.StringVar()
    newpath = tk.StringVar()
    root.title('Movefile Setting')
    root.geometry("800x280")

    label_old_path = ttk.Label(root, text="原文件夹路径：")
    label_old_path.grid(row=0, column=0, pady=5, sticky='E')
    entry_old_path = ttk.Entry(root, textvariable=oldpath)
    entry_old_path.grid(row=0, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    ttk.Button(root, text="浏览", command=lambda: selectpath(place='old', ori_content=entry_old_path.get())).grid(row=0,
                                                                                                                  column=1,
                                                                                                                  ipadx=3,
                                                                                                                  sticky='E',
                                                                                                                  padx=10)

    label_new_path = ttk.Label(root, text='新文件夹路径：')
    label_new_path.grid(row=1, column=0, pady=5, sticky='E')
    entry_new_path = ttk.Entry(root, textvariable=newpath)
    entry_new_path.grid(row=1, column=1, padx=10, pady=5, ipadx=190, sticky='W')
    ttk.Button(root, text="浏览", command=lambda: selectpath(place='new', ori_content=entry_new_path.get())).grid(row=1,
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
    is_foldermove = tk.BooleanVar()
    entry_foldermove = ttk.Checkbutton(root, text='移动项目包括文件夹', variable=is_foldermove,
                                       command=lambda: movefolder(is_foldermove.get()))
    entry_foldermove.grid(row=2, column=1, padx=10, sticky='E')

    entryframe_keep_files = tk.Frame(root)
    entryframe_keep_files.grid(row=3, column=1, ipadx=5, sticky='E')
    label_keep_files = ttk.Label(root, text='保留项目选择：')
    label_keep_files.grid(row=3, column=0, pady=5, sticky='E')
    entry_keep_files_x = ttk.Entry(root)
    entry_keep_files_x.grid(row=3, column=1, padx=10, pady=5, ipadx=240, sticky='W')
    entry_keep_files_x.config(state=tk.DISABLED)

    entryframe_keep_formats = tk.Frame(root)
    entryframe_keep_formats.grid(row=4, column=1, pady=5, ipadx=5, sticky='E')
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

    # 创建输入框
    def is_num():
        try:
            float(entry_time.get())
        except:
            return False
        else:
            return True

    def has_blank():
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

    def path_error():
        try:
            os.listdir(entry_old_path.get())
            os.listdir(entry_new_path.get())
        except:
            return True
        else:
            return False

    def savefile():
        if not is_num():
            tkinter.messagebox.showwarning('Movefile', '警告：请在时间设定栏内输入数字')
        elif has_blank():
            tkinter.messagebox.showwarning(title='Movefile',
                                           message='警告：请填写所有除白名单与开机自启勾选栏外的必填项目！')
        elif path_error():
            tkinter.messagebox.showwarning(title='Movefile', message='警告：请填输入有效路径！（建议使用浏览）')
        else:
            if not os.path.exists(data_path + r'Movefile_data.ini'):
                file = open(data_path + r'Movefile_data.ini', 'w')
                file.close()
            cf.read(data_path + r'Movefile_data.ini')
            if not cf.has_section("Movefile_settings"):
                cf.add_section("Movefile_settings")
            cf.set("Movefile_settings", "old_path", entry_old_path.get())
            cf.set("Movefile_settings", "new_path", entry_new_path.get())
            cf.set("Movefile_settings", "pass_filename", entry_keep_files.get())
            cf.set("Movefile_settings", "pass_format", entry_keep_formats.get())
            cf.set("Movefile_settings", "set_hour", entry_time.get())
            cf.set("Movefile_settings", "mode", str(entry_mode.get()))
            cf.set("Movefile_settings", "autorun", str(is_autorun.get()))
            cf.set("Movefile_settings", "move_folder", str(is_foldermove.get()))
            cf.write(open(data_path + r'Movefile_data.ini', "w+", encoding='ANSI'))
            tkinter.messagebox.showinfo(title='信息提示', message='信息保存成功！')
            bt2.config(state=tk.NORMAL)

    def openini(askpath=True):
        if askpath:
            inipath = tkinter.filedialog.askopenfilename()
        else:
            inipath = data_path + r'Movefile_data.ini'
        cffile = configparser.ConfigParser()
        cffile.read(inipath)  # 获取配置文件
        if entry_old_path.get() != '':
            entry_old_path.delete(0, 'end')
        if entry_new_path.get() != '':
            entry_new_path.delete(0, 'end')
        entry_old_path.insert(0, cffile.get('Movefile_settings', 'old_path'))  # 旧文件夹
        entry_new_path.insert(0, cffile.get('Movefile_settings', 'new_path'))  # 新文件夹
        refresh_whitelist_entry()
        if entry_keep_files.get() != '':
            entry_keep_files.delete(0, 'end')
        if entry_keep_formats.get() != '':
            entry_keep_formats.delete(0, 'end')
        if entry_time.get() != '':
            entry_time.delete(0, 'end')

        entry_keep_files.insert(0, cffile.get('Movefile_settings', 'pass_filename'))  # 设置跳过白名单
        entry_keep_formats.insert(0, cffile.get('Movefile_settings', 'pass_format'))  # 设置跳过格式
        entry_time.insert(0, cffile.get('Movefile_settings', 'set_hour'))  # 设置过期时间(hour)
        entry_mode.set(cffile.getint("Movefile_settings", 'mode'))  # 设置判断模式
        is_autorun.set(cffile.get("Movefile_settings", 'autorun'))
        is_foldermove.set(cffile.get('Movefile_settings', 'move_folder'))

    def helpfunc():
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

    def help_keep():
        tkinter.messagebox.showinfo(title='Movefile', message="""保留项目/文件格式选择功能详解：

保留项目选择：
选中的项目不会被转移

保留文件格式选择：
某种格式类型的文件都不会被转移
比如选中'.lnk'，即表示原文件夹中所有的快捷方式不会被转移""")

    def help_timeset():
        tkinter.messagebox.showinfo(title='Movefile', message="""过期时间功能详解：

本软件可以获取文件的最后修改、访问时间
可以保留一定时间内修改/访问过的文件
例如若将过期时间设为"48"，判定方式设为"以最后修改时间为依据"
则运行日期前两天内修改过的文件不会被删除
如果不想用此方法，则过期时间设为"0"即可""")

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
  且无法按上面的解释修复
  请联系作者（QQ:2567466856）,我会尽快尝试帮你修复""")

    def continue_going(onlyquit=False):
        root.quit()
        root.destroy()
        if not onlyquit:
            operate(data_path + r'Movefile_data.ini')
            show_notice()

    # 创建按键
    bt1 = ttk.Button(root, text='保存', command=savefile)
    bt1.grid(row=7, column=1, ipadx=100, pady=4, padx=10, sticky='W')
    bt2 = ttk.Button(root, text='继续', command=continue_going)
    bt2.grid(row=7, column=1, ipadx=100, pady=4, padx=10, sticky='E')
    bt2.config(state=tk.DISABLED)

    # 菜单栏
    main_menu = tk.Menu(root)
    filemenu = tk.Menu(main_menu, tearoff=False)
    filemenu.add_command(label="读取配置文件", command=openini, accelerator="Ctrl+O")
    filemenu.add_command(label="保存", command=savefile, accelerator="Ctrl+S")
    helpmenu = tk.Menu(main_menu, tearoff=False)
    helpmenu.add_command(label="关于本软件", command=helpfunc)
    helpmenu.add_command(label="使用前注意事项", command=help_before_use)
    helpmenu.add_command(label="保留文件/文件格式选择", command=help_keep)
    helpmenu.add_command(label="过期时间设定", command=help_timeset)
    main_menu.add_cascade(label="文件", menu=filemenu)
    main_menu.add_cascade(label="帮助", menu=helpmenu)
    root.config(menu=main_menu)

    root.bind("<Control-o>", openini)
    root.bind("<Control-O>", openini)
    root.bind("<Control-s>", savefile)
    root.bind("<Control-S>", savefile)

    if first_ask:
        helpfunc()
        help_before_use()
        entry_old_path.insert(0, get_desktop())
        entry_time.insert(0, '0')
        entry_mode.set(1)
        refresh_whitelist_entry()

    if muti_ask or error:
        refresh_whitelist_entry()
        openini(askpath=False)
        bt2.config(state=tk.NORMAL)

        if error:
            tkinter.messagebox.showwarning(title='Movefile', message='''错误：配置信息无效！
请尽量不要手动更改ini配置文件''')

    root.mainloop()


def move_dir(old__path, new__path, passfile, pass__format, t, mode, is__movefolder, test=False):
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
        if (not is_folder and ((file not in passfile) or pf)) or (
                is_folder and file not in passfile and is__movefolder):  # 判断移动条件
            if mode == 1:
                last = int(os.stat(file_path).st_mtime)  # 最后一次修改的时间 (Option 1)
            elif mode == 2:
                last = int(os.stat(file_path).st_atime)  # 最后一次访问的时间 (Option 2)
            else:
                raise
            if (now - last >= t) and not test:  # 移动过期文件
                try:
                    shutil.move(file_path, new__path)
                    Movename += (file + ',  ')
                except:
                    Errorname += (file + ',  ')


def create_shortcut(bin_path: str, name: str, _icon: str, desc: str):
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


def set_startup(autorun):
    # 将快捷方式添加到自启动目录
    # 获取用户名
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
    startup_path = os.path.join(roaming_path + r"Microsoft\Windows\Start Menu\Programs\Startup")
    bin_path = r"Movefile " + vision + ".exe"
    link_path = startup_path + "\\Movefile"
    desc = "自动转移文件程序"
    icon_ = data_path + r'Movefile.ico'
    if autorun:
        create_shortcut(bin_path, link_path, icon_, desc)
    else:
        if os.path.exists(link_path + '.lnk'):
            os.remove(link_path + '.lnk')


def operate(filename):
    global old_path, new_path
    cf = configparser.ConfigParser()
    cf.read(filename)  # 获取配置文件
    old_path = cf.get('Movefile_settings', 'old_path')  # 旧文件夹
    new_path = cf.get('Movefile_settings', 'new_path')  # 新文件夹
    passfile = cf.get('Movefile_settings', 'pass_filename').split(',')  # 设置跳过白名单
    passformat = cf.get('Movefile_settings', 'pass_format').split(',')  # 设置跳过格式
    time_ = cf.getint('Movefile_settings', 'set_hour') * 3600  # 设置过期时间(hour)
    mode = cf.getint('Movefile_settings', 'mode')  # 设置判断模式
    is_movefolder = cf.get('Movefile_settings', 'move_folder')  # 设置是否移动文件夹
    if cf.get('Movefile_settings', 'autorun') == 'True':
        set_startup(True)
    else:
        set_startup(False)
    move_dir(old_path, new_path, passfile, passformat, time_, mode, is_movefolder)


def show_notice():
    toaster = ToastNotifier()
    new_folder = new_path.split('\\')[-1]
    old_folder = old_path.split('\\')[-1]
    if len(Movename) > 0:
        toaster.show_toast('These Files from ' + old_folder + ' are moved to ' + new_folder + ':',
                           Movename,
                           icon_path=data_path + r'Movefile.ico',
                           duration=10,
                           threaded=False)
    else:
        toaster.show_toast(old_folder + ' is pretty clean now',
                           'Nothing is moved away',
                           icon_path=data_path + r'Movefile.ico',
                           duration=10,
                           threaded=False)
    if len(Errorname) > 0:
        toaster.show_toast("Couldn't move files",
                           Errorname + """
无法被移动，请在关闭文件或移除重名文件后重试""",
                           icon_path=data_path + r'Movefile.ico',
                           duration=10,
                           threaded=False)


def ending_code():
    pass


def mainprocess():
    cf = configparser.ConfigParser()
    asktime_plus()
    loadicon()
    cf.read(data_path + r'Movefile_data.ini')
    from_root = False
    if not cf.has_section("Movefile_settings"):
        askinfo(first_ask=True)
        from_root = True
    elif data_error():
        askinfo(error=True)
        from_root = True
    elif cf.getint("General", "asktime_today") > 1:
        askinfo(muti_ask=True)
        from_root = True

    if not from_root:
        try:
            operate(data_path + r'Movefile_data.ini')
            show_notice()
        except:
            pass
        finally:
            ending_code()
    else:
        ending_code()


if __name__ == '__main__':
    mainprocess()
