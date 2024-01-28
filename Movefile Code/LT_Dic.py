version = 'v2.3.7'
update_time = '2024/1/28'
r_label_text_dic = {

    # Menu options
    'file_menu': ['文件', 'File'],
    'readfile_menu': ['读取/删除 配置文件', 'Read/Delete config'],
    'savefile_menu': ['保存', 'Save config'],
    'update_menu': ['检查更新', 'Check for Update'],
    'exit_menu': ['退出', 'Exit'],
    'option_menu': ['选项', 'Option'],
    'auto_update_menu': ['软件启动检查更新', 'Check for Update on Starting the app'],
    'autorun_menu': ['开机自启', 'Start Movefile with Windows'],
    'auto_quit_menu': ['自动化运行完毕后自动退出', 'Automatically quit after automation upon startup'],
    'desktop_shortcut': ['添加快捷方式到桌面', 'Add a shortcut to Desktop'],
    'language_menu': ['语言', 'Language'],
    'help_menu': ['帮助', 'Help'],
    'about_menu': ['关于本软件', 'About'],
    'precautions_menu': ['使用前注意事项', 'Precautions before use'],
    'cf_keep_menu': ['保留文件/文件格式选择', 'Keep file/format setting'],
    'cf_expire_menu': ['过期时间设定', 'Expire time setting'],
    'sf_removable_menu': ['可移动磁盘同步', 'Removable Volume mode'],
    'sf_lock_menu': ['锁定文件/文件夹选择', 'Lock folder/sile setting'],
    'log_menu': ['使用日志', 'Movefile Log'],
    'menu_hide': ['隐藏至后台', 'Hide to Backend'],

    # Taskbar options
    'taskbar_setting': ['设置界面', 'Setting Window'],
    'taskbar_hide': ['隐藏设置窗口', 'Hide Setting Window'],
    'taskbar_exit': ['退出', 'Exit'],

    # Function options
    'current_save_name': ['当前存档：', 'Current config：'],
    'label_choose_state': ['功能选择：', 'Function：'],
    'option_is_cleanfile': ['清理桌面', 'Clean Desktop'],
    'option_is_syncfile': ['同步文件', 'Syncfile'],

    # Cleanfile labels
    'cf_label_old_path': ['源文件夹：', 'Source path：'],
    'cf_browse_old_path_button': ['浏览', 'Browse'],
    'cf_browse_new_path_button': ['浏览', 'Browse'],
    'cf_label_new_path': ['移动到：', 'Moving to：'],
    'cf_label_move_options': ['移动选项：', 'Move Options：'],
    'cf_option_folder_move': ['移动文件夹', 'Move Folders'],
    'cf_option_move_lnk': ['移动快捷方式', 'Move Shortcuts (.lnk)'],
    'cf_button_adv': ['高级选项 ↓', 'Advanced Options ↓'],
    'cf_label_keep_files': ['强制保留项目：', 'Reserved Files：'],
    'cf_label_keep_formats': ['按文件格式保留：', 'Reserved Formats：'],
    'cf_label_time': ['项目保留时长(小时)：', 'Retain Item for(h)：'],
    'cf_label_expire_options': ['↑ 开始计时节点：', "↑ Since the Item's："],
    'cf_option_mode_1': ['项目最后修改时刻', "Last Modified Moment"],
    'cf_option_mode_2': ['项目最后访问时刻', "Last Accessed Moment"],
    'cf_label_start_options': ['系统选项：', 'Boot option：'],
    'cf_option_is_auto': ['开机自动按上方设置清理', 'Automatically clean as settings above upon Startup'],
    'cf_previous_files_init': [r'旧文件', r'Previous Files'],

    # Syncfile labels
    'sf_label_place_mode': ['同步模式：', 'Sync mode：'],
    'sf_option_mode_usb': ['可移动磁盘(U盘)与本地同步', 'Between Removable Volume and Local Folder'],
    'sf_option_mode_local': ['本地文件夹间同步', 'Between Local Folders'],
    'sf_option_mode_single': ['单向同步（仅从A向B同步）', 'Unidirectional Sync (A to B Only)'],
    'sf_option_mode_double': ['双向同步（皆保留最新版本）', 'Bidirectional Sync (Two way)'],
    'sf_label_path_1': [['选择可移动磁盘：', '源文件夹：'], ['Removable Volume：', 'Source Folder：']],
    'sf_label_path_2': [['本地文件夹：', '目标文件夹：'], ['Local Path：', 'Target Folder：']],
    'sf_no_disk': ['未检测到可移动磁盘', 'No removable volume detected'],
    'sf_browse_path_1_button': ['浏览', 'Browse'],
    'sf_browse_path_2_button': ['浏览', 'Browse'],
    'sf_label_lock_folder': ['禁止修改文件夹：', 'Locked Folders：'],
    'sf_browse_lockfolder_button': ['添加文件夹', 'Add Folder'],
    'sf_label_lock_file': ['禁止覆盖、删除文件：', 'Locked Files：'],
    'sf_browse_lockfile_button': ['添加文件', 'Add Files'],
    'sf_label_autorun': ['系统选项：', 'Boot option：'],
    'sf_option_autorun': [['磁盘接入自动同步', '开机自动同步'],
                          ['Start syncing once inserted',
                           'Automatically sync upon startup']],
    'sf_option_direct_sync': ['← 不显示提示弹窗', '← Skip reminder'],
    'sf_option_real_time': ['实时同步', 'Real-time syncing'],

    # ComBoPicker select all label
    'select_all': ['全选', 'Select All'],

    # Func labels
    'preview_button': ['移动项目预览', 'Action Preview'],
    'default_preview': ['点击上方 “预览” 来检查设置，并查看该设置下哪些项目将被移动', 'Click the "Action Preview" button above\nto check the settings above and view which items will be moved'],
    'preview_cost': ['扫描耗时：', 'Scan Cost: '],
    'preview_num_found': ['找到需要移动的项目： ', "Need-to-Move Objects' number： "],
    'save_button': ['保存当前配置', 'Save the config'],
    'continue_button': ['运行', 'Run'],

    # Readfile options
    'read_name_label': ['     选择存档：', '   Pick a config：'],
    'read_mode_entry': [['清理桌面(Clean Desktop)', '同步文件(Syncfile)'], ['Cleanfile', 'Syncfile']],
    'read_mode_entry_s': [['清理桌面(Clean Desktop)', 'Cleanfile'], ['同步文件(Syncfile)', 'Syncfile']],
    'del_save_button': ['删除存档', 'Delete'],
    'sure_name_bottom': ['读取存档', 'Read'],
    'sf_disk_not_found': ['请插入该存档指定的可移动磁盘来将其读取', 'Please insert the specified removable disk for this archive to read it'],

    # Savefile options
    'ask_name_window': ['设置配置存档名称', "Set Config's Name"],
    'name_label': ['  请输入存档的名称：', "     Enter a name："],
    'sure_name_button': ['确定保存', 'Confirm'],

    # Warnings & Tips
    'num_warning': ['警告：请在时间设定栏内输入数字',
                    'Warning: Please enter a number in the time setting field'],
    'blank_warning': ['警告：请填写所有非选填项目',
                      'Warning: Please fill all the blanks not optional'],
    'path_warning': ['警告：请填输入有效路径！（建议使用浏览）',
                     'Warning: Please input a path that exists (Browse suggested)'],
    'same_path_warning': ['警告：请输入两个不一样的路径！', 'Warning：Please input two different paths！'],
    'in_path_warning': ['警告：两个待同步的文件夹不能为包含关系！', '''Warning：Two folders to be synchronized \ncannot have a containing relationship！'''],
    'in_disk_path_warning': ['警告：不能将一个分区与位于该分区内的文件夹同步！', '''Warning：Cannot synchronize a partition \nwith a folder located within that partition！'''],
    'ini_error': ['''错误：配置信息有误\n请尽量不要手动更改配置文件''', """Error：Config invalid, \nplease don't edit the config file directly"""],
    'request_save': ['提示：若要让该功能更好地运作，需要保存该配置，\n并设置本软件为开机自启，\n\n注：开机自启可以在菜单栏"选项"中关闭，\n也可以设定自动化运行完毕后自动退出。\n\n选择"确定"以继续', "Notice: You must save the current config\n and set Movefile to start upon startup\nto ensure the normal functioning of this autorun function\n\nTip: this feature could be disabled\n by unchecking the startup option in 'Option' Menu,\nand you can also set Movefile to quit after running startup automation there\n\nClick 'OK' to continue"],
    'suggest_save': ['提示：使用此功能需要保存， \n且建议设定开机自启。\n\n选择"确定"来进行推荐设置(可选)', "Tip: You need to save the current config when using,\nand setting Movefile to start upon startup is suggested.\n\nClick 'OK' to follow the suggestions above (Optional)"],
    'succ_save': [['信息提示', '信息保存成功！'], ['Information prompt', 'Data saved Successfully']],
    'change_language': ['提示：需要重启本软件来让一些标签的语言改变', '''Tip：You need to restart the app\nto make the language of some labels changed'''],
    'path_not_exist_notice': ['提示：下面的路径不存在：\n', 'Notice：The following path does not exist:\n'],
    'create_path_notice': ['\n选择 "是" 来创建该路径', '\nChoose "Yes" to create this path'],
    'blank': [138, 117],
    'sure_delete': ['确认删除配置 "', 'Sure about deleting the config named "'],
    'sf_running_notice': ['提醒： 当前有实时同步进程正在运行\n如果希望其继续运行可以选"否"来隐藏本软件到后台\n(等于菜单栏上的"隐藏至后台")\n若要退出请选择"是"',
                          "Notice： There's a real-time syncing task running.\nIf you want it to keep running, \nclick 'NO' to hide this app to backend.\nElse if you want to quit, click 'Yes'"],
    'update_notice': ['提示：发现新版本，是否要更新？', 'Notice：Found a new version, do you want to update?'],
    'update_downloading': ['正在下载新版本...\n请稍后..', 'Downloading new version...\nPlease wait..'],
    'update_download_failed': ['下载失败，请检查网络连接或关闭代理', 'Download failed, please check your network connection'],
    'update_no_newer': ['当前已是最新版本', 'This is the latest version'],
}


cfdic = {
    'title_p1': ['这些文件已从 ', 'These Files from '],
    'title_p2_1': [' 移动到 ', ' are moved to '],
    'title_p2_2': [' 移除:', ' are removed:'],
    'cltitle': [' 目前很干净', ' is pretty clean now'],
    'clcontent': ['没有文件被移除', 'Nothing is moved away'],
    'errtitle': ['无法移动一些文件', "Couldn't move several files"],
    'errcontent': ['无法被移动，请在关闭正在运行的文件后重试', "Couldn't be moved, try again after closing the running file"],
    'cptitle': ['检测到同名文件：', 'Detected two files with the same name：'],
    'cpsize': ['大小：', 'Size：'],
    'cpctime': ['创建时间：', 'Birth time：'],
    'cpetime': ['最后修改时间：', 'Last changed time：'],
    'cpprompt': ['请选择操作：', 'Please select an action：'],
    'main_progress_label': ['扫描文件中...  发现文件：', 'Scanning items...  Found item：'],
    'main_progress_label1': [['总进度：', '已完成'], ['Progress：', 'Completed']],
    'main_progress_label2': ['扫描文件中...', 'Scanning items...'],
    'current_file_label': ['等待中...', 'Waiting...'],
    'current_file_label1': ['文件处理中：', 'File in process：'],
    'preview_src': ['源路径: ', 'Source: '],
    'preview_dest': ['移动到: ', 'Destination: '],
    'preview_item': ['下面的项目将被移动: ⬇', 'The following items would be moved: ⬇'],
    'preview_no_item': ['该设置下将没有项目被移动。', 'No item would be moved according to the settings above.']
}

sfdic = {
    'title_p1': ['同步成功 ', 'Sync Successfully'],
    'title_p2_1': ['"', 'The files in "'],
    'title_p2_2': ['" 与 "', '" and "'],
    'title_p2_3': ['" 中的文件已被成功同步', '" are synchronized'],
    'err_title_p1': ['配置文件出现错误', 'Error in config file:'],
    'err_title_p2_1': ['该配置文件内容出现错误：', 'We found some errors in this config file:'],
    'err_title_p2_2': ['请重新进行设置并保存，\n且不要直接手动更改配置文件', 'Please Save it again,\nand please do NOT edit the config file directly'],
    'cltitle': [' 目前很干净', ' is pretty clean now'],
    'clcontent': ['没有文件被移除', 'Nothing is moved away'],
    'errtitle': ['无法同步一些文件', "Couldn't synchronize several files"],

    'main_progress_label': ['扫描文件中...  发现文件：', 'Scanning items...  Found item：'],
    'main_progress_label1': [['总进度：', '已完成'], ['Progress：', 'Completed']],
    'main_progress_label2': ['扫描文件中...', 'Scanning items...'],
    'current_file_label': ['等待中...', 'Waiting...'],
    'current_file_label1': ['加入复制进程的文件：', 'File added into ThreadPool：'],
    'exit_sync': ['''文件正在同步中，\n确定中断同步进程并退出?''', '''Synchronization is in progress,\nAre you sure to interrupt the process and exit?'''],
    'can_not_move_notice': ["""\n无法被同步，请在关闭文件或移除重名文件后重试""", """\nCouldn't be synchronized, Please try again after closing the file\nor removing the duplicate file """],
    'new_disk_detected': [['检测到可移动磁盘 "', '" 接入,\n', '确定按配置 "', '" 进行同步?'], ['Removable partition "', '" detected,\n', 'Synchronize as config "', '" ?']],

}

progress_root_label_dic = {
    'confirm_exit_text': ['''文件正在移动中，\n确定中断进程并退出?''', '''The file is currently being moved,\nAre you sure to interrupt the process and exit?'''],
    'stopping_label': ['正在结束...', 'Quitting...'],
    'waiting_label': ['请等待片刻...', 'Please wait for a while...'],
}

help_main_text = ["""关于
软件名称： Movefile
软件版本： """ + version + """               更新时间： """ + update_time + """

功能概述：
本程序可将某个文件夹中满足一定设定要求的文件转移到另一个文件夹，或者与另外一个文件夹同步，使你可以方便地整理文件

如果对本软件功能有任何疑惑，可以查看菜单栏中的 "帮助" 选项
使用本软件进行的所有操作会在用户AppData/Roaming/Movefile文件夹下的Movefile.log记录

作者：Robert He
如果对本软件有任何改进意见，请联系作者
如果意见被采纳，新版本中会进行更改

如有功能异常请先访问 Github 查看有无新版本，或者阅读 Github 中的其他注意事项和运行机制说明
地址：

本窗口将不再自动弹出""", """About
App name： Movefile
Vision： """ + version + """               Update time： """ + update_time + """

Function overview:
This program can have files in a folder that meet the given requirements transferred to another folder or synchronize with another folder, Enabling you to organize documents easily

If you have any doubts about the function of this app, you can check the "Help" option in the menu bar
All operations performed by this app will be recorded in Roaming/Movefile/Movefile.log

Author: Robert He
If you have any suggestions for improvement of this app, please contact the author.
If the comments are adopted, changes will be made in the new version.

If there is any function abnormality, please visit Github first to check whether there is a new version, or read other precautions and operating mechanism instructions in Github.
Address: 

This notice won't be shown automatically anymore"""]

help_before_use_text = ["""使用前特别注意事项
1.本软件必须在64位Windows10及以上操作系统下运行
2.本exe文件的名称请不要改变："Movefile.exe"，否则会影响开机自启功能
3.使用本软件前请打开Windows设置中的 系统/通知和操作/通知/获取来自应用和其他发送者的通知 选项，否则会影响操作结果通知功能
5.如果经过版本更新后软件无法运行，可以尝试删除位于Roaming文件夹中的配置文件
6.若有其他原因导致软件功能无法正常运行，且无法按上面的解释修复，可以访问 Github 官方网站: 
  或直接联系作者（QQ:2567466856），我会尽快尝试帮你修复""", """Precautions before use
1.This app must be run under a 64-bit Windows 10 or above operating system.
2.Please do not change the name of this exe file："Movefile.exe", otherwise the startup function will be affected.
3.Please check the option in Windows Setting: System/Notifications/Notifications/Get notifications from apps and other senders, otherwise the operation result notifying function would be affected
5.If the app can't run after updating the new version, you can try to delete the profile located in the Roaming folder
6.If the app fails to run normally due to other reasons, and also can't be fixed as explained above, you can visit our Github website: 
   Or contact the author directly (QQ: 2567466856), I'll try to repair it for you as soon as possible"""]

cf_help_text = ["""Clean Desktop：清理文件工具
这是一个用来整理文件夹（尤其是桌面）的程序，

包含设定是否移动文件夹与快捷方式，
选取强制保留文件，按文件类型强制保留，
设定过期时间以及判断方式
开机自动运行存档等功能""", """Clean Desktop
Clean-up tool for files
This is a useful program to organize folders (especially the desktop),

Include setting whether to move the folders and shortcuts,
Selecting reserved files and reserved files' format,
Set expiration time and judgment method
Start up and automatically run archiving and other functions
"""]

cf_help_keep_text = ["""保留项目/文件格式选择功能详解
保留项目选择：
选中的项目不会被转移

保留文件格式选择：
某种格式类型的文件都不会被转移
比如选中'.exe'，即表示原文件夹中所有exe应用程序不会被转移""", """Preserve item
Keep item selection:
The selected items will not be transferred

Keep file format selection:
Files of a certain format type will not be transferred 
For example, selecting '.exe' means that
all executable files in the original folder will not be transferred"""]

cf_help_timeset_text = ["""过期时间功能详解
本软件可以获取文件的最后修改、访问时间
可以保留一定时间内修改/访问过的文件
例如若将过期时间设为"48"，判定方式设为"以最后修改时间为依据"
则运行日期前两天内修改过的文件不会被删除
如果不想用此方法，则过期时间设为"0"即可""", '''Expiration time setting
The app can obtain the latest modification and access time of the file

You can reserve files that have been modified/accessed for a certain period of time.

For example, if the expiration time is set to "48", and
the judgment method is set to "Use Items' latest edit time",
the files modified within two days before the operation date will not be deleted

If you do not want to use this method, 
set the expiration time to "0" ''']

sf_help_text = ['''Syncfile：文件同步工具
这是一个用来同步文件两个路径下文件的程序，
也可以将U盘数据与电脑同步

包括 可移动磁盘与本地磁盘 和 本地磁盘间同步 两种模式选择，
选择单向与双向同步模式，保留最新更改文件
开机自动运行存档， 实时同步， 
自动检测选定的可移动磁盘接入并自动同步等功能''', '''Syncfile
Synchronize tool for Files
This is a program used to synchronize files in two paths,
You can also synchronize USB flash disk data with the computer

It includes two modes of synchronization: 
sync between a removable disk and a local disk, or between local disks,
also select one-way or two-way synchronization mode, 
Automatically run archive after startup, keep the latest changed files,
Real-time synchronization, 
Automatically detect the access of recorded removable disks 
and automatically synchronize them
and so on''']

sf_removable_help_text = ['''可移动磁盘同步功能详解
工作原理：
读取所有 属于当前接入的可移动磁盘设备 的卷，加入待选列表中
为了防止同一个卷在不同时间接入设备时被分配了不同的卷标，
判断前后接入的是否为同一个卷的方式为 获取卷的ID并与保存的信息比对。

打开软件后，会实时获取当前设备上可移动卷的接入情况
如果发现新接入的卷在存档中，且选中了自动运行选项，
那会弹窗提示进行同步。
''', '''Removable Disk Sync
Working principle:
Read all volumes belonging to the connected removable disk devices 
and add them to the list of candidates
To prevent the same volume from being assigned different volume labels when accessing devices at different times,
the way to determine whether it is the same volume 
is to obtain the volume IDs and compare them with saved data.

After starting the app, it will obtain the access status 
of removable volumes on the current device in real-time
If a newly accessed volume is found in the archive
and the automatic run option is selected,
a pop-up prompt will ask you whether to synchronize or not.
''']

sf_lock_help_text = ['''锁定文件夹/文件功能
锁定文件夹：
当你添加了一个文件夹，这个文件夹将会被显示在待选列表中。
在待选列表内勾选这个文件夹，这个文件夹内的内容将不会被修改或删除。

锁定文件：
添加原理与锁定文件夹相同，
如果勾选一个文件，那么这个文件不会被修改。
''', '''Lock folder/file function
Lock folder:
When you add a folder, it will be displayed in the waiting list.
Check this folder in the list to be selected, 
and the contents of this folder will not be modified or deleted.

Lock file:
The principle of adding is the same as locking a folder,
If a file is checked, it will not be modified.
''']

lnk_desc = ["自动转移文件工具", "File declutter tool"]
