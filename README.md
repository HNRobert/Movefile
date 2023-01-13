# Movefile
这是一个用来整理文件夹（尤其是桌面）的程序
文件夹中exe文件是已经打包好的程序，可以直接在电脑任意位置使用；
pyw文件是代码源文件，还有一个是图标的Base64编码；

使用前请务必阅读下面的使用注意事项



# 功能概述：
本程序可将某个文件夹中一定时间未修改或者未访问，且满足其他一些设定要求的文件，转移到另一个文件夹，使你可以方便地整理文件

包含功能：选择原文件夹（默认桌面），选择放置文件的新文件夹，设置过期时间，设置过期时间判断依据（按最后修改/访问时间），选择是否移动文件夹（目前只支持整个文件夹移动），
选择保留文件（列出原文件夹内文件/文件夹），选择保留文件格式（扫描原文件夹内文件后缀后列出），开机自动启动

如果使用过程中对本软件功能有任何疑惑，可以查看菜单栏中的 "帮助" 选项

由于作者还是萌新，功能又比较多，代码就比较冗长（750行），如果对代码结构有什么改进意见，可以联系作者，新版本中会进行更改哦~

# pyw文件打包说明：
本项目开源，可以下载pyw文件与图表文件自行更改源代码

打包方法：

先要安装python环境，python安装完后

# 使用前特别注意事项：
1.本软件必须在64位操作系统下运行，
  后续如果需求增加，会推出32位操作系统版本
  也可以下载pyw文件，自己打包成32位的exe文件
  
*2.本exe文件的名称请不要改变："Movefile vX.X.X.exe"，否则会影响开机自启功能
  
*3.使用本软件前请打开Windows设置中的
  系统/通知和操作/通知/
  “获取来自应用和其他发送者的通知” 选项，
  否则会影响操作结果通知功能
  
*4.使用本软件前请先将本软件放入
  Windows安全中心的防病毒扫描排除项中，
  否则在运行时会被直接删除。
  这是因为本软件涉及更改开机启动项。
  如果本软件在使用中被意外删除，
  请在Windows安全中心中
  病毒威胁和防护的 "保护历史记录"
  或其他安全软件中找回本软件
  
5.如果经过版本新后软件无法运行，
  可以尝试删除位于Roaming文件夹中的配置文件
  
6.若有其他原因导致软件功能无法正常运行，
  且无法按上面的解释修复，
  请联系作者,我会尽快尝试帮你修复

# 保留项目/文件格式选择功能：

保留项目选择：
选中的项目不会被转移

保留文件格式选择：
某种格式类型的文件都不会被转移
比如选中'.lnk'，即表示原文件夹中所有的快捷方式不会被转移

# 过期时间设定：
本软件可以获取文件的最后修改、访问时间
可以保留一定时间内修改/访问过的文件
例如若将过期时间设为"48"，判定方式设为"以最后修改时间为依据"
则运行日期前两天内修改过的文件不会被删除
如果不想用此方法，则过期时间设为"0"即可

# 移动文件流程图：
如下：