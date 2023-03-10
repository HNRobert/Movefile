vision = 'v2.1.0'
update_time = '2023/1/30'
r_label_text_dic = {
    'file_menu': ['文件', 'File'],
    'readfile_menu': ['读取配置文件', 'Read config'],
    'savefile_menu': ['保存', 'Save config'],
    'option_menu': ['选项', 'Option'],
    'autorun_menu': ['开机自动启动本软件', 'Start automatically'],
    'language_menu': ['语言', 'Language'],
    'help_menu': ['帮助', 'Help'],
    'about_menu': ['关于本软件', 'About'],
    'precautions_menu': ['使用前注意事项', 'Precautions before use'],
    'cf_keep_menu': ['保留文件/文件格式选择', 'Keep file/format setting'],
    'cf_expire_menu': ['过期时间设定', 'Expire time setting'],

    'taskbar_setting': ['设置界面', 'Setting Window'],
    'taskbar_exit': ['退出', 'Exit'],

    'label_choose_state': ['功能选择：', 'Function：'],
    'option_is_cleanfile': ['清理文件', 'Cleanfile'],
    'option_is_syncfile': ['同步文件', 'Syncfile'],
    'cf_label_old_path': ['原文件夹路径：', 'original path：'],
    'cf_browse_old_path_button': ['浏览', 'Browse'],
    'cf_browse_new_path_button': ['浏览', 'Browse'],
    'cf_label_new_path': ['目标文件夹路径：', 'Target path：'],
    'cf_label_move_options': ['文件移动选项：', 'Expire Criteria：'],
    'cf_option_mode_1': ['以项目最后修改时间为过期判断依据', "Use Items' latest edit time"],
    'cf_option_mode_2': ['以项目最后访问时间为过期判断依据', "Use Items' latest ask time"],
    'cf_option_folder_move': ['移动项目包括文件夹', 'Move items including Folders'],
    'cf_label_keep_files': ['保留项目(选填)：', 'Reserved Files(opt)：'],
    'cf_label_keep_formats': ['保留文件格式(选填)：', 'Reserved Fmts(opt)：'],
    'cf_label_time': ['过期时间设定(小时)：', 'Expire Hours：'],
    'cf_label_start_options': ['系统选项：', 'Boot option：'],
    'cf_option_is_auto': ['开机自动运行本存档(若保存)', 'Automatically run this config after Startup(if saved)'],
    'sf_label_place_mode': ['路径模式选择：', 'Sync-Path mode：'],
    'sf_option_mode_usb': ['可移动磁盘(卷)同步模式', 'Removable Volume mode'],
    'sf_option_mode_local': ['本地文件夹同步模式', 'Local Folder mode'],
    'sf_label_path_1': [['选择可移动磁盘：', '文件夹路径-A：'], ['Removable Volume：', 'Folder Path-A：']],
    'sf_label_path_2': [['本地文件夹路径：', '文件夹路径-B：'], ['Local Path：', 'Folder Path-B：']],
    'sf_no_disk': ['未检测到可移动磁盘', 'No removable disk detected'],
    'sf_browse_path_1_button': ['浏览', 'Browse'],
    'sf_browse_path_2_button': ['浏览', 'Browse'],
    'sf_label_mode': ['同步模式选择：', 'Sync mode：'],
    'sf_option_mode_double': ['双向同步（皆保留最新版本）', 'Two-way Sync'],
    'sf_option_mode_single': ['单向同步（仅从A向B同步）', 'One-way Sync'],
    'sf_label_lock_folder': ['锁定文件夹：', 'Reserved Folders：'],
    'sf_browse_lockfolder_button': ['添加文件夹', 'Add Folder'],
    'sf_label_lock_file': ['锁定文件：', 'Reserved Files：'],
    'sf_browse_lockfile_button': ['添加文件', 'Add Files'],
    'sf_label_autorun': ['系统选项：', 'Boot option：'],
    'sf_option_autorun': [['可移动磁盘接入后自动按本存档设置同步(若保存)', '开机自动运行本存档(若保存)'], ['Automatically run when this Removable Volume inserted', 'Automatically run this config after Startup(if saved)']],
    'save_button': ['保存', 'Save'],
    'continue_button': ['运行当前配置', 'Run current configuration'],

    'read_name_label': ['     选择存档：', '   Pick a config：'],
    'read_mode_entry': [['清理文件(Cleanfile)', '同步文件(Syncfile)'], ['Cleanfile', 'Syncfile']],
    'del_save_button': ['删除存档', 'Delete'],
    'sure_name_bottom': ['读取存档', 'Read'],

    'ask_name_window': ['设置配置存档名称', "Set Config's Name"],
    'name_label': ['  请输入存档的名称：', "     Enter a name："],
    'sure_name_button': ['确定保存', 'Confirm'],

    'num_warning': ['警告：请在时间设定栏内输入数字',
                    'Warning: Please enter a number in the time setting field'],
    'blank_warning': ['警告：请填写所有非选填项目',
                      'Warning: Please fill all the blanks not optional'],
    'path_warning': ['警告：请填输入有效路径！（建议使用浏览）',
                     'Warning: Please input a path that exists (Browse suggested)'],
    'same_path_warning': ['警告：请输入两个不一样的路径！', 'Warning：Please input two different paths！'],
    'ini_error': ['''错误：配置信息无效
请尽量不要手动更改ini配置文件''', """Error：Config File invalid, 
please don't edit the config file directly"""],
    'succ_save': [['信息提示', '信息保存成功！'], ['Information prompt', 'Data saved Successfully']],
    'change_language': ['提示：需要重启本软件来让一些标签的语言改变', '''Tip：You need to restart the software
to make the language of some labels changed''']
    }

cr_label_text_dic = {
    'c_label': ['Movefile 初始化中...', 'Movefile initializing...']}

sf_label_text_dic = {
    'main_progress_label': ['扫描文件中...  发现文件：', 'Scanning items...  Find item：'],
    'main_progress_label1': [['总进度：', '已完成'], ['Progress：', 'Completed']],
    'main_progress_label2': ['扫描文件中...', 'Scanning items...'],
    'current_file_label': ['等待中...', 'Waiting...'],
    'current_file_label1': ['文件同步中：', 'File in process：'],
    'exit_sync': ['''文件正在同步中，
确定中断同步进程并退出?''', '''Synchronization is in progress,
Are you sure to interrupt the process and exit?'''],
    'can_not_move_notice': ["""
无法被移动，请在关闭文件或移除重名文件后重试""", """
Couldn't be moved, Please try again after closing the file
or removing the duplicate file """]

    }

help_main_text = ["""软件名称： Movefile
软件版本： """ + vision + """               更新时间： """ + update_time + """

功能概述：
本程序可将某个文件夹中满足一定设定要求的文件
转移到另一个文件夹，或者与另外一个文件夹同步
使你可以方便地整理文件

如果对本软件功能有任何疑惑，可以查看菜单栏中的 "帮助" 选项

作者：Robert He
如果对本软件有任何改进意见，请联系作者
如果意见被采纳，新版本中会进行更改

如有功能异常请先访问 Github 查看有无新版本，
或者阅读 Github 中的其他注意事项和运行机制说明
地址：https://github.com/HNRobert/Movefile""", """Software name： Movefile
Vision： """ + vision + """               Update time： """ + update_time + """

Function overview:
This program can make files in a folder that meet the given requirements
Transfer to another folder or synchronize with another folder,
Enabling you to organize documents easily

If you have any doubts about the function of this software,
you can check the "Help" option in the menu bar

Author: Robert He
If you have any suggestions for improvement of this software, 
please contact the author
If the comments are adopted, changes will be made in the new version.

If there is any function abnormality,
please visit Github first to check whether there is a new version,
Or read other precautions and operating mechanism instructions in Github.
Address: https://github.com/HNRobert/Movefile"""]

help_before_use_text = ["""使用前特别注意事项：
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
  且无法按上面的解释修复，可以访问 Github 网站
  或直接联系作者（QQ:2567466856），我会尽快尝试帮你修复""", """Precautions before use:
1.This software must be run under a 64-bit operating system,
   The 32-bit operating system version will be introduced later.
2.Please do not change the name of this exe file："Movefile """ + vision + """.exe"
   Otherwise, the startup function will be affected.
3.Please open the option in the windows setting:
   System/notification and operation/notification/
   "Get notifications from apps and other senders",
   Otherwise, the operation result notification function will be affected
4.Please put the software into the
   'Antivirus scanning exclusion item' of Windows Security Center,
   Otherwise, it will be deleted directly at runtime
   This is because this software involves changing the Startup item.
   If this software is accidentally deleted in use,
   Please retrieve this software in the "Protection History"
   of virus threat and protection in Windows Security Center 
   Or other security software
5.If the software cannot run after the new version,
   You can try to delete the profile located in the Roaming folder
6.If the software fails to run normally due to other reasons, and
   Also can't be repaired as explained above,
   You can visit Github website https://github.com/HNRobert/Movefile
   Or contact the author directly (QQ: 2567466856), 
   I will try to repair it for you as soon as possible"""]

cf_help_text = ["""Cleanfile
清理文件工具

这是一个用来整理文件夹（尤其是桌面）的程序，
也是Movefile推出的第一个程序块
包含选取保留文件，保留文件类型
设定是否移动文件夹，
设定过期时间以及判断方式
开机自动运行存档等功能""", """Cleanfile
Clean up file tool

This is a program used to organize folders (especially the desktop),
It is also the first program block launched by Movefile
Include selecting reserved files and reserved files' format,
Set whether to move the folder,
Set expiration time and judgment method
Start up and automatically run archiving and other functions
"""]

cf_help_keep_text = ["""保留项目/文件格式选择功能详解：

保留项目选择：
选中的项目不会被转移

保留文件格式选择：
某种格式类型的文件都不会被转移
比如选中'.lnk'，即表示原文件夹中所有的快捷方式不会被转移""", """Preserve project/file format selection function:

Keep item selection:
The selected items will not be transferred

Keep file format selection:
Files of a certain format type will not be transferred 
For example, selecting '. lnk' means that
all shortcuts in the original folder will not be transferred"""]

cf_help_timeset_text = ["""过期时间功能详解：

本软件可以获取文件的最后修改、访问时间
可以保留一定时间内修改/访问过的文件
例如若将过期时间设为"48"，判定方式设为"以最后修改时间为依据"
则运行日期前两天内修改过的文件不会被删除
如果不想用此方法，则过期时间设为"0"即可""", '''Expiration time setting:
The software can obtain the latest modification and access time of the file

You can reserve files that have been modified/accessed for a certain period of time.

For example, if the expiration time is set to "48", and
the judgment method is set to "Use Items' latest edit time",
the files modified within two days before the operation date will not be deleted

If you do not want to use this method, 
set the expiration time to "0" ''']

sf_help_text = ['''Syncfile
同步文件工具

这是一个用来同步文件两个路径下文件的程序，
也可以将U盘数据与电脑同步

包括 可移动磁盘与本地磁盘 和 本地磁盘间同步 两种模式选择，
选择单向与双向同步模式，保留最新更改文件
开机自动运行存档
自动检测选定的可移动磁盘接入并自动同步等功能''', '''Syncfile
Synchronize File Tool

This is a program used to synchronize files in two paths,
You can also synchronize USB flash disk data with the computer

It includes two modes of synchronization: 
sync between removable disk and local disk or between local disks,
also select one-way or two-way synchronization mode, 
auto run archive after startup, keep the latest changed files,
Automatically detect the access of recorded removable disks and automatically synchronize them
and so on''']
