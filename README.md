# Movefile
#### （中文版说明位于下方）
This is a program for organizing files, including two main functions of Cleanfile and Syncfile.

The .exe file only provides packaged files released by the distribution. If the semantics of the code are not changed or the function is unstable, the latest packaged file will not be provided;

Beta programs will not be packaged. If you want to have a better use experience, please download the latest release version.

If you have any doubts about the function of this software during use, you can check the "Help" option in the menu bar.

Due to its aplenty functions, the main program code is quite lengthy. If you have any suggestions on improving the code structure, you can contact the author, and changes will be made in the new version~

Please read the following precautions before use

### About Compatibility
The .exe files provided here only support 64-bit Windows operating system, and Win10 works best

If your operating system is 32-bit Windows, you can download the code file, and then package it as the .exe file of the 32-bit operating system

##### This software only supports Windows operating system!

#### pyinstaller packaging method:

First install the python environment. After the installation of python, open cmd to install pyinstaller (pip install pyinstaller)

If you want to package it as 32-bit exe, you should package it in 32-bit Python.

After installation, open the 【Movefile Code】 folder, enter 【cmd】 in the path box of the folder, and then enter 【pyinstaller - i Movefile.ico - noupx Movefile.pyw -- onefile】 in the pop-up command prompt window ,then get the packed file in the output 【dist】 folder.

### Precautions before use:

1.Please do not change the name of this exe file："Movefile vX.X.X.exe",
   or the startup function will be affected.

2.Please open the option in the windows setting:
   System/notification and operation/notification/
   "Get notifications from apps and other senders",
   otherwise the notification function will be affected.

3.Please put the software into the
   'Antivirus scanning exclusion item' of Windows Security Center.
   otherwise, it might be deleted directly at runtime.
   That is because this software involves changing the Startup item.
   If this software is accidentally deleted in use,
   please retrieve this software in the "Protection History"
   of virus threat and protection in Windows Security Center, 
   Or other security software

4.If the software cannot run after the new version,
   you can try to delete the profile located in the Roaming folder.

5.If the software fails to run normally due to other reasons, and
   also can't be repaired as explained above,
   you can contact the author directly, 
   I will try to repair it for you as soon as possible.

## Cleanfile
This is a program used to organize folders (especially the desktop), and the first program block launched by Movefile
![屏幕截图 2023-02-11 144857](https://user-images.githubusercontent.com/120773486/218244939-669a39a0-265f-4242-9ec2-56f22cc044e2.png)

### Function overview
This program can transfer files in a folder that have not been modified or accessed for a certain period of time and meet other setting requirements to another folder, so that you can easily organize files

#### Including functions: 
```
select the original folder (default desktop)
select the new folder to place files
set the expiration time
set the judgment basis for the expiration time (according to the latest ask/edit time)
select whether to move the folder (currently only the entire folder is supported)
Select the reserved file (list the files/folders in the original folder)
select the reserved file format (list after scanning the filenames' suffix in the original folder) 
start cleaning automatically after startup
```
### Function explanation

#### Preserve project/file format selection function:
##### Keep item selection:
The selected items will not be transferred
##### Keep file format selection:
Files of a certain format type will not be transferred
For example, selecting '. lnk' means that all shortcuts in the original folder will not be transferred

#### Expiration time setting:
The software can obtain the latest modification and access time of the file

Files that have been modified/accessed for a certain period of time can be retained

For example, if the expiration time is set to "48", the judgment method is set to "Use Items' latest edit time"
The files modified within two days before the operation date will not be deleted

If you do not want to use this method, set the expiration time to "0"

## Syncfile
This is a program used to synchronize files in two paths,
You can also synchronize USB flash disk data with the computer
![屏幕截图 2023-02-11 145240](https://user-images.githubusercontent.com/120773486/218245067-74255275-aa50-474c-b721-1b15f8f4c2c7.png)

### Function overview
You can compare the files in the two folders, find the same files, and keep the latest version,
Then copy the files that the other party does not have to the other party to realize the synchronization function

#### Including functions: 
```
two modes of synchronization between removable disk and local disk and local disk
Select one-way or two-way synchronization mode
Keep the latest changed files
Automatically run the archive after startup
Automatically detect the archived removable disk access and automatically synchronize
Lock folders and files to keep them from being synchronized 
```
### Function explanation

#### Mode selection between Removable Volume and Local path:
If you select the removable disk mode and save the configuration, you can select a connected removable disk to synchronize with a local location

In addition, if the software is open, every time the removable disk recorded in the configuration is accessed, a prompt box will pop up automatically. You can directly start synchronization according to the settings.

The way to determine whether the accessed disk is the disk saved in the configuration is to compare the volume serial number.

If you select synchronization between local disks, you can select two local disks for synchronization

#### Lock folder/file function:

##### Lock folder:
When you add a folder, it will be displayed in the waiting list.

Check this folder in the list to be selected, and the contents of this folder will not be modified or deleted.

##### Lock file:
The principle of adding is the same as locking a folder.

If a file is checked, it will not be modified.

# Movefile 中文说明
这是一个用于整理文件的程序，包括了 Cleanfile 和 Syncfile 两个主要功能

exe文件只提供发行版发布的打包的文件，若代码的语义未改变，或者功能不稳定，则不会提供最新的打包文件；

Beta 版程序不会打包，如果想要有更加好的使用体验，请下载最新发布版本

如果使用过程中对本软件功能有任何疑惑，可以查看菜单栏中的 "帮助" 选项

由于功能比较多，主程序代码比较冗长，如果对代码结构有什么改进意见，可以联系作者，新版本中会进行更改哦~

使用前请务必阅读下面的使用注意事项

### 兼容性说明
代码中的exe文件仅支持windows64位操作系统，Win10效果最佳

如果操作系统是32位Windows，可以下载pyw文件，然后自行打包为32位操作系统的exe文件

##### 本软件仅支持Windows操作系统下使用！

#### pyinstaller打包法：

先要安装python环境，python安装完后打开cmd安装pyinstaller (pip install pyinstaller)

如果想打包为32为的exe，那就要在32位的Python下打包

安装完成后，打开【Movefile Code】文件夹，文件夹的索引框内输入【cmd】，然后在弹出的命令提示框内输入【pyinstaller -i Movefile.ico -noupx Movefile.pyw --onefile】，就可以在产出的【dist】文件夹内得到打包好的exe文件。

### 使用前特别注意事项：
*1.本exe文件的名称请不要改变："Movefile vX.X.X.exe"，否则会影响开机自启功能
  如果想更改名称，可以将exe文件移至别处后创建快捷方式

*2.使用本软件前请打开Windows设置中的
  系统/通知和操作/通知/
  “获取来自应用和其他发送者的通知” 选项，
  否则会影响操作结果通知功能
  
*3.使用本软件前请先将本软件放入
  Windows安全中心的防病毒扫描排除项中，
  否则在运行时会被直接删除。
  这是因为本软件涉及更改开机启动项。
  如果本软件在使用中被意外删除，
  可以在Windows安全中心中
  病毒威胁和防护的 "保护历史记录"
  或其他安全软件中找回本软件
  
4.如果经过版本新后软件无法运行，
  可以尝试删除位于Roaming文件夹中的配置文件
  
5.若有其他原因导致软件功能无法正常运行，
  且无法按上面的解释修复，
  请联系作者,我会尽快尝试帮你修复

## Cleanfile
这是一个用来整理文件夹（尤其是桌面）的程序，也是Movefile推出的第一个程序块
![保存文件](https://user-images.githubusercontent.com/120773486/215319327-806c44c7-1165-4aa1-ae9d-0dd6a8f7ee12.png)

### 功能概述
本程序可将某个文件夹中一定时间未修改或者未访问，且满足其他一些设定要求的文件，转移到另一个文件夹，使你可以方便地整理文件

#### 包含功能：
```
选择原文件夹（默认桌面）
选择放置文件的新文件夹
设置过期时间
设置过期时间判断依据（按最后修改/访问时间）
选择是否移动文件夹（目前只支持整个文件夹移动）
选择保留文件（列出原文件夹内文件/文件夹）
选择保留文件格式（扫描原文件夹内文件后缀后列出）
可选开机自动按配置存档运行任务
```
### 功能详解

#### 保留项目/文件格式选择功能：
保留项目选择：
选中的项目不会被转移

保留文件格式选择：
某种格式类型的文件都不会被转移
比如选中'.lnk'，即表示原文件夹中所有的快捷方式不会被转移

#### 过期时间设定：
本软件可以获取文件的最后修改、访问时间
可以保留一定时间内修改/访问过的文件
例如若将过期时间设为"48"，判定方式设为"以最后修改时间为依据"
则运行日期前两天内修改过的文件不会被删除
如果不想用此方法，则过期时间设为"0"即可

#### 移动文件流程图：
![流程图](https://user-images.githubusercontent.com/120773486/212371363-01cd7daf-1114-4c2c-bd11-bbe22e9d2783.png)


## Syncfile
这是一个用来同步文件两个路径下文件的程序，
也可以将U盘数据与电脑同步
![保存文件2](https://user-images.githubusercontent.com/120773486/215319432-ff60f693-52c2-4e76-993f-d6bbb4fa4218.png)

### 功能概述
可以将两个文件夹中的文件进行比较，找到相同的文件，保留最新版，
然后将对方没有的文件复制给对方，来实现同步的功能

#### 包括功能：
```
可移动磁盘与本地磁盘 与 本地磁盘间同步 两种模式选择
选择单向与双向同步模式
保留最新更改文件
开机自动运行存档
自动检测选定的可移动磁盘接入并自动同步
锁定文件/文件夹功能
```
### 功能详解

#### 可移动磁盘模式与本地磁盘间模式选择：
如果选择可移动磁盘模式并保存配置，可以选择一个已经接入的可移动磁盘，与一个本地位置同步

此外，如果软件处于打开状态，每次接入配置中记录的可移动磁盘时，会自动跳出提示框，可选直接开始按设置同步。
判断接入的磁盘是否为配置中保存的磁盘的方式为比较卷序列号。

如果选择本地磁盘间同步，则可以选择两个本地磁盘进行同步

#### 锁定文件夹/文件功能：

##### 锁定文件夹：
当你添加了一个文件夹，这个文件夹将会被显示在待选列表中。

在待选列表内勾选这个文件夹，这个文件夹内的内容将不会被修改或删除。

##### 锁定文件：
添加原理与锁定文件夹相同，如果勾选一个文件，那么这个文件不会被修改。

## 特别鸣谢
本程序中的多选下拉列表框组件代码改编自CSDN博主【只为你开心】的【Python tkinter自定义多选下拉列表框(带滚动条、全选)】，微调数据并添加了改变选择框高度的功能

（ https://blog.csdn.net/weixin_45774074/article/details/123293411 ）

# Update log - 更新日志
```
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
```