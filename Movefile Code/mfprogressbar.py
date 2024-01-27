import tkinter.messagebox
from threading import Thread
from tkinter import ttk

import LT_Dic
from mf_const import MF_ICON_PATH
from mttkinter import mtTkinter as tk


# The ProgressBar class generate a root used to display the progress of a task.
class MFProgressBar:
    def __init__(self, title, label1, label2, lang_num, hidden=False):
        self.initialization_done = False
        self.hidden = hidden
        self.title = title
        self.label1 = label1
        self.label2 = label2
        self.label_dic = LT_Dic.progress_root_label_dic
        self.lang_num = lang_num
        self.stop_running_flag = False

        """
        self.main_progress_label = None
        self.main_progress_bar = None
        self.current_file_label = None
        self.show_running_bar = None
        self.progress_root = None
        self.roll_bar = None
        """

    def set_label1(self, content, add_value=False):
        if not self.hidden and not self.stop_running_flag:
            self.main_progress_label.config(text=content)
            if add_value:
                self.main_progress_bar.step(1)
                self.progress_root.update_idletasks()

    def set_label2(self, content):
        if not self.hidden and not self.stop_running_flag:
            self.current_file_label.config(text=content)

    def set_maximum(self, num):
        if not self.hidden:
            self.main_progress_bar.config(maximum=num)
            self.main_progress_bar.config(value=0)
            self.progress_root.update_idletasks()

    def get_value(self):
        if not self.hidden and not self.stop_running_flag:
            return self.main_progress_bar['value']

    def withdraw_root(self):
        if not self.hidden and not self.stop_running_flag:
            self.progress_root.withdraw()

    def destroy_root(self):
        if not self.hidden and not self.stop_running_flag:
            self.progress_root.destroy()
        self.stop_running_flag = True

    def launch(self, root_master):
        self.progress_root = tk.Toplevel(root_master)
        if self.hidden:
            self.progress_root.withdraw()
        self.progress_root.title(self.title)
        self.progress_root.geometry('420x115')
        self.progress_root.iconbitmap(MF_ICON_PATH)
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
        if not self.hidden and not self.stop_running_flag:
            self.show_running_bar.start(10)

    def sync_bar_on_exit(self):
        if self.hidden or self.stop_running_flag:
            return
        if tkinter.messagebox.askyesno(title='Syncfile', message=self.label_dic['confirm_exit_text'][self.lang_num]):
            self.set_label1(self.label_dic['stopping_label'][self.lang_num])
            self.set_label2(self.label_dic['waiting_label'][self.lang_num])
            self.stop_running_flag = True

    def progress_root_destruction(self):
        if not self.hidden:
            self.progress_root.destroy()
