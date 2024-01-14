

import configparser
from doctest import BLANKLINE_MARKER
import os
import time
import tkinter.filedialog
import tkinter.messagebox
from threading import Thread
from tkinter import ttk

import LT_Dic
from cleanfile import cf_autorun_operation, cf_move_dir
from ComBoPicker import Combopicker
from mf_const import (CF_CONFIG_PATH, DESKTOP_PATH, MF_CONFIG_PATH,
                      MF_ICON_PATH, SF_CONFIG_PATH)
from mf_mods import (detect_removable_disks_thread, language_num,
                     list_saving_data, mf_log, mf_toaster,
                     put_desktop_shortcut, scan_removable_disks, set_auto_quit,
                     set_startup)
from mttkinter import mtTkinter as tk
from PIL import Image
from pystray import Icon, Menu, MenuItem
from syncfile import sf_autorun_operation, sf_sync_dir
from win32api import GetVolumeInformation

from Movefile import gvar


def make_ui(first_visit=False, startup_visit=False, visits_today=0, quit_after_autorun=False):
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
    general_data.read(MF_CONFIG_PATH)
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
            suffix = item.name.split('.')[-1]
            if item.is_file() and (suffix == 'lnk' and cf_is_lnk_move.get() or suffix != 'lnk'):
                file_names.append(item.name)
                all_ends.append('.' + suffix)
            elif item.is_dir() and cf_is_folder_move.get():
                folder_names.append(item.name)

        exist_ends = sorted(set(filter(lambda suff: suff != '.lnk', all_ends)))

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

    def set_preview(result=[], mode='cf', content=''):
        """
        The function `set_preview` is used to update the preview text widget based on the given parameters.

        :param result: The `result` parameter is a list that contains information about the items to be previewed. Each item in the list is a tuple with three elements: the item's name, the item's path, and destination path
        :param mode: The `mode` parameter is used to determine the type of preview to be displayed. It can have two possible values: 'cf' or 'sf', defaults to cf (optional)
        :param content: The `content` parameter is a string that represents the content to be displayed in the preview_text widget. If this parameter is not empty, the content will be inserted directly into the widget
        """
        preview_text.config(state='normal')
        preview_text.delete('1.0', tk.END)
        if content:
            preview_text.insert(tk.END, content)
        elif len(result) == 0:  # no item in result
            preview_text.insert(
                tk.END, LT_Dic.cfdic['preview_no_item'][lang_num] + '\n')
        elif mode == 'cf':
            preview_text.insert(
                tk.END, LT_Dic.cfdic['preview_src'][lang_num] + os.path.dirname(result[0][1]) + '\n')
            preview_text.insert(
                tk.END, LT_Dic.cfdic['preview_dest'][lang_num] + result[0][2] + '\n')
            preview_text.insert(
                tk.END, '---------------------------------------------------------------------------\n')
            preview_text.insert(
                tk.END, LT_Dic.cfdic['preview_item'][lang_num] + '\n')
            for line in result:
                s_path = os.path.basename(line[1])
                preview_text.insert(tk.END, s_path + '\n')
        elif mode == 'sf':
            pass
        else:
            assert False, "No Such Mode"
        preview_text.insert(tk.END, '\n')
        preview_text.config(state='disabled')

    def set_language(lang_number):
        label_choose_state_text.set(
            LT_Dic.r_label_text_dic['label_choose_state'][lang_number])
        option_is_cleanfile_text.set(
            LT_Dic.r_label_text_dic['option_is_cleanfile'][lang_number])
        option_is_syncfile_text.set(
            LT_Dic.r_label_text_dic['option_is_syncfile'][lang_number])
        current_save_name.set(
            LT_Dic.r_label_text_dic['current_save_name'][lang_number])
        cf_label_old_path_text.set(
            LT_Dic.r_label_text_dic['cf_label_old_path'][lang_number])
        cf_browse_old_path_button_text.set(
            LT_Dic.r_label_text_dic['cf_browse_old_path_button'][lang_number])
        cf_browse_new_path_button_text.set(
            LT_Dic.r_label_text_dic['cf_browse_new_path_button'][lang_number])
        cf_label_new_path_text.set(
            LT_Dic.r_label_text_dic['cf_label_new_path'][lang_number])
        cf_label_move_options_text.set(
            LT_Dic.r_label_text_dic['cf_label_move_options'][lang_number])
        cf_option_folder_move_text.set(
            LT_Dic.r_label_text_dic['cf_option_folder_move'][lang_number])
        cf_option_move_lnk_text.set(
            LT_Dic.r_label_text_dic['cf_option_move_lnk'][lang_number])
        cf_label_adv_text.set(
            LT_Dic.r_label_text_dic['cf_label_adv'][lang_number])
        cf_option_adv_text.set(
            LT_Dic.r_label_text_dic['cf_option_adv'][lang_number])
        cf_option_mode_1_text.set(
            LT_Dic.r_label_text_dic['cf_option_mode_1'][lang_number])
        cf_option_mode_2_text.set(
            LT_Dic.r_label_text_dic['cf_option_mode_2'][lang_number])
        cf_label_keep_files_text.set(
            LT_Dic.r_label_text_dic['cf_label_keep_files'][lang_number])
        cf_label_keep_formats_text.set(
            LT_Dic.r_label_text_dic['cf_label_keep_formats'][lang_number])
        cf_label_expire_options_text.set(
            LT_Dic.r_label_text_dic['cf_label_expire_options'][lang_number])
        cf_label_time_text.set(
            LT_Dic.r_label_text_dic['cf_label_time'][lang_number])
        label_preview_text.set(
            LT_Dic.r_label_text_dic['label_preview'][lang_number])
        preview_button_text.set(
            LT_Dic.r_label_text_dic['preview_button'][lang_number])
        cf_label_start_options_text.set(
            LT_Dic.r_label_text_dic['cf_label_start_options'][lang_number])
        cf_option_is_auto_text.set(
            LT_Dic.r_label_text_dic['cf_option_is_auto'][lang_number])

        sf_label_place_mode_text.set(
            LT_Dic.r_label_text_dic['sf_label_place_mode'][lang_number])
        sf_option_mode_usb_text.set(
            LT_Dic.r_label_text_dic['sf_option_mode_usb'][lang_number])
        sf_option_mode_local_text.set(
            LT_Dic.r_label_text_dic['sf_option_mode_local'][lang_number])
        sf_label_path_1_text.set(
            LT_Dic.r_label_text_dic['sf_label_path_1'][lang_number][0])
        sf_label_path_2_text.set(
            LT_Dic.r_label_text_dic['sf_label_path_2'][lang_number][0])
        sf_browse_path_1_button_text.set(
            LT_Dic.r_label_text_dic['sf_browse_path_1_button'][lang_number])
        sf_browse_path_2_button_text.set(
            LT_Dic.r_label_text_dic['sf_browse_path_2_button'][lang_number])
        sf_no_disk_text.set(LT_Dic.r_label_text_dic['sf_no_disk'][lang_number])
        sf_label_mode_text.set(
            LT_Dic.r_label_text_dic['sf_label_mode'][lang_number])
        sf_option_mode_double_text.set(
            LT_Dic.r_label_text_dic['sf_option_mode_double'][lang_number])
        sf_option_mode_single_text.set(
            LT_Dic.r_label_text_dic['sf_option_mode_single'][lang_number])
        sf_label_lock_folder_text.set(
            LT_Dic.r_label_text_dic['sf_label_lock_folder'][lang_number])
        sf_browse_lockfolder_button_text.set(
            LT_Dic.r_label_text_dic['sf_browse_lockfolder_button'][lang_number])
        sf_label_lock_file_text.set(
            LT_Dic.r_label_text_dic['sf_label_lock_file'][lang_number])
        sf_browse_lockfile_button_text.set(
            LT_Dic.r_label_text_dic['sf_browse_lockfile_button'][lang_number])
        sf_label_autorun_text.set(
            LT_Dic.r_label_text_dic['sf_label_autorun'][lang_number])
        sf_option_autorun_text.set(
            LT_Dic.r_label_text_dic['sf_option_autorun'][lang_number])
        select_all_text.set(LT_Dic.r_label_text_dic['select_all'][lang_number])

        save_button_text.set(
            LT_Dic.r_label_text_dic['save_button'][lang_number])
        continue_button_text.set(
            LT_Dic.r_label_text_dic['continue_button'][lang_number])

        file_menu_text.set(LT_Dic.r_label_text_dic['file_menu'][lang_number])
        readfile_menu_text.set(
            LT_Dic.r_label_text_dic['readfile_menu'][lang_number])
        savefile_menu_text.set(
            LT_Dic.r_label_text_dic['savefile_menu'][lang_number])
        exit_menu_text.set(LT_Dic.r_label_text_dic['exit_menu'][lang_number])
        option_menu_text.set(
            LT_Dic.r_label_text_dic['option_menu'][lang_number])
        autorun_menu_text.set(
            LT_Dic.r_label_text_dic['autorun_menu'][lang_number])
        auto_quit_menu_text.set(
            LT_Dic.r_label_text_dic['auto_quit_menu'][lang_number])
        desktop_shortcut_text.set(
            LT_Dic.r_label_text_dic['desktop_shortcut'][lang_number])
        language_menu_text.set(
            LT_Dic.r_label_text_dic['language_menu'][lang_number])
        help_menu_text.set(LT_Dic.r_label_text_dic['help_menu'][lang_number])
        about_menu_text.set(LT_Dic.r_label_text_dic['about_menu'][lang_number])
        precautions_menu_text.set(
            LT_Dic.r_label_text_dic['precautions_menu'][lang_number])
        cf_keep_menu_text.set(
            LT_Dic.r_label_text_dic['cf_keep_menu'][lang_number])
        cf_expire_menu_text.set(
            LT_Dic.r_label_text_dic['cf_expire_menu'][lang_number])
        sf_removable_menu_text.set(
            LT_Dic.r_label_text_dic['sf_removable_menu'][lang_number])
        sf_lock_menu_text.set(
            LT_Dic.r_label_text_dic['sf_lock_menu'][lang_number])
        menu_hide_text.set(LT_Dic.r_label_text_dic['menu_hide'][lang_number])

        taskbar_setting_text.set(
            LT_Dic.r_label_text_dic['taskbar_setting'][lang_number])
        taskbar_hide_text.set(
            LT_Dic.r_label_text_dic['taskbar_hide'][lang_number])
        taskbar_exit_text.set(
            LT_Dic.r_label_text_dic['taskbar_exit'][lang_number])

    class Place:
        def __init__(self, mode=None, sf_place=None):
            self.mode = mode
            label_choose_state.grid(row=0, column=0, pady=4, sticky='E')
            blank.grid(row=3, column=1, padx=321, pady=4, sticky='W')
            option_is_cleanfile.grid(
                row=0, column=1, padx=10, pady=5, sticky='W')
            option_is_syncfile.grid(
                row=0, column=1, padx=100, pady=5, sticky='W')
            label_current_save_name.grid(row=0, column=1, padx=10, sticky='E')
            blank_pix.grid(row=114, column=0, ipadx=67, pady=4,
                           padx=0, sticky='E')  # This is a Placeholder
            label_preview.grid(
                row=9, column=0, pady=5, sticky='EN')
            preview_button.grid(
                row=9, column=0, pady=22, ipady=50, ipadx=3, sticky='ES')
            preview_text.grid(row=9, rowspan=1, column=1, padx=10,
                              pady=5, ipadx=127, ipady=50, sticky='NW')
            preview_xscrollbar.grid(
                row=9, rowspan=1, column=1, padx=10, pady=5, ipadx=288, sticky='WS')
            preview_yscrollbar.grid(
                row=9, rowspan=1, column=1, padx=10, pady=5, ipady=50, sticky='EN')
            save_button.grid(row=12, column=1, ipadx=100,
                             pady=4, padx=10, sticky='W')
            continue_button.grid(row=12, column=1, ipadx=100,
                                 pady=4, padx=10, sticky='E')
            # continue_button.config(state=tk.DISABLED)
            if self.mode == 'cf':
                self.cf_state()
            elif self.mode == 'sf':
                self.sf_state(sf_place)
            # self.judge_button_pix()

        @staticmethod
        def cf_fold_adv(state=False):
            if state:
                cf_label_old_path.grid(row=4, column=0, pady=5, sticky='E')
                cf_label_keep_files.grid(row=5, column=0, pady=5, sticky='E')
                cf_label_keep_formats.grid(row=6, column=0, pady=5, sticky='E')
                cf_label_expire_options.grid(
                    row=7, column=0, pady=4, sticky='E')
                cf_label_time.grid(row=8, column=0, pady=5, sticky='E')

                cf_entry_old_path.grid(
                    row=4, column=1, padx=10, pady=5, ipadx=190, sticky='W')
                cf_browse_old_path_button.grid(
                    row=4, column=1, ipadx=3, sticky='E', padx=10)
                cf_entry_keep_files.grid(
                    row=5, column=1, padx=10, pady=5, ipadx=240, sticky='W')
                cf_entry_frame_keep_files.grid(row=5, column=1, sticky='W')
                cf_entry_keep_formats.grid(
                    row=6, column=1, padx=10, pady=5, ipadx=240, sticky='W')
                cf_entry_frame_keep_formats.grid(row=6, column=1, sticky='W')
                cf_option_mode_1.grid(
                    row=7, column=1, padx=10, ipadx=0, sticky='W')
                temp_adjust_value = [150, 180]
                cf_option_mode_2.grid(
                    row=7, column=1, padx=temp_adjust_value[lang_num], ipadx=0, sticky='W')
                cf_entry_time.grid(row=8, column=1, padx=10,
                                   pady=0, ipadx=240, sticky='W')
                root.geometry('800x520')
            else:
                cf_label_old_path.grid_forget()
                cf_entry_old_path.grid_forget()
                cf_browse_old_path_button.grid_forget()
                cf_label_keep_files.grid_forget()
                cf_label_keep_formats.grid_forget()
                cf_label_expire_options.grid_forget()
                cf_label_time.grid_forget()
                cf_entry_keep_files.grid_forget()
                cf_entry_frame_keep_files.grid_forget()
                cf_entry_keep_formats.grid_forget()
                cf_entry_frame_keep_formats.grid_forget()
                cf_option_mode_1.grid_forget()
                cf_option_mode_2.grid_forget()
                cf_entry_time.grid_forget()
                root.geometry('800x360')

        @staticmethod
        def sf_change_place_mode(mode):
            if mode == 'movable':
                label_index = 0
                sf_browse_path_1_button.grid_forget()
                sf_entry_select_removable.grid(
                    row=3, column=1, padx=10, pady=5, ipadx=231, sticky='W')
            else:
                label_index = 1
                sf_browse_path_1_button.grid(
                    row=3, column=1, ipadx=3, sticky='E', padx=10)
                sf_entry_select_removable.grid_forget()
            sf_label_path_1_text.set(
                LT_Dic.r_label_text_dic['sf_label_path_1'][lang_num][label_index])
            sf_label_path_2_text.set(
                LT_Dic.r_label_text_dic['sf_label_path_2'][lang_num][label_index])
            sf_option_autorun_text.set(
                LT_Dic.r_label_text_dic['sf_option_autorun'][lang_num][label_index])

        @staticmethod
        def exchange_preview_text():
            pre_preview_text = opp_preview_text.get()
            opp_preview_text.set(preview_text.get('1.0', tk.END))
            set_preview(content=pre_preview_text)

        """
        @staticmethod
        def judge_button_pix():
            def adjust_widget(mount: list):
                
                cf_option_lnk_move.grid(
                    row=2, column=1, padx=mount[2], ipadx=0, sticky='W')

            if lang_num == 0:
                adjust_widget([100, 100, 150])
            elif lang_num == 1:
                adjust_widget([100, 100, 150])
        """

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

            cf_label_new_path.grid(row=1, column=0, pady=5, sticky='E')
            cf_label_move_options.grid(row=2, column=0, pady=3, sticky='E')
            cf_label_adv.grid(row=3, column=0, pady=3, sticky='E')
            cf_label_start_options.grid(row=11, column=0, sticky='E')

            cf_entry_new_path.grid(
                row=1, column=1, padx=10, pady=5, ipadx=190, sticky='W')
            cf_browse_new_path_button.grid(
                row=1, column=1, ipadx=3, sticky='E', padx=10)
            cf_option_folder_move.grid(row=2, column=1, padx=10, sticky='W')
            cf_option_lnk_move.grid(row=2, column=1, padx=150, sticky='W')
            cf_option_adv.grid(row=3, column=1, padx=10, sticky='W')

            cf_option_is_auto.grid(row=11, column=1, padx=10, sticky='NW')
            Place.cf_fold_adv(cf_unfold_adv.get())
            Place.exchange_preview_text()

            current_save_name.set(
                LT_Dic.r_label_text_dic['current_save_name'][lang_num] + current_cf_save_name.get())

        @staticmethod
        def sf_state(placemode=None):
            cf_entry_old_path.grid_forget()
            cf_browse_old_path_button.grid_forget()
            cf_entry_new_path.grid_forget()
            cf_browse_new_path_button.grid_forget()
            cf_option_folder_move.grid_forget()
            cf_option_lnk_move.grid_forget()
            cf_entry_keep_files.grid_forget()
            cf_entry_keep_formats.grid_forget()
            cf_entry_frame_keep_files.grid_forget()
            cf_entry_frame_keep_formats.grid_forget()
            cf_option_mode_1.grid_forget()
            cf_option_mode_2.grid_forget()
            cf_entry_time.grid_forget()
            cf_option_is_auto.grid_forget()
            cf_label_old_path.grid_forget()
            cf_label_new_path.grid_forget()
            cf_label_expire_options.grid_forget()
            cf_label_keep_files.grid_forget()
            cf_label_keep_formats.grid_forget()
            cf_label_expire_options.grid_forget()
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
            sf_label_autorun.grid(row=11, column=0, sticky='E')
            sf_option_autorun.grid(row=11, column=1, padx=10, sticky='W')
            root.geometry('800x468')
            Place.exchange_preview_text()
            current_save_name.set(
                LT_Dic.r_label_text_dic['current_save_name'][lang_num] + current_sf_save_name.get())

    root = tk.Tk()
    if startup_visit:
        root.withdraw()
    root.iconbitmap(MF_ICON_PATH)
    root.title('Movefile Setting')
    root.geometry("800x360")
    root.resizable(False, False)
    root.attributes('-topmost', True)
    root.attributes('-topmost', False)
    root.update_idletasks()
    root.protocol('WM_DELETE_WINDOW', lambda: exit_program())
    # 重新定义点击关闭按钮的处理

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
    cf_option_folder_move_text = tk.StringVar()
    cf_option_move_lnk_text = tk.StringVar()
    cf_label_adv_text = tk.StringVar()

    cf_option_adv_text = tk.StringVar()
    cf_label_keep_files_text = tk.StringVar()
    cf_label_keep_formats_text = tk.StringVar()
    cf_label_expire_options_text = tk.StringVar()
    cf_option_mode_1_text = tk.StringVar()
    cf_option_mode_2_text = tk.StringVar()
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

    label_preview_text = tk.StringVar()
    preview_button_text = tk.StringVar()
    opp_preview_text = tk.StringVar()
    select_all_text = tk.StringVar()

    save_button_text = tk.StringVar()
    continue_button_text = tk.StringVar()
    file_menu_text = tk.StringVar()
    readfile_menu_text = tk.StringVar()
    savefile_menu_text = tk.StringVar()
    exit_menu_text = tk.StringVar()
    option_menu_text = tk.StringVar()
    autorun_menu_text = tk.StringVar()
    auto_quit_menu_text = tk.StringVar()
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
    menu_hide_text = tk.StringVar()
    taskbar_hide_text = tk.StringVar()
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
    cf_entry_old_path = ttk.Entry(root, textvariable=source_path, state='')
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
    cf_is_lnk_move = tk.BooleanVar()
    cf_option_lnk_move = ttk.Checkbutton(root, textvariable=cf_option_move_lnk_text,
                                         variable=cf_is_lnk_move)
    cf_is_folder_move = tk.BooleanVar()
    cf_option_folder_move = ttk.Checkbutton(root, textvariable=cf_option_folder_move_text,
                                            variable=cf_is_folder_move)

    cf_label_adv = ttk.Label(root, textvariable=cf_label_adv_text)
    cf_unfold_adv = tk.BooleanVar()
    cf_option_adv = ttk.Checkbutton(root, textvariable=cf_option_adv_text,
                                    variable=cf_unfold_adv,
                                    command=lambda: Place.cf_fold_adv(cf_unfold_adv.get()))

    cf_entry_frame_keep_files = tk.Frame(root)
    cf_label_keep_files = ttk.Label(
        root, textvariable=cf_label_keep_files_text)
    cf_entry_keep_files = Combopicker(
        master=cf_entry_frame_keep_files, frameheight=220, allname_textvariable=select_all_text)
    cf_entry_keep_files.bind(
        '<Button-1>', lambda event: cf_refresh_whitelist_entry())

    cf_entry_frame_keep_formats = tk.Frame(root)
    cf_label_keep_formats = ttk.Label(
        root, textvariable=cf_label_keep_formats_text)
    cf_entry_keep_formats = Combopicker(
        master=cf_entry_frame_keep_formats, frameheight=190, allname_textvariable=select_all_text)
    cf_entry_keep_formats.bind(
        '<Button-1>', lambda event: cf_refresh_whitelist_entry())

    cf_label_expire_options = ttk.Label(
        root, textvariable=cf_label_expire_options_text)
    cf_entry_mode = tk.IntVar()
    cf_option_mode_1 = ttk.Radiobutton(root, textvariable=cf_option_mode_1_text, variable=cf_entry_mode,
                                       value=1)
    cf_option_mode_2 = ttk.Radiobutton(root, textvariable=cf_option_mode_2_text, variable=cf_entry_mode,
                                       value=2)
    cf_label_time = ttk.Label(root, textvariable=cf_label_time_text)
    cf_entry_time = ttk.Entry(root)

    label_preview = ttk.Label(root, textvariable=label_preview_text)
    preview_text = tk.Text(root, height=5, width=50,
                           state='disabled', wrap='none', )

    preview_yscrollbar = tk.Scrollbar()
    preview_text.config(yscrollcommand=preview_yscrollbar.set)
    preview_yscrollbar.config(command=preview_text.yview)

    preview_xscrollbar = tk.Scrollbar(orient='horizontal')
    preview_text.config(xscrollcommand=preview_xscrollbar.set)
    preview_xscrollbar.config(command=preview_text.xview)

    preview_button = ttk.Button(
        root, textvariable=preview_button_text, command=lambda: Thread(target=lambda: execute_as_root(exe_preview=True)).start())

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
        master=sf_entry_frame_lock_folder, frameheight=190, allname_textvariable=select_all_text)
    sf_browse_lockfolder_button = ttk.Button(root, textvariable=sf_browse_lockfolder_button_text,
                                             command=lambda: choose_lock_items('lockfolder'))

    sf_label_lock_file = ttk.Label(root, textvariable=sf_label_lock_file_text)
    sf_entry_frame_lock_file = tk.Frame(root)
    sf_entry_lock_file = Combopicker(
        master=sf_entry_frame_lock_file, frameheight=150, allname_textvariable=select_all_text)
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
            self.show_help(LT_Dic.help_main_text[lang_num])

        def help_before_use(self):
            self.show_help(LT_Dic.help_before_use_text[lang_num])

        def cf_help(self):
            self.show_help(LT_Dic.cf_help_text[lang_num])

        def cf_help_keep(self):
            self.show_help(LT_Dic.cf_help_keep_text[lang_num])

        def cf_help_timeset(self):
            self.show_help(LT_Dic.cf_help_timeset_text[lang_num])

        def sf_help(self):
            self.show_help(LT_Dic.sf_help_text[lang_num])

        def sf_removable_help(self):
            self.show_help(LT_Dic.sf_removable_help_text[lang_num])

        def sf_lock_help(self):
            self.show_help(LT_Dic.sf_lock_help_text[lang_num])

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
                                              message=LT_Dic.r_label_text_dic["path_not_exist_notice"][lang_num] + noexist_path + LT_Dic.r_label_text_dic["create_path_notice"][lang_num]):
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
                    'Movefile', LT_Dic.r_label_text_dic['num_warning'][lang_num])
                return True
            elif self.cf_has_blank():
                tkinter.messagebox.showwarning(
                    title='Movefile', message=LT_Dic.r_label_text_dic['blank_warning'][lang_num])
                return True
            elif cf_path_error_info == 'same_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=LT_Dic.r_label_text_dic['same_path_warning'][lang_num])
                return True
            elif cf_path_error_info is None:
                return True
            elif cf_path_error_info:
                tkinter.messagebox.showwarning(
                    title='Movefile', message=LT_Dic.r_label_text_dic['path_warning'][lang_num])
                return True
            else:
                return False

        def get_sf_error_state(self):
            sf_path_error_info = self.sf_path_error()
            if self.sf_has_blank():
                tkinter.messagebox.showwarning(
                    title='Movefile', message=LT_Dic.r_label_text_dic['blank_warning'][lang_num])
                return True
            elif sf_path_error_info == 'same_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=LT_Dic.r_label_text_dic['same_path_warning'][lang_num])
                return True
            elif sf_path_error_info == 'in_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=LT_Dic.r_label_text_dic['in_path_warning'][lang_num])
                return True
            elif sf_path_error_info == 'in_disk_path_error':
                tkinter.messagebox.showwarning(title='Movefile',
                                               message=LT_Dic.r_label_text_dic['in_disk_path_warning'][lang_num])
                return True
            elif sf_path_error_info is None:
                return True
            elif sf_path_error_info:
                tkinter.messagebox.showwarning(
                    title='Movefile', message=LT_Dic.r_label_text_dic['path_warning'][lang_num])
                return True
            else:
                return False

    def initial_entry(set_cf_dest=False):
        default_dest_path = os.path.join(DESKTOP_PATH, r'Previous Files')
        if not cf_entry_old_path.get():
            cf_entry_old_path.insert(0, DESKTOP_PATH)
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
                    mf_log(f'remove_last_edit error: {save_name}')

        def savefile(function, save_name='New_Setting'):  # 保存文件
            cf_data.read(CF_CONFIG_PATH)
            sf_data.read(SF_CONFIG_PATH)

            if function == 'cf':  # 如果当前界面为cf
                remove_last_edit(cf_data, CF_CONFIG_PATH)
                if not os.path.exists(CF_CONFIG_PATH):
                    file = open(CF_CONFIG_PATH,
                                'w', encoding='ANSI')
                    file.close()
                cf_data.read(CF_CONFIG_PATH)
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
                cf_data.set(save_name, "move_lnk", str(cf_is_lnk_move.get()))
                cf_data.write(
                    open(CF_CONFIG_PATH, "w+", encoding='ANSI'))

            elif function == 'sf':  # 如果当前界面为sf
                remove_last_edit(sf_data, SF_CONFIG_PATH)
                if not os.path.exists(SF_CONFIG_PATH):
                    file = open(SF_CONFIG_PATH,
                                'w', encoding='ANSI')
                    file.close()
                sf_data.read(SF_CONFIG_PATH)
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
                    open(SF_CONFIG_PATH, 'w+', encoding='ANSI'))

            tkinter.messagebox.showinfo(title=LT_Dic.r_label_text_dic['succ_save'][lang_num][0],
                                        message=LT_Dic.r_label_text_dic['succ_save'][lang_num][1])
            continue_button.config(state=tk.NORMAL)

        def sure_save():
            ask_name_window.withdraw()
            savefile(function=cf_or_sf.get(), save_name=name_entry.get())
            log_function = 'Syncfile'
            if cf_or_sf.get() == 'cf':
                log_function = 'Cleanfile'
            mf_log(
                f"\nA config file of {log_function} named {name_entry.get()} is saved")
            current_save_name.set(
                LT_Dic.r_label_text_dic['current_save_name'][lang_num] + name_entry.get())
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
            ask_name_window.iconbitmap(MF_ICON_PATH)
            ask_name_window.geometry('400x35')
            ask_name_window.title(
                LT_Dic.r_label_text_dic['ask_name_window'][lang_num])
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
                ask_name_window, text=LT_Dic.r_label_text_dic['name_label'][lang_num])
            name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')

            name_entry = ttk.Combobox(
                ask_name_window, values=current_mode_savings)
            name_entry.insert(0, autofill_name)
            name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='W')
            sure_name_button = ttk.Button(ask_name_window, text=LT_Dic.r_label_text_dic['sure_name_button'][lang_num],
                                          command=lambda: sure_save())
            sure_name_button.grid(row=0, column=2, sticky='W')
            ask_name_window.bind('<Return>', lambda event: sure_save())
            ask_name_window.protocol('WM_DELETE_WINDOW', exit_asn)

    def read_saving(ask_path=False):
        global ask_saving_root
        cf_file = configparser.ConfigParser()
        cf_file.read(CF_CONFIG_PATH)  # 获取配置文件
        sf_file = configparser.ConfigParser()
        sf_file.read(SF_CONFIG_PATH)
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
            cf_is_folder_move.set(cf_file.getboolean(
                setting_name, 'move_folder'))
            cf_is_lnk_move.set(cf_file.getboolean(setting_name, 'move_lnk'))
            Place('cf')
            cf_or_sf.set('cf')
            current_cf_save_name.set(setting_name)
            current_save_name.set(
                LT_Dic.r_label_text_dic['current_save_name'][lang_num] + setting_name)
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
                LT_Dic.r_label_text_dic['current_save_name'][lang_num] + setting_name)
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
                ini_file.read(CF_CONFIG_PATH)
                ini_file.remove_section(del_name)
                ini_file.write(
                    open(CF_CONFIG_PATH, 'w+', encoding='ANSI'))
                mf_log(
                    f"\nA config file of Cleanfile named {del_name} is deleted")
            elif del_mode in ['同步文件(Syncfile)', 'Syncfile'] and is_continue:
                ini_file.read(SF_CONFIG_PATH)
                ini_file.remove_section(del_name)
                ini_file.write(
                    open(SF_CONFIG_PATH, 'w+', encoding='ANSI'))
                mf_log(
                    f"\nA config file of Syncfile named {del_name} is deleted")
            exit_asr()

        def sure_open():
            saving_name = read_name_entry.get()
            if read_mode_entry.get() in ['清理文件(Cleanfile)', 'Cleanfile']:
                open_cf_saving(saving_name)
            elif read_mode_entry.get() in ['同步文件(Syncfile)', 'Syncfile']:
                open_sf_saving(saving_name)
            current_save_name.set(
                LT_Dic.r_label_text_dic['current_save_name'][lang_num] + saving_name)
            exit_asr()

        def exit_asr():
            ask_saving_root.destroy()

        if ask_path:
            ask_saving_root = tk.Toplevel(root)
            ask_saving_root.iconbitmap(MF_ICON_PATH)
            if lang_num == 0:
                ask_saving_root.geometry('680x35')
            elif lang_num == 1:
                ask_saving_root.geometry('700x35')
            ask_saving_root.title(
                LT_Dic.r_label_text_dic['readfile_menu'][lang_num])
            ask_saving_root.focus_force()
            last_edit_mode = ''
            last_edit_name = ''
            save_names = []
            last_saving_data = list_saving_data()[0]
            if last_saving_data:
                last_edit_mode = last_saving_data[0]
                last_edit_name = last_saving_data[1]
            read_name_label = ttk.Label(
                ask_saving_root, text=LT_Dic.r_label_text_dic['read_name_label'][lang_num])
            read_name_label.grid(row=0, column=0, pady=5, padx=5, sticky='E')
            read_mode_entry = ttk.Combobox(ask_saving_root, values=LT_Dic.r_label_text_dic['read_mode_entry'][lang_num],
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
            del_save_button = ttk.Button(ask_saving_root, text=LT_Dic.r_label_text_dic['del_save_button'][lang_num],
                                         command=lambda: del_saving())
            del_save_button.grid(row=0, column=3, padx=5, pady=5)
            sure_name_bottom = ttk.Button(ask_saving_root, text=LT_Dic.r_label_text_dic['sure_name_bottom'][lang_num],
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

    def cf_operate_from_root(preview=False):
        old_path = cf_entry_old_path.get()  # 旧文件夹
        new_path = cf_entry_new_path.get()  # 新文件夹
        pass_file = cf_entry_keep_files.get().split(',')  # 设置跳过白名单
        pass_format = cf_entry_keep_formats.get().split(',')  # 设置跳过格式
        time_ = int(cf_entry_time.get()) * 3600  # 设置过期时间(hour)
        mode = int(cf_entry_mode.get())  # 设置判断模式
        is_move_folder = cf_is_folder_move.get()  # 设置是否移动文件夹
        is_move_lnk = cf_is_lnk_move.get()
        cf_tasks = cf_move_dir(root, old__path=old_path, new__path=new_path, pass__file=pass_file, pass__format=pass_format,
                               overdue__time=time_,
                               check__mode=mode, is__move__folder=is_move_folder, is__move__lnk=is_move_lnk, preview=preview)
        return cf_tasks

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
        sf_sync_dir(root, path1, path2, single_sync, lang_num,
                    area_name, lockfile, lockfolder)

    def startup_autorun():
        time.sleep(1)
        cf_autorun_operation(root)
        sf_autorun_operation(root, 'local')
        if quit_after_autorun:
            exit_program()

    def change_language(language):
        nonlocal lang_num
        general_data.set('General', 'language', language)
        general_data.write(
            open(MF_CONFIG_PATH, "w+", encoding='ANSI'))
        lang_num = language_num(language)
        set_language(lang_num)
        Place(cf_or_sf.get(), sf_place_mode.get())
        tkinter.messagebox.showinfo(
            title='Movefile', message=LT_Dic.r_label_text_dic['change_language'][lang_num])

    def execute_as_root(exe_preview=False):
        if cf_or_sf.get() == 'cf' and not root_info_checker.get_cf_error_state():
            if not exe_preview:
                root.withdraw()
            _result = cf_operate_from_root(preview=exe_preview)  # run cf
            if exe_preview:
                set_preview(result=_result, mode='cf')

        elif cf_or_sf.get() == 'sf' and not root_info_checker.get_sf_error_state():
            sf_operator = Thread(
                target=lambda: sf_operate_from_root(), daemon=True)
            sf_operator.start()
            root.withdraw()

    # @atexit.register
    def exit_program():
        gvar.set('program_finished', True)
        root.withdraw()
        mf_toaster.stop_notification_thread()
        if 'ask_saving_root' in globals().keys():
            ask_saving_root.quit()
            ask_saving_root.destroy()
        if 'ask_name_window' in globals().keys():
            ask_name_window.quit()
            ask_name_window.destroy()

        task_menu.stop()
        root.quit()
        root.destroy()

        mf_log("\nMovefile Quit\n")
        butt_icon.join()
        background_detect.join()

    # 创建按键
    blank_pix = ttk.Label(root, text=' ')  # This is a Placeholder
    save_button = ttk.Button(
        root, textvariable=save_button_text, command=lambda: ask_save_name())
    continue_button = ttk.Button(
        root, textvariable=continue_button_text, command=lambda: Thread(target=lambda: execute_as_root()).start())

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
    is_startup_run.set(general_data.getboolean('General', 'autorun'))
    auto_quit = tk.BooleanVar()
    auto_quit.set(quit_after_autorun)
    is_desktop_shortcut = tk.BooleanVar()
    is_desktop_shortcut.set(general_data.getboolean(
        'General', 'desktop_shortcut'))
    option_menu.add_checkbutton(label=autorun_menu_text.get(), variable=is_startup_run,
                                command=lambda: set_startup(is_startup_run.get(), lang_num))
    option_menu.add_checkbutton(label=auto_quit_menu_text.get(), variable=auto_quit,
                                command=lambda: set_auto_quit(auto_quit.get()))
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
    
    main_menu.add_command(label=' ' * LT_Dic.r_label_text_dic['blank'][lang_num], state='disabled')
    main_menu.add_command(label=menu_hide_text.get(),
                          command=lambda: root.withdraw())

    root.config(menu=main_menu)

    # 托盘菜单
    menu = (
        MenuItem(taskbar_setting_text.get(),
                 lambda event: root.deiconify(), default=True), Menu.SEPARATOR,
        MenuItem(taskbar_hide_text.get(),
                 action=lambda event: root.wait_window()),
        MenuItem(taskbar_exit_text.get(), action=lambda: exit_program()))
    image = Image.open(MF_ICON_PATH)
    task_menu = Icon("icon", image, "Movefile", menu)

    root.bind("<Control-o>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-O>", lambda event: read_saving(ask_path=True))
    root.bind("<Control-s>", lambda event: ask_save_name())
    root.bind("<Control-S>", lambda event: ask_save_name())
    # root.bind('<Button-1>'), lambda: sf_refresh_disk_list(none_disk=True)

    root_info_checker = MF_Info_Checker()

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
        target=lambda: detect_removable_disks_thread(root, lang_num), daemon=True)
    background_detect.start()

    if visits_today == 1 and startup_visit:
        autorun_options = Thread(
            target=lambda: startup_autorun(), daemon=True)
        autorun_options.start()

    root.mainloop()
