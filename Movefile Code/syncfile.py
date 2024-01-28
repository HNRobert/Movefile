

import configparser
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from filecmp import dircmp
from pathlib import Path
from shutil import Error as shutil_Error
from shutil import copy2 as shutil_copy2
from shutil import copytree as shutil_copytree
from threading import Thread

import LT_Dic
from mf_const import MF_CONFIG_PATH, MF_ICON_PATH, SF_CONFIG_PATH
from mf_mods import (get_removable_disks, language_num, mf_log, mf_toaster,
                     remove_last_edit)
from win32api import GetVolumeInformation

from Movefile import gvar


def sf_sync_dir(master_root, language_number, preview=False, hidden=False, **sf_saving_details):
    """
    The `sf_sync_dir` function synchronizes files between two directories, displaying progress using a progress bar.

    :param master_root: The master_root parameter is a string that represents the root window variable of the Movefile application. It is the mother root to create and display the progress bar.
    :param path1: The path to the first folder that you want to synchronize
    :param path2: The `path2` parameter represents the destination directory where the files will be synchronized to
    :param single_sync: A boolean value indicating whether to perform a single sync or not. If True, only files present in the first folder will be synced to the second folder. If False, files present in both folders will be synced
    :param language_number: The `language_number` parameter is an integer that represents the language code to be used for displaying messages and notifications. It is used to select the appropriate language from a dictionary of language translations
    :param area_name: The `area_name` parameter is an optional parameter that represents the label of the partitions being synchronized. It is used in the notification message to indicate which area of files has been synchronized. If not provided, the default name will be the last part of the `path1`
    :param lock_file: The `lock_file` parameter is a string that represents a comma-separated list of file paths that should be excluded from the synchronization process. These files will not be moved or replaced during the synchronization
    :param lock_folder: The `lock_folder` parameter is a string that represents the paths of folders that should be excluded from the synchronization process. These folders will not be compared or synchronized with the other folders. Multiple folder paths can be separated by commas
    """

    from mfprogressbar import MFProgressBar

    def diff_items_in(folderA, folderB, _bar_root):
        """
        The function takes two folder paths as input and returns the files that are present in one
        folder but not in the other.

        :param folderA_path: The path to the first folder that you want to compare
        :param folderB_path: The path to the second folder that you want to compare
        """

        def add_only_data(index, data_list, src_base: str, tar_base: str):
            if any(tar_base.startswith(p_folder) for p_folder in lock_folders):
                return
            for item in data_list:
                idx = 0
                src_path, tar_path = os.path.join(
                    src_base, item), os.path.join(tar_base, item)
                item_is_folder = os.path.isdir(src_path)
                if item_is_folder and any(tar_path.startswith(p_folder) for p_folder in lock_folders):
                    continue
                elif item_is_folder:
                    idx = 2
                elif tar_path in lock_files:  # file in lockfile
                    continue
                diff_data[index+idx].append([src_path, tar_path])
                _bar_root.set_label1(
                    LT_Dic.sfdic['main_progress_label'][language_number] + item)

        # [diff_files, left_only_files, right_only_files, left_only_folders, right_only_folders]
        diff_data = [[], [], [], [], []]
        if folderA.endswith(':'):
            folderA += '\\'
        if folderB.endswith(':'):
            folderB += '\\'
        if not os.path.isdir(folderA) or not os.path.isdir(folderB):
            return diff_data
        cmp_data = dircmp(folderA, folderB, ignore=[])
        for dfile in cmp_data.diff_files:
            diff_data[0].append(
                [os.path.join(folderA, dfile), os.path.join(folderB, dfile)])
        add_only_data(1, cmp_data.left_only, folderA, folderB)
        add_only_data(2, cmp_data.right_only, folderB, folderA)

        for com_dir in cmp_data.common_dirs:
            dir_data = diff_items_in(os.path.join(
                folderA, com_dir), os.path.join(folderB, com_dir), _bar_root)
            for i in range(5):
                diff_data[i].extend(dir_data[i])
        return diff_data

    def get_sf_tasks(_bar_root: MFProgressBar):
        """
        The function "get_task" compares the two folder and decides which file need to be moved or replaced.

        :param _bar_root: The parameter `_bar_root` is likely a variable or object that represents the
        root node or starting point of a tree or hierarchy structure. It could be used to navigate or
        perform operations on the tree or hierarchy
        """
        def judged_task(*items):
            """
            The function `judged_task` compares the modification times of two items and returns the
            items in a list if certain conditions are met.

            :param only_one: The `only_one` parameter is a boolean flag that determines if there is only one
            of the item in items exists. If True, the compare between their mtime would be skipped
            :type only_one: bool (optional)
            :return: a list containing the values of itemA and itemB.
            """

            itemA, itemB = items
            if int(os.stat(itemA).st_mtime) < int(os.stat(itemB).st_mtime):
                if single_sync:
                    return None
                itemA, itemB = itemB, itemA
            if any(itemB.startswith(p_folder) for p_folder in lock_folders) or itemB in lock_files:
                return None
            _bar_root.set_label1(
                LT_Dic.sfdic['main_progress_label'][language_number] + itemA.split('\\')[-1])
            return [itemA, itemB]

        # task items' format: [source_file_path, dest_file_path]
        sync_tasks = [[], []]
        diff_item_data = diff_items_in(path1, path2, _bar_root)
        for a_only_folder in diff_item_data[3]:
            sync_tasks[0].append(a_only_folder)
        for a_only_file in diff_item_data[1]:
            sync_tasks[1].append(a_only_file)
        if not single_sync:
            for b_only_folder in diff_item_data[4]:
                sync_tasks[0].append(b_only_folder)
            for b_only_file in diff_item_data[2]:
                sync_tasks[1].append(b_only_file)

        for diff_file in diff_item_data[0]:
            sync_tasks[1].append(judged_task(*diff_file))
        for i in range(2):
            sync_tasks[i] = list(filter(None, sync_tasks[i]))
        return sync_tasks

    def synchronize_files(baroot: MFProgressBar, is_folder=False, *task):
        """
        The function `synchronize_files` takes two parameters, `baroot` and `task`, and does some kind of file synchronization operation.

        :param baroot: The `baroot` parameter is a string that represents the root directory of the source files. It is the directory from which the files will be synchronized
        :param task: The `task` parameter is a string that represents the specific task or operation that needs to be performed on the files
        """
        if baroot.stop_running_flag:
            return
        baroot.set_label2(
            LT_Dic.sfdic["current_file_label1"][language_number] + task[0].split('\\')[-1])
        source_file_path, dest_file_path = task
        dest_path = Path(dest_file_path)
        # Create parent directories if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if is_folder:
                shutil_copytree(source_file_path, dest_file_path)
            else:
                shutil_copy2(source_file_path, dest_file_path)
        except shutil_Error:
            return source_file_path
        return None

    def run_sync_tasks(baroot: MFProgressBar, tasks):
        """
        The function "run_sync_tasks" performs synchronous tasks.

        :param baroot: The progress bar root object
        """

        def execute_sf_tasks(_baroot: MFProgressBar, _tasks, _is_folder):
            nonlocal sf_error_name
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(
                    synchronize_files, _baroot, _is_folder, *_task) for _task in _tasks]

                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        sf_error_name += result + ' , '

                    _baroot.set_label1(
                        f'{LT_Dic.sfdic["main_progress_label1"][language_number][0]}{str(_baroot.get_value())}/{str(task_len)}  {LT_Dic.sfdic["main_progress_label1"][language_number][1]}', add_value=True)

        sf_error_name = ''
        folder_tasks, file_tasks = tasks[0], tasks[1]
        task_len = len(folder_tasks) + len(file_tasks)
        baroot.set_maximum(task_len)
        baroot.set_label1(
            f'{LT_Dic.sfdic["main_progress_label1"][language_number][0]}0/{str(task_len)}  {LT_Dic.sfdic["main_progress_label1"][language_number][1]}')

        execute_sf_tasks(baroot, folder_tasks, True)
        execute_sf_tasks(baroot, file_tasks, False)

        baroot.withdraw_root()
        if not hidden:
            path_name_1 = path1.split('\\')[-1]
            if sf_saving_details['place_mode'] == 'movable':
                path_name_1 = GetVolumeInformation(path1)[0]
            sf_show_notice(path_name_1, path2.split(
                '\\')[-1], sf_error_name, language_number=language_number)
        if folder_tasks or file_tasks:
            _result = ''
            for _item in folder_tasks + file_tasks:
                _result += _item[0] + ' -> ' + _item[1] + '\n'
            mf_log('\nSynced items:\n' + _result)

        baroot.destroy_root()

    path1 = sf_saving_details['path_1']
    path2 = sf_saving_details['path_2']
    single_sync = sf_saving_details['single_sync']
    lock_folders: list = sf_saving_details['lock_folder']
    lock_folders += [path1+'\\System Volume Information',
                     path2+'\\System Volume Information']
    lock_files = sf_saving_details['lock_file']
    lock_folders = list(filter(None, lock_folders))
    lock_files = list(filter(None, lock_files))

    if path1[-1] != ':' and not os.path.exists(path1):
        os.makedirs(path1)
    if not os.path.exists(path2):
        os.makedirs(path2)

    sync_bar_root = MFProgressBar('Movefile  -Syncfile Progress',
                                  LT_Dic.sfdic["main_progress_label2"][language_number],
                                  LT_Dic.sfdic["current_file_label"][language_number],
                                  language_number, hidden=hidden)
    if not hidden:
        sync_bar_root_task = Thread(
            target=lambda: sync_bar_root.launch(root_master=master_root), daemon=True)
        sync_bar_root_task.start()
        while not sync_bar_root.initialization_done:
            time.sleep(0.01)
    sf_tasks = get_sf_tasks(sync_bar_root)
    if not preview:
        run_tasks = Thread(
            target=lambda: run_sync_tasks(sync_bar_root, sf_tasks), daemon=True)
        run_tasks.start()
        while not sync_bar_root.stop_running_flag:
            time.sleep(0.02)
    sync_bar_root.progress_root_destruction()
    return sf_tasks  # [folder_task, file_task]


def sf_show_config_error(config_name, language_number):
    sf_notice_title = LT_Dic.sfdic["err_title_p1"][language_number]
    sf_notice_content = LT_Dic.sfdic["err_title_p2_1"][language_number] + config_name + \
        LT_Dic.sfdic["err_title_p2_2"][language_number]
    mf_toaster.show_toast(sf_notice_title,
                          sf_notice_content,
                          icon_path=MF_ICON_PATH,
                          duration=10,
                          threaded=False)
    mf_log("\n" + sf_notice_title + "\n" + sf_notice_content)


def sf_show_notice(path_1, path_2, sf_error_name, language_number, direct_movable=False):
    if not direct_movable:
        sf_notice_title = LT_Dic.sfdic["title_p1"][language_number]
        sf_notice_content = LT_Dic.sfdic["title_p2_1"][language_number] + path_1 + \
            LT_Dic.sfdic["title_p2_2"][language_number] + path_2 + \
            LT_Dic.sfdic["title_p2_3"][language_number]
        mf_log("\n" + sf_notice_title + "\n" + sf_notice_content)
    else:
        sf_notice_title = ''
        sf_notice_content = ''
    mf_toaster.show_toast(sf_notice_title,
                          sf_notice_content,
                          icon_path=MF_ICON_PATH,
                          duration=10,
                          threaded=False)

    if len(sf_error_name):
        sf_error_title = LT_Dic.sfdic["errtitle"][language_number]
        sf_error_content = sf_error_name + \
            LT_Dic.sfdic['can_not_move_notice'][language_number]
        mf_log("\n" + sf_error_title + "\n" + sf_error_content)
        mf_toaster.show_toast(sf_error_title,
                              sf_error_content,
                              icon_path=MF_ICON_PATH,
                              duration=10,
                              threaded=False)


def sf_autorun_operation(master, place, mv_saving_name: str = ''):
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
    sf_file.read(SF_CONFIG_PATH, encoding='utf-8')
    mf_file = configparser.ConfigParser()
    mf_file.read(MF_CONFIG_PATH, encoding='utf-8')

    def autorun_movable_sf(save: str):
        lang_num = language_num(mf_file.get('General', 'language'))
        sf_options = sf_read_config(save)
        if not sf_options:
            sf_show_config_error(save, lang_num)  # show notice
            return
        hidden = sf_options['direct_sync']
        sf_sync_dir(master, lang_num, False, hidden, **sf_options)

    def autorun_local_sf(data_names):
        lang_num = language_num(mf_file.get('General', 'language'))
        for saving_data in data_names:
            sf_options = sf_read_config(saving_data)
            if not sf_options:
                sf_show_config_error(saving_data, lang_num)  # show notice
                continue
            sf_sync_dir(master, lang_num, False, False, **sf_options)
            mf_log(
                f'\nAutomatically ran Syncfile operation as config "{saving_data}"')

    if place == 'movable':
        autorun_movable_sf(mv_saving_name)
    elif place == 'local':
        autorun_local_sf(get_sf_startup_savings())


"""
def all_files_in(item_dir: str, folderA_path, folderB_path):
    all_files = []
    for itroot, itdirs, itfiles in os.walk(item_dir):
        for itfile in itfiles:
            itfile_path = os.path.join(itroot, itfile)
            if folderA_path[-1] == '\\':
                folderA_path = folderA_path[:-1]
            opp_file_path = itfile_path.replace(folderA_path, folderB_path)
            all_files.append([itfile_path, opp_file_path])

    return all_files
"""


def get_sf_savings_with(*wants, **conditions):
    sf_dat = configparser.ConfigParser()
    sf_dat.read(SF_CONFIG_PATH, encoding='utf-8')
    target_savings = []  # [volume id, saving_name, direct_sync]
    for saving in sf_dat.sections():
        if not _fixed_sf_config(sf_dat, saving):
            continue
        for key, value in conditions.items():
            if sf_dat.get(saving, key) != value:
                break
        else:
            target_savings.append([saving] +
                                  [sf_dat.get(saving, want_item) for want_item in wants])
    return target_savings


def get_sf_startup_savings():
    conditions = {'place_mode': 'local', 'autorun': 'True'}
    return get_sf_savings_with(**conditions)


def get_movable_autorun_infos():
    wants = ['disk_number', 'direct_sync']
    conditions = {'place_mode': 'movable',
                  'autorun': 'True', 'real_time': 'False'}
    return get_sf_savings_with(*wants, **conditions)


def get_real_time_infos():
    wants = ['place_mode']
    conditions = {'real_time': 'True'}
    return get_sf_savings_with(*wants, **conditions)


def get_removable_real_time_infos():
    wants = ['disk_number']
    conditions = {'real_time': 'True', 'place_mode': 'movable'}
    return get_sf_savings_with(*wants, **conditions)


def _fixed_sf_config(sf_config_file: configparser.ConfigParser, saving_name: str):
    if not saving_name:
        return False
    if not sf_config_file.has_section(saving_name):
        return False
    if not sf_config_file.has_option(saving_name, 'place_mode'):
        return False
    if not sf_config_file.has_option(saving_name, 'path_1') and sf_config_file.get(saving_name, 'place_mode') == 'local':
        return False
    if not sf_config_file.has_option(saving_name, 'disk_number') and sf_config_file.get(saving_name, 'place_mode') == 'movable':
        return False
    if not sf_config_file.has_option(saving_name, 'path_2'):
        return False
    option_names = ['path_1', 'lock_folder', 'lock_file',
                    'mode', 'autorun', 'real_time', 'direct_sync']
    default_values = ['', '', '', 'single', 'False', 'False', 'False']
    flag = False
    for option, value in zip(option_names, default_values):
        if not sf_config_file.has_option(saving_name, option):
            sf_config_file.set(saving_name, option, value)
            flag = True
    if flag:
        sf_config_file.write(open(SF_CONFIG_PATH, 'w+', encoding='utf-8'))
    return True


def sf_read_config(saving_name):
    sf_file = configparser.ConfigParser()
    sf_file.read(SF_CONFIG_PATH, encoding='utf-8')
    if not _fixed_sf_config(sf_file, saving_name):
        return False
    sf_options = {}
    sf_options['place_mode'] = sf_file.get(saving_name, 'place_mode')
    if sf_options['place_mode'] == 'local':
        sf_options['path_1'] = sf_file.get(saving_name, 'path_1')
    else:
        sf_disk_data = get_removable_disks(
            sf_file.get(saving_name, 'disk_number'))
        if not sf_disk_data:
            return {}
        sf_options['path_1'] = sf_disk_data[1]
        sf_options['disk_show_data'] = sf_disk_data[0]
    sf_options['path_2'] = sf_file.get(saving_name, 'path_2')
    sf_options['single_sync'] = sf_file.get(saving_name, 'mode') == 'single'
    sf_options['mode'] = sf_file.get(saving_name, 'mode')
    sf_options['lock_folder'] = list(
        filter(None, sf_file.get(saving_name, 'lock_folder').split('|')))
    sf_options['lock_file'] = list(
        filter(None, sf_file.get(saving_name, 'lock_file').split('|')))
    sf_options['autorun'] = sf_file.getboolean(saving_name, 'autorun')
    sf_options['direct_sync'] = sf_file.getboolean(saving_name, 'direct_sync')
    sf_options['real_time'] = sf_file.getboolean(saving_name, 'real_time')

    return sf_options


def sf_save_config(save_name, **configs):
    if not os.path.exists(SF_CONFIG_PATH):
        file = open(SF_CONFIG_PATH,
                    'w', encoding='utf-8')
        file.close()
    remove_last_edit(SF_CONFIG_PATH)
    sf_file = configparser.ConfigParser()
    sf_file.read(SF_CONFIG_PATH, encoding='utf-8')
    if not sf_file.has_section(str(save_name)):
        sf_file.add_section(str(save_name))
    sf_file.set(save_name, '_last_edit_', 'True')
    sf_file.set(save_name, 'place_mode', configs['place_mode'])
    if configs['place_mode'] == 'local':
        sf_file.set(save_name, 'path_1', configs['path_1'])
        sf_file.set(save_name, 'disk_number', '')
        sf_file.set(save_name, 'direct_sync', 'False')
    else:
        sf_file.set(save_name, 'path_1', '')
        sf_file.set(save_name, 'disk_number',
                    str(GetVolumeInformation(configs['disk_show_data'].split(':')[0][-1] + ':')[1]))
        sf_file.set(save_name, 'direct_sync', str(configs['direct_sync']))
    sf_file.set(save_name, 'path_2', configs['path_2'])
    sf_file.set(save_name, 'mode', configs['mode'])
    sf_file.set(save_name, 'lock_folder', configs['lock_folder'])
    sf_file.set(save_name, 'lock_file', configs['lock_file'])
    sf_file.set(save_name, 'autorun', str(configs['autorun']))
    sf_file.set(save_name, 'real_time', str(configs['real_time']))
    sf_file.write(
        open(SF_CONFIG_PATH, 'w+', encoding='utf-8'))


def run_sf_real_time(master, lang_num):
    """
    The function `run_sf_real_time` manages a pool of real-time processes based on the configuration
    settings.
    """

    def sf_real_time_precess(setting_name):
        if setting_name not in running_process.keys():
            return
        sf_options = sf_read_config(setting_name)
        if not sf_options:
            print("Removable Volume Not Found")
            return
        gvar.set('sf_real_time_running', True)
        while not gvar.get('program_finished') and keep_running:
            s_time = time.time()
            print(setting_name + ' Running (real time)')
            if not os.path.isdir(sf_options['path_1']) or not os.path.isdir(sf_options['path_2']):
                print('Path Not Found')
                break
            _result = sf_sync_dir(master, lang_num, False, True, **sf_options)
            if _result[0] + _result[1]:  # contents moved
                time.sleep(3)
                continue
            # that makes sense, for longer scanning time means more cpu usage
            space_time = max(3, (time.time()-s_time)**0.5*20)
            print(f'{setting_name} costed {time.time()-s_time} to check')
            print(f'{setting_name} will check again after: {space_time}')
            time.sleep(space_time)
        running_process[setting_name] = False

    def add_process(proc_info_list: list):
        """
        The function adds processes to a running process list and starts a thread for each process.

        :param proc_info_list: The `proc_info_list` parameter is a list of process information. Each
        element in the list is a list itself, containing information about a specific process. The
        information includes the setting's name (setting_info[0]) and other details that are not specified
        in the code snippet
        :type proc_info_list: list
        """
        for setting_info in proc_info_list:  # add process
            running_process[setting_info[0]] = True
            Thread(target=sf_real_time_precess,
                   args=(setting_info[0],)).start()

    # a global flag for all the real-time syncing threads that determines shall they keep scanning or end
    keep_running = True
    # a dictionary for the real-time syncing threads that shows if they are running
    running_process = {}

    while not gvar.get('program_finished'):
        # While the config isn't changed, there's no need to scan it again
        if not gvar.get("sf_config_changed"):
            time.sleep(2)
            continue
        gvar.set("sf_config_changed", False)  # refresh

        keep_running = False
        while any(running_process.values()):  # wait for all the real-time syncing threads to end
            time.sleep(1)
        gvar.set('sf_real_time_running', False)
        keep_running = True

        add_process(get_real_time_infos())  # add real-time syncing threads

        time.sleep(2)
