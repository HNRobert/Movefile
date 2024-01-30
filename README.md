# Movefile Instruction

 [*English*](#english)  [*中文*](#movefile-中文说明)

 [Update Log](#update-log---更新日志)

_________

## English

This is a program made for **organizing files**, including two main functions: [**Clean Desktop**](#clean-desktop) and [**Syncfile**](#syncfile).

If you have any confusion about the function of this software during use, you can ***check the "Help" option in the menu bar***, or ***visit this website page*** for further instructions.

All operations performed by this software will be recorded in Roaming/Movefile/Movefile.log, and you can also check it by clicking **"Movefile Log"** in the menu, then you can see what have this program done to your files at anytime.

The online update check function has been added since version 3.0.0, and you can set the *"Check for Update on Starting the app"* option to True in menu to make sure the app is always the latest version.

If you have any suggestions on improving the function or ui, you can contact the author, and changes will be made in the new version~

### Please read the following ***precautions*** before use

#### About Compatibility

***This software only supports 64bit Windows operating system now***

**Note: The notification module used in this program is a modified win10toast. The modified version adds thread pool and notification queue management functions to improve notification display logic*

#### Precautions before use

1. Please do not change the name of this exe file："Movefile.exe",
   or the startup function will be affected.

2. Please check the option in Windows Setting:
   System/Notification and operation/Notification/
   "Get notifications from apps and other senders",
   otherwise the notification function will be affected.

3. If the software cannot run after the new version,
   you can try to delete the profile located in the Roaming folder.

4. If the software fails to run normally due to other reasons, and
   also can't be repaired as explained above,
   you can contact the author directly,
   I will try to repair it for you as soon as possible.

### Clean Desktop

This is a program used to organize folders (especially the desktop)
![屏幕截图 2023-04-28 220535]

#### Function overview

This program can transfer files in a folder that have not been modified or accessed for a certain period of time and meet other setting requirements to another folder, so that you can easily organize files. Cleaning the cluttered desktop is its most useful function.

##### Including functions

- Selecting the source folder (default desktop)
- Selecting the destination to place files, or fill nothing in order to remove these files
- Setting the expiration time
- Retaining a item for certain time, and setting when to start counting the retaining time (according to the latest accessed/modified time)
- Deciding whether to move the folders and shortcuts
- Selecting the files to reserve
- Selecting the reserved file format  
- Start cleaning automatically after startup once a day

#### Detailed explanation

##### Preserve project/file format selection function

###### Reserve item selection

The selected items will not be moved

###### Reserve format selection

Files of a certain format type will not be moved.
For example, selecting '.exe' means that all executable files in the original folder will not be moved

##### Retain item for...(h) Setting

The app can obtain the latest modification and access time of the file, and you can retain files that have been modified/accessed before a certain period of time.

For example, if the expiration time is set to "48", and
the judgment method is set to "Last Modified Moment",
the files modified within two days before the operation date will not be moved

If you don't want to use this function, just set the expiration time to "0"

### Syncfile

This is a program used to synchronize files in two paths,
You can also synchronize USB flash disk data with the computer
![屏幕截图 2023-04-28 221421]

#### Syncfile Function overview

You can compare the files in the two folders, find the same files, and keep the latest version,
Then copy the files that the other folder does not have to the another folder to realize the synchronization function

##### Including functions (Syncfile)

- two modes of synchronization between removable disk and local disk and local disk
- Select one-way or two-way synchronization mode
- Keep the latest changed files
- Automatically run the archive after startup
- Automatically detect the access of archived removable disk and automatically synchronize
- Real-time sync between folders
- Lock folders and files to keep them from being modified during the synchronization

#### Syncfile Function explanation

##### Mode selection between Removable Volume and Local path

If you select the removable disk mode and save the configuration, you can select a currently inserted removable disk to synchronize with a local location

In addition, if the app is running, every time the removable disk recorded in the configuration is inserted, a prompt box will pop up automatically. You can directly start synchronization according to the settings. Of course, you can decide whether to prompt you before auto-syncing or not.

The way to determine whether the accessed disk is the disk saved in the configuration is to compare the volume serial number.

If you select synchronization between local disks, you can select two local disks for synchronization

##### Lock folder/file function

###### Lock folder

When you add a folder, it will be displayed in the list.

Check this folder in the list to be selected, and the contents of this folder will not be modified.

###### Lock file

The principle of adding is the same as locking a folder.

If a file is checked, it will not be modified.

_________

## Movefile 中文说明

这是一个用于**整理文件**的程序，包括了 [**Clean Desktop**](#clean-desktop-功能) 和 [**Syncfile**](#syncfile功能) 两个主要功能

如果使用过程中对本软件功能有任何疑惑，可以**查看菜单栏中的 "帮助" 选项**， 或者**访问本网站**来获取更多信息

使用本软件进行的所有操作会在 Roaming/Movefile/Movefile.log 中记录，也可以在菜单栏的 **"使用日志"** 中查看。

自动联网更新功能在3.0.0版本发布， 可以在菜单栏中选择"程序启动时自动检查更新"来确保当前软件为最新版。

如果对程序功能或者界面有什么改进意见，可以联系作者，新版本中会进行更改哦~

### 使用前请务必阅读下面的***使用注意事项***

#### 兼容性说明

***本软件目前仅支持 64位 Windows 操作系统下使用***

**注意：本程序使用的通知模组是魔改过的 win10toast，更改后的版本添加线程池与通知队列管理功能，改进通知显示逻辑*

#### 使用前特别注意事项

1. 本exe文件的名称请不要改变："Movefile.exe"，否则会影响开机自启功能
   如果想更改名称，可以将exe文件移至别处后创建快捷方式

2. 使用本软件前请打开Windows设置中的
   系统/通知和操作/通知/
   “获取来自应用和其他发送者的通知” 选项，
   否则会影响操作结果通知功能
  
3. 如果经过版本新后软件无法运行，
   可以尝试删除位于Roaming文件夹中的配置文件
  
4. 若有其他原因导致软件功能无法正常运行，
   且无法按上面的解释修复，
   请联系作者,我会尽快尝试帮你修复

### Clean Desktop 功能

这是一个用来整理文件夹（尤其是桌面）的程序
![屏幕截图 2023-04-28 222425]

#### 功能概述

本程序可将某个文件夹中一定时间未修改或者未访问，且满足其他一些设定要求的文件，转移到另一个文件夹，使你可以方便地整理文件

##### 包含功能

- 选择原文件夹（默认桌面）
- 选择放置文件的新文件夹，或者不填写新文件夹来直接删除这些文件
- 设置项目保留时间
- 设置保留时间判断依据（按最后修改/访问时间）
- 选择是否移动文件夹（整个文件夹移动）和和快捷方式
- 选择保留文件（列出原文件夹内文件/文件夹）
- 选择按文件格式保留（扫描原文件夹内文件后缀后列出）
- 可选开机自动按配置存档运行任务

#### 功能详解

##### 保留项目/文件格式选择功能

###### 强制保留项目选择

选中的项目不会被转移

###### 按文件格式保留选择

某种格式类型的文件都不会被转移
比如选中'.exe'，即表示原文件夹中所有exe应用程序不会被转移

##### 过期时间设定

本软件可以获取文件的最后修改、访问时间, 可以保留一定时间内修改/访问过的文件

例如若将保留时间设为"48"，判定方式设为"最后修改时间", 则运行日期前两天内修改过的文件不会被移动

如果不想用此方法，则过期时间设为"0"即可

### Syncfile功能

这是一个用来同步文件两个路径下文件的程序，也可以方便地将U盘数据与电脑同步
!!!

#### 功能概述（Syncfile）

可以将两个文件夹中的文件进行比较，找到相同的文件，保留最新版，
然后将对方没有的文件复制给对方，来实现同步的功能

##### 包括功能

- 可移动磁盘与本地磁盘 与 本地磁盘间同步 两种模式选择
- 选择单向与双向同步模式
- 保留最新更改文件
- 开机自动运行存档
- 自动检测选定的可移动磁盘接入并自动同步
- 实时同步
- 锁定文件/文件夹功能

#### Syncfile 功能详解

##### 可移动磁盘模式与本地磁盘间模式选择

如果选择可移动磁盘模式并保存配置，可以选择一个已经接入的可移动磁盘，与一个本地位置同步

此外，如果软件处于打开状态，每次接入配置中记录的可移动磁盘时，会自动跳出提示框，可选直接开始按设置同步。当然也可以选择开始同步前是否跳出提示框

判断接入的磁盘是否为配置中保存的磁盘的方式为比较卷序列号。

如果选择本地文件夹间同步，则可以选择两个本地文件夹进行同步

##### 禁止修改文件夹/文件功能

###### 禁止修改文件夹

当你添加了一个文件夹，这个文件夹将会被显示在待选列表中。

在待选列表内勾选这个文件夹，这个文件夹内的内容将不会被修改。

###### 禁止覆盖文件

添加原理与锁定文件夹相同，如果勾选一个文件，那么这个文件不会被修改。

## 特别鸣谢

本程序中的多选下拉列表框组件代码改编自CSDN博主 **只为你开心** 的 **Python tkinter自定义多选下拉列表框(带滚动条、全选)**

（ <https://blog.csdn.net/weixin_45774074/article/details/123293411> ）

Syncfile的文件夹比对函数由Stack Exchange的答主们提示，效率以得到提升；一些逻辑和代码结构的改进也要感谢他们

_________

## Update log - 更新日志

```log
0:19 2022/12/30
Movefile v1.2.2
更新内容：
修复了一些bug

1:04 2023/1/2
Movefile v1.3.0
更新内容：
更改了配置文件的保存地址至用户文件夹\AppData\Local\Movefile
添加了一些帮助内容
更改格式白名单的设置，使其与文件白名单内文件格式同步
更强悍的性能
修复了一些bug

22:35 2023/1/3
Movefile v1.3.1
更新内容：
更改配置文件的保存地址至用户文件夹\AppData\Roaming\Movefile
修复了用户文件夹名称与用户名称不同时无法运行的bug
更改设定为无法将目录内文件夹移动，后续将完善目录内文件夹的移动的功能

4:05 2023/1/12
Movefile v1.4.0
更新内容：
添加移动文件夹选项
更改了UI排版
更改了一些繁琐的名称，
修复了多选下拉列表框中“全选”进入输入框的bug
修复了其他一些逻辑bug

9:20 2023/1/12
Movefile v1.4.1
更新内容：改善代码语法，改进一些逻辑

14:30 2023/1/12
Movefile v1.4.2
更新内容：修复了文件夹移动的bug

1:00 2023/1/14
Movefile v1.4.3
更新内容：修复了一些漏洞，开启 Syncfile 项目

3:14 2023/1/27
Movefile v2.0.0
更新内容：
新增加Syncfile功能，可以同步文件
自动识别可移动磁盘，同步文件
修复了很多bug

3:00 2023/1/28
Movefile v2.0.1
更新内容：修复了一些初始化的Bug

20:46 2023/2/9
Movefile v2.1.0
更新内容：
推出英语版
优化代码结构和多线程
优化文件同步进度条
修复了一些Bug

23:58 2023/4/27
Movefile v2.2.0
更新内容：
修复了闪退的bug
优化逻辑，添加锁定文件夹/文件功能

20:50 2023/4/28
Movefile v2.2.1
更新内容：
修复了删除存档后的闪退问题
添加新文件夹选择限制，包括不能有包含关系等

23:30 2023/5/7
Movefile v2.3.0
更新内容：
改进Cleanfile逻辑，遇到重名文件将覆盖
Cleanfile的新目录框若不填写可将文件删除
添加一些标签的双语版本

2:39 2023/8/19
Movefile v2.3.1
更新内容：
添加进程检测功能，不会重复打开多个进程，
检测到有已经打开的本软件进程会显示设置主窗口；
重构syncfile的逻辑以提高效率
采用多线程复制文件来加速；
修复打开多个子窗口再关闭后无法关闭软件的问题；
修复win10toast模块的内置bug，采用队列推送消息；
优化代码结构；
修复开机自启无法自动运行的Bug；

18:48 2023/8/21
Movefile v2.3.2
更新内容：
改进开机自启的逻辑，优化了一些翻译
修复了其他一些bug

21:06 2023/11/24
Movefile v2.3.3
更新内容：
彻底修复开机自启无法自动运行的Bug，
添加logging功能，
使所有执行的操作被记录在Roaming/Movefile/Movefile.log中

21:18 2023/11/30
Movefile v2.3.4
更新内容：
更改开机自启的判断逻辑，使判定更加准确
修复Syncfile功能磁盘同步的路径问题
将开始菜单快捷方式添加功能改为添加桌面快捷方式
修复其他一些小bug，完善logging与import

16:30 2023/12/3
Movefile v2.3.5
更新内容：
开机自启时提前隐藏窗口使其彻底不会被显示（而不是闪一下）
修复Syncfile同步时会忽略一些缓存文件的问题
修复其他一些小Bug，完善安装包

21:40 2023/12/6
Movefile v2.3.6
Update Content:
Enhanced error capture capability
Add exit button on menu
Optimized structure and logic
Bugs Fixed, More stable

17:20 2023/12/12
Movefile v2.3.7
Update Content:
More stable ComBoPicker
Syncfile Lockfolder function fixed
Startup autorun function fixed
Current config label upgraded
Translation complement
Saving & Reading improvement

21:45 2024/1/29
Movefile v3.0.0
Update Content:
Update UI & Label
Add Real-time syncing function
Action Preview function
Hidden removable disk syncing function
Online check update function
Quit after autorun option
Visible Logging function
More efficient Syncfile scanning & copying
General Reconfiguration
More stable daily use, bugs fixed
```
