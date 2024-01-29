import os
import re
import shutil
from pathlib import Path

from github_release_downloader import GitHubRepo, check_and_download_updates, get_latest_version
from LT_Dic import version
from mf_const import CACHE_PATH, CACHE_TEMP_PATH, MF_TEMP_PATH
from semantic_version import Version

"""
def set_global_proxy(status='off'):
    '''
    全局性的关闭或者启用系统代理。
    测试时发现，如果设置了系统代理，在访问 https 网站时发生错误 requests.exceptions.ProxyError
    原因是 SSL: self._sslobj.do_handshake() -> OSError: [Errno 0] Error
    进一步，是因为 urllib3 1.26.0 以上版本支持 https协议，但是代理软件不支持，导致连接错误。
    所以使用 { 'https': 'http://127.0.0.1:1080' }，http的协议访问 https 的网址（本地通信），即可解决。
    或者在 requests.get 函数中增加 proxies={'https': None} 参数来解决，但每次访问都需加这个参数，太麻烦，
    此处通过修改 requests 库中的 get_environ_proxies 函数的方法来全局性地关闭系统代理，或者仅关闭 https 的代理。
    参数：
    status - 'off', 关闭系统代理；
    'on', 打开系统代理；
    'toggle', 切换关闭或者打开状态；
    注意：仅影响本 Python程序的 requests包，不影响其他 Python程序，
    不影响 Windows系统的代理设置，也不影响浏览器的代理设置。
    '''
    from requests import sessions, utils
    init_func = sessions.get_environ_proxies
    if status=='off':
    # 关闭系统代理
        if init_func.__name__ == '<lambda>':
            # 已经替换了原始函数，即已经是关闭状态，无需设置
            return
            # 修改函数，也可以是 lambda *x, **y: {'https': None}
        sessions.get_environ_proxies = lambda *x, **y: {}
    elif status=='on':
        # 打开系统代理，如果设置了代理的话
        # 对高版本的 urllib3(>1.26.0) 打补丁，修正 https代理 BUG: OSError: [Errno 0] Error
        proxies = utils.getproxies()
        if 'https' in proxies:
            proxies['https'] = proxies.get('http') # None 或者 'http://127.0.0.1:1080'
            sessions.get_environ_proxies = lambda *x, **y: proxies
            sessions.get_environ_proxies.__name__ = 'get_environ_proxies'
    else:
    # 切换开关状态
        if init_func.__name__ == '<lambda>':
        # 已经是关闭状态
            set_global_proxy('on')
        else:
        # 已经是打开状态
            set_global_proxy('off')
        return
"""

def is_mf_need_update():
    try:
        latest = get_latest_version(GitHubRepo("HNRobert", "Movefile"))
        if str(latest) > version[1:]:
            return True
        return False
    except Exception as e:
        print(e, 'Checking Error')
        return False


def has_new_mf_downloaded():

    def set_new_version(*content):
        nonlocal new_exe
        new_exe = content[0].name

    if os.path.exists(CACHE_TEMP_PATH):
        shutil.copy(CACHE_TEMP_PATH, CACHE_PATH)

    new_exe = ''
    try:
        check_and_download_updates(
            GitHubRepo("HNRobert", "Movefile"),  # Releases source
            # Download *Setup.exe only
            assets_mask=re.compile(".*\\Setup.exe"),
            current_version=Version(version[1:]),  # Current version
            downloads_dir=Path(MF_TEMP_PATH),  # Where to download
            download_callback=set_new_version,  # Callback function
        )
        if os.path.exists(CACHE_TEMP_PATH):
            os.remove(CACHE_TEMP_PATH)
        if new_exe and os.path.exists(CACHE_PATH):
            shutil.move(CACHE_PATH, MF_TEMP_PATH)
        return new_exe

    except Exception as e:
        print(e, 'Downloading Error')
        return ''


def main():
    has_new_mf_downloaded()


if __name__ == "__main__":
    main()
