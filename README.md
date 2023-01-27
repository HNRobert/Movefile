# Movefile
这是一个用于整理文件的程序，包括了 Cleanfile 和 Syncfile 两个主要功能

文件夹中exe文件是已经打包好的程序，可以直接在电脑任意位置使用；
pyw文件是代码源文件，py文件是图标的Base64编码，ico文件是图标文件，供打包时使用，ComBoPicker.py 是多选下拉列表框模块；

exe文件只提供发行版发布的打包的文件，若代码的语义未改变则不会提供最新的打包文件；
Beta 版程序也不会打包。

如果使用过程中对本软件功能有任何疑惑，可以查看菜单栏中的 "帮助" 选项

由于功能比较多，代码比较冗长（主程序1450行，自建模块200+行），如果对代码结构有什么改进意见，可以联系作者，新版本中会进行更改哦~

使用前请务必阅读下面的使用注意事项

### 兼容性说明：
代码中的exe文件仅支持windows64位操作系统，Win10效果最佳

如果操作系统是32位Windows，可以下载pyw文件，解码base64编码过的图标文件，然后自行打包为32位操作系统的exe文件

##### 本软件仅支持Windows操作系统下使用！

#### pyinstaller打包法：

先要安装python环境，python安装完后打开cmd安装pyinstaller (pip install pyinstaller)

如果想打包为32为的exe，那就要在32位的Python下打包

安装完成后，现将【Movefile vX.X.X.pyw】改名为【Movefile.pyw】，接着在文件夹内放入ico文件与其他配置文件，然后在【Movefile vX.X.X.pyw】所在文件夹的索引框内输入【cmd】，然后在弹出的命令提示框内输入【pyinstaller -i Movefile.ico -noupx Movefile.pyw --onefile】，就可以在产出的【dist】文件夹内得到打包好的exe文件。

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

### 功能概述：
本程序可将某个文件夹中一定时间未修改或者未访问，且满足其他一些设定要求的文件，转移到另一个文件夹，使你可以方便地整理文件

包含功能：选择原文件夹（默认桌面），选择放置文件的新文件夹，设置过期时间，设置过期时间判断依据（按最后修改/访问时间），选择是否移动文件夹（目前只支持整个文件夹移动），
选择保留文件（列出原文件夹内文件/文件夹），选择保留文件格式（扫描原文件夹内文件后缀后列出），开机自动启动

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

###功能概述：
可以将两个文件夹中的文件进行比较，找到相同的文件，保留最新版，
然后将对方没有的文件复制给对方，来实现同步的功能

包括功能：可移动磁盘与本地磁盘 与 本地磁盘间同步 两种模式选择，
选择单向与双向同步模式，保留最新更改文件，开机自动运行存档，
自动检测选定的可移动磁盘接入并自动同步

###功能详解
####可移动磁盘模式与本地磁盘间模式选择：
如果选择可移动磁盘模式并保存配置，可以选择一个已经接入的可移动磁盘，与一个本地位置同步

此外，如果软件处于打开状态，每次接入配置中记录的可移动磁盘时，会自动跳出提示框，可选直接开始按设置同步。
判断接入的磁盘是否为配置中保存的磁盘的方式为比较卷序列号。

如果选择本地磁盘间同步，则可以选择两个本地磁盘进行同步

# 特别鸣谢：
本程序中的多选下拉列表框的组件代码改编自CSDN博主【只为你开心】的【Python tkinter自定义多选下拉列表框(带滚动条、全选)】，微调数据并添加了改变选择框高度的功能

（ https://blog.csdn.net/weixin_45774074/article/details/123293411 ）
