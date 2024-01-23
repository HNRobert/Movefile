import os
from mf_const import (CF_CONFIG_PATH, DESKTOP_PATH, MF_CONFIG_PATH,
                      MF_ICON_PATH, MF_LOG_PATH, SF_CONFIG_PATH)
dest_path = 'C://ProgramData'
print(os.path.splitdrive(dest_path))
