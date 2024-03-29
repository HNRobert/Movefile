import os
import winreg

WIN_SHELL_KEY = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
ROAMING_PATH = os.path.join(winreg.QueryValueEx(WIN_SHELL_KEY, 'AppData')[0])
MF_DATA_PATH = os.path.join(ROAMING_PATH, r'Movefile')
MF_CONFIG_PATH = os.path.join(MF_DATA_PATH, r'Movefile_data.ini')
MF_TEMP_PATH = os.path.join(MF_DATA_PATH, r'temp')
CACHE_NAME = r'repo-HNRobert-Movefile.cache'
CACHE_PATH = '.\\' + CACHE_NAME
CACHE_TEMP_PATH = os.path.join(MF_TEMP_PATH, CACHE_NAME)
MF_ICON_PATH = os.path.join(MF_DATA_PATH, r'Movefile.ico')
MF_LOG_PATH = os.path.join(MF_DATA_PATH, r'Movefile.log')
CF_DATA_PATH = os.path.join(MF_DATA_PATH, r'Cleanfile')
CF_CONFIG_PATH = os.path.join(CF_DATA_PATH, r'Cleanfile_data.ini')
SF_DATA_PATH = os.path.join(MF_DATA_PATH, r'Syncfile')
SF_CONFIG_PATH = os.path.join(SF_DATA_PATH, r'Syncfile_data.ini')
DESKTOP_PATH = winreg.QueryValueEx(WIN_SHELL_KEY, "Desktop")[0]
STARTUP_PATH = os.path.join(
    ROAMING_PATH, r"Microsoft\Windows\Start Menu\Programs\StartUp")
START_MENU_PATH = os.path.join(
    ROAMING_PATH, r"Microsoft\Windows\Start Menu\Programs")
