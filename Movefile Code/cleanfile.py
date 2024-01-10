

import configparser
import os
import time
from shutil import move as shutil_move
from threading import Thread

import LT_Dic
from mf_const import CF_CONFIG_PATH, MF_CONFIG_PATH, MF_ICON_PATH
from mf_mods import language_num, mf_log, mf_toaster, scan_items


def cf_move_dir(master_root, old__path, new__path, pass__file, pass__format, overdue_time, check__mode, is__move__folder):
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
    from mf_ui import ProgressBar
    mf_file = configparser.ConfigParser()
    mf_file.read(MF_CONFIG_PATH)
    lang_num = language_num(mf_file.get('General', 'language'))

    def cf_show_notice(old_path, new_path, move_name, error_name):
        new_folder = new_path.split('\\')[-1]
        old_folder = old_path.split('\\')[-1]
        mf_icon_path = os.path.join(MF_ICON_PATH)
        if len(move_name) > 0:
            notice_title = LT_Dic.cfdic['title_p1'][lang_num] + old_folder + \
                LT_Dic.cfdic['title_p2_1'][lang_num] + new_folder + ':'
            if new_path == '':
                notice_title = LT_Dic.cfdic['title_p1'][lang_num] + \
                    old_folder + LT_Dic.cfdic['title_p2_2'][lang_num]
            mf_log("\n" + notice_title + "\n" + move_name[:-3])
            mf_toaster.show_toast(notice_title, move_name[:-3],
                                  icon_path=mf_icon_path,
                                  duration=10,
                                  threaded=False)
        else:
            notice_title = old_folder + LT_Dic.cfdic['cltitle'][lang_num]
            notice_content = LT_Dic.cfdic['clcontent'][lang_num]
            mf_log("\n" + notice_title + "\n" + notice_content)
            mf_toaster.show_toast(notice_title, notice_content,
                                  icon_path=mf_icon_path,
                                  duration=10,
                                  threaded=False)
        if len(error_name) > 0:
            notice_title = LT_Dic.cfdic['errtitle'][lang_num]
            notice_content = error_name[:-3] + \
                '\n' + LT_Dic.cfdic['errcontent'][lang_num]
            mf_log("\n" + notice_title + "\n" + notice_content)
            mf_toaster.show_toast(notice_title, notice_content,
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
            baroot.set_label1(LT_Dic.cfdic['main_progress_label']
                              [lang_num] + item_data.name)
            baroot.progress_root.update_idletasks()
        item_datas.close()
        return tasks

    def run_cleanfile(baroot):
        nonlocal cleanfile_done
        cf_move_name = ''
        cf_error_name = ''
        baroot.main_progress_bar['value'] = 0
        baroot.progress_root.update_idletasks()
        tasks = get_cf_tasks(baroot)
        task_len = str(len(tasks))
        baroot.main_progress_bar['maximum'] = len(tasks)
        baroot.set_label1(
            f'{LT_Dic.cfdic["main_progress_label1"][lang_num][0]}{str(baroot.main_progress_bar["value"])}/{task_len}  {LT_Dic.cfdic["main_progress_label1"][lang_num][1]}')
        for task in tasks:
            item = task[0]
            item_path = task[1]
            for_path = task[2]
            baroot.set_label2(LT_Dic.cfdic["current_file_label1"]
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
                f'{LT_Dic.cfdic["main_progress_label1"][lang_num][0]}{str(baroot.main_progress_bar["value"])}/{task_len}  {LT_Dic.cfdic["main_progress_label1"][lang_num][1]}')
            baroot.progress_root.update_idletasks()
        baroot.progress_root.withdraw()
        cf_show_notice(old__path, new__path, cf_move_name, cf_error_name)
        baroot.progress_root.withdraw()
        cleanfile_done = True

    if new__path != '' and not os.path.exists(new__path):
        os.mkdir(new__path)

    cleanfile_done = False
    clean_bar_root = ProgressBar('Movefile  -Syncfile Progress',
                                 LT_Dic.cfdic["main_progress_label2"][lang_num],
                                 LT_Dic.cfdic["current_file_label"][lang_num],
                                 lang_num)
    clean_bar_root_task = Thread(
        target=lambda: clean_bar_root.launch(root_master=master_root), daemon=True)
    clean_bar_root_task.start()
    while not clean_bar_root.initialization_done:
        time.sleep(0.01)
    run_tasks = Thread(
        target=lambda: run_cleanfile(clean_bar_root), daemon=True)
    run_tasks.start()
    while not cleanfile_done:
        time.sleep(1)
    clean_bar_root.progress_root_destruction()
    clean_bar_root_task.join()
    run_tasks.join()


def cf_autorun_operation(master):
    """
    The function cf_autorun_operation is used to perform an cleanfile operation automatically.
    """
    cf_file = configparser.ConfigParser()
    cf_file.read(CF_CONFIG_PATH)

    autorun_savings = []
    for cf_name in cf_file.sections():
        if cf_file.get(cf_name, 'autorun') == 'True':
            autorun_savings.append(cf_name)

    for save_name in autorun_savings:
        cf_move_dir(master_root=master,
                    old__path=cf_file.get(save_name, 'old_path'),
                    new__path=cf_file.get(save_name, 'new_path'),
                    pass__file=cf_file.get(
                        save_name, 'pass_filename').split(','),
                    pass__format=cf_file.get(
                        save_name, 'pass_format').split(','),
                    overdue_time=cf_file.getint(save_name, 'set_hour') * 3600,
                    check__mode=cf_file.getint(save_name, 'mode'),
                    is__move__folder=cf_file.get(save_name, 'move_folder'))
        mf_log(
            f'\nAutomatically ran Cleanfile operation as config "{save_name}"')
