import os
import re
import shutil
from pathlib import Path

from github_release_downloader import GitHubRepo, check_and_download_updates, get_latest_version
from LT_Dic import version
from mf_const import CACHE_PATH, CACHE_TEMP_PATH, MF_TEMP_PATH
from semantic_version import Version


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
