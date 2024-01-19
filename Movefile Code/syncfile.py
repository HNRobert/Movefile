

import configparser
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from filecmp import dircmp
from pathlib import Path
from shutil import Error as shutil_Error
from shutil import copy2 as shutil_copy2
from threading import Thread

import LT_Dic
from Movefile import gvar
from mf_const import MF_CONFIG_PATH, MF_ICON_PATH, SF_CONFIG_PATH
from mf_mods import language_num, mf_log, mf_toaster


def sf_sync_dir(master_root, path1, path2, single_sync, language_number, area_name=None, pass_file_paths='', pass_folder_paths='', preview=False):
    """
    The `sf_sync_dir` function synchronizes files between two directories, displaying progress using a progress bar.

    :param master_root: The master_root parameter is a string that represents the root window variable of the Movefile application. It is the mother root to create and display the progress bar.
    :param path1: The path to the first folder that you want to synchronize
    :param path2: The `path2` parameter represents the destination directory where the files will be synchronized to
    :param single_sync: A boolean value indicating whether to perform a single sync or not. If True, only files present in the first folder will be synced to the second folder. If False, files present in both folders will be synced
    :param language_number: The `language_number` parameter is an integer that represents the language code to be used for displaying messages and notifications. It is used to select the appropriate language from a dictionary of language translations
    :param area_name: The `area_name` parameter is an optional parameter that represents the label of the partitions being synchronized. It is used in the notification message to indicate which area of files has been synchronized. If not provided, the default name will be the last part of the `path1`
    :param pass_file_paths: The `pass_file_paths` parameter is a string that represents a comma-separated list of file paths that should be excluded from the synchronization process. These files will not be moved or replaced during the synchronization
    :param pass_folder_paths: The `pass_folder_paths` parameter is a string that represents the paths of folders that should be excluded from the synchronization process. These folders will not be compared or synchronized with the other folders. Multiple folder paths can be separated by commas
    """

    from mfprogressbar import MFProgressBar

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
        cmp_data = dircmp(folderA_path, folderB_path, ignore=[])
        add_diff_data(0, cmp_data.diff_files)
        add_diff_data(1, cmp_data.left_only)
        add_diff_data(2, cmp_data.right_only, True)
        """
        print("--------------------------------\n" + folderA_path + "\n" + folderB_path)
        print(cmp_data.diff_files)
        print(cmp_data.left_only)
        print(cmp_data.right_only)
        print("\n")
        """
        for com_dir in cmp_data.common_dirs:
            dir_data = diff_files_in(os.path.join(
                folderA_path, com_dir), os.path.join(folderB_path, com_dir))
            for i in range(3):
                diff_data[i].extend(dir_data[i])
        return diff_data

    def get_sf_tasks(_bar_root: MFProgressBar):
        """
        The function "get_task" compares the two folder and decides which file need to be moved or replaced.

        :param _bar_root: The parameter `_bar_root` is likely a variable or object that represents the
        root node or starting point of a tree or hierarchy structure. It could be used to navigate or
        perform operations on the tree or hierarchy
        """
        def judged_task(fileA: str, fileB: str, only_one: bool = False):
            """
            The function `judge_and_append` takes two file names as input and a boolean value indicating
            whether to append the contents of fileB to fileA or not.

            :param fileA: A string representing the path to the first file
            :type fileA: str
            :param fileB: The `fileB` parameter is a string that represents the file name or file path
            of the second file
            :type fileB: str
            """

            if not only_one and int(os.stat(fileA).st_mtime) < int(os.stat(fileB).st_mtime):
                if single_sync:
                    return None
                fileA, fileB = fileB, fileA
            if any(fileB.startswith(p_folder) and p_folder != '' for p_folder in pass_folder_paths.split(',')) or any(
                    fileB == p_file for p_file in pass_file_paths.split(',')):
                return None
            _bar_root.set_label1(
                LT_Dic.sfdic['main_progress_label'][language_number] + fileA[0].split('\\')[-1])
            return [fileA, fileB]

        sync_tasks = []  # task items' format: [source_file_path, dest_file_path]
        diff_item_data = diff_files_in(path1, path2)
        for a_only_item in diff_item_data[1]:
            sync_tasks.append(judged_task(
                a_only_item[0], a_only_item[1], True))
        if not single_sync:
            for b_only_item in diff_item_data[2]:
                sync_tasks.append(judged_task(
                    b_only_item[0], b_only_item[1], True))
        for diff_item in diff_item_data[0]:
            sync_tasks.append(judged_task(diff_item[0], diff_item[1]))

        sync_tasks = list(filter(None, sync_tasks))
        return sync_tasks

    def synchronize_files(baroot: MFProgressBar, task):
        """
        The function `synchronize_files` takes two parameters, `baroot` and `task`, and does some kind of file synchronization operation.

        :param baroot: The `baroot` parameter is a string that represents the root directory of the source files. It is the directory from which the files will be synchronized
        :param task: The `task` parameter is a string that represents the specific task or operation that needs to be performed on the files
        """
        baroot.main_progress_bar['value'] += 0
        baroot.set_label2(
            LT_Dic.sfdic["current_file_label1"][language_number] + task[0].split('\\')[-1])
        source_file_path, dest_file_path = task
        dest_path = Path(dest_file_path)
        # Create parent directories if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil_copy2(source_file_path, dest_file_path)
        except shutil_Error:
            return source_file_path
        return None

    def run_sync_tasks(baroot: MFProgressBar, tasks):
        """
        The function "run_sync_tasks" performs synchronous tasks.

        :param baroot: The progress bar root object
        """
        sf_error_name = ''
        baroot.main_progress_bar['value'] = 0
        baroot.progress_root.update_idletasks()
        baroot.main_progress_bar['maximum'] = len(tasks)
        baroot.set_label1(
            f'{LT_Dic.sfdic["main_progress_label1"][language_number][0]}{str(baroot.main_progress_bar["value"])}/{str(len(tasks))}  {LT_Dic.sfdic["main_progress_label1"][language_number][1]}')
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(
                synchronize_files, baroot, task) for task in tasks]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    sf_error_name += result + ' , '

                baroot.main_progress_bar['value'] += 1
                baroot.set_label1(
                    f'{LT_Dic.sfdic["main_progress_label1"][language_number][0]}{str(baroot.main_progress_bar["value"])}/{str(len(tasks))}  {LT_Dic.sfdic["main_progress_label1"][language_number][1]}')
                baroot.progress_root.update_idletasks()

        baroot.progress_root.withdraw()
        path_name_1 = path1.split('\\')[-1]
        if area_name:
            path_name_1 = area_name
        sf_show_notice(path_name_1, path2.split(
            '\\')[-1], sf_error_name, language_number=language_number)
        baroot.progress_root.destroy()

    if path1[-1] != ':' and not os.path.exists(path1):
        os.mkdir(path1)
    if not os.path.exists(path2):
        os.mkdir(path2)
    sync_bar_root = MFProgressBar('Movefile  -Syncfile Progress',
                                  LT_Dic.sfdic["main_progress_label2"][language_number],
                                  LT_Dic.sfdic["current_file_label"][language_number],
                                  language_number)
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
        run_tasks.join()
    sync_bar_root.progress_root_destruction()
    sync_bar_root_task.join()
    return sf_tasks


def sf_show_notice(path_1, path_2, sf_error_name, language_number):
    sf_notice_title = LT_Dic.sfdic["title_p1"][language_number]
    sf_notice_content = LT_Dic.sfdic["title_p2_1"][language_number] + path_1 + \
        LT_Dic.sfdic["title_p2_2"][language_number] + path_2 + \
        LT_Dic.sfdic["title_p2_3"][language_number]
    mf_log("\n" + sf_notice_title + "\n" + sf_notice_content)
    mf_toaster.show_toast(sf_notice_title,
                          sf_notice_content,
                          icon_path=MF_ICON_PATH,
                          duration=10,
                          threaded=False)

    if len(sf_error_name) > 0:
        sf_error_title = LT_Dic.sfdic["errtitle"][language_number]
        sf_error_content = sf_error_name + \
            LT_Dic.sfdic['can_not_move_notice'][language_number]
        mf_log("\n" + sf_error_title + "\n" + sf_error_content)
        mf_toaster.show_toast(sf_error_title,
                              sf_error_content,
                              icon_path=MF_ICON_PATH,
                              duration=10,
                              threaded=False)


def sf_autorun_operation(master, place, saving_datas=None):
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
    sf_file.read(SF_CONFIG_PATH)
    mf_file = configparser.ConfigParser()
    mf_file.read(MF_CONFIG_PATH)

    def autorun_movable_sf(data):
        for saving_data in data:
            path1 = saving_data[0]
            path2 = sf_file.get(saving_data[2], 'path_2')
            lockfolder = sf_file.get(saving_data[2], 'lock_folder')
            lockfile = sf_file.get(saving_data[2], 'lock_file')
            single_sync = True
            if sf_file.get(saving_data[2], 'mode') == 'double':
                single_sync = False
            sf_sync_dir(master, path1, path2, single_sync, language_num(mf_file.get('General', 'language')), saving_data[1],
                        lockfile, lockfolder)

    def autorun_local_sf(data_names):
        for saving_data in data_names:
            path1 = sf_file.get(saving_data, 'path_1')
            path2 = sf_file.get(saving_data, 'path_2')
            lockfolder = sf_file.get(saving_data, 'lock_folder')
            lockfile = sf_file.get(saving_data, 'lock_file')
            single_sync = sf_file.get(saving_data, 'mode') == 'single'
            sf_sync_dir(master, path1, path2, single_sync, language_number=language_num(mf_file.get('General', 'language')),
                        pass_folder_paths=lockfolder, pass_file_paths=lockfile)
            mf_log(
                f'\nAutomatically ran Syncfile operation as config "{saving_data}"')

    if place == 'movable':
        autorun_movable_sf(saving_datas)
    elif place == 'local':
        autorun_local_sf(get_sf_startup_savings())


def fixed_sf_config(sf_config_file: configparser.ConfigParser, saving_name: str):
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
    option_names = ['lock_folder', 'lock_file',
                    'mode', 'autorun', 'real_time', 'direct_sync']
    default_values = ['', '', 'single', 'False', 'False', 'False']
    for option, value in zip(option_names, default_values):
        if not sf_config_file.has_option(saving_name, option):
            sf_config_file.set(saving_name, option, value)
    return True


def get_sf_savings_with(*wants, **conditions):
    sf_dat = configparser.ConfigParser()
    sf_dat.read(SF_CONFIG_PATH)
    target_savings = []  # [volume id, saving_name, direct_sync]
    for saving in sf_dat.sections():
        if not fixed_sf_config(sf_dat, saving):
            continue
        for key, value in conditions.items():
            if sf_dat.get(saving, key) != value:
                break
        else:
            target_savings.append([saving] +
                                  [sf_dat.get(saving, want_item) for want_item in wants])
    return target_savings


def get_sf_startup_savings():
    wants = []
    conditions = {'place_mode': 'local', 'autorun': 'True'}
    return get_sf_savings_with(*wants, **conditions)


def get_movable_autorun_infos():
    wants = ['disk_number', 'direct_sync']
    conditions = {'place_mode': 'movable', 'autorun': 'True'}
    return get_sf_savings_with(*wants, **conditions)


def get_real_time_infos():
    wants = ['path_2', 'place_mode']
    conditions = {'autorun': 'True', 'real_time': 'True'}
    return get_sf_savings_with(*wants, **conditions)


def sf_real_time_runner():
    real_time_settings = get_real_time_infos()
    while not gvar.get('program_finished'):
        if gvar.get("sf_config_changed"):
            gvar.set("sf_config_changed", False)
            real_time_settings = get_real_time_infos()
        print(real_time_settings)
        time.sleep(1)
