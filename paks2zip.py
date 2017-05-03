import os
import zipfile
import shutil

import settings


def main():
    ScriptPakDirName = settings.EXPORT_PATH + settings.SCRIPT_PAKCAGE_NAME
    LocalePakDirName = settings.EXPORT_PATH + settings.LOCALE_PACKAGE_NAME

    if os.path.exists(ScriptPakDirName) is False:
        return

    if os.path.exists(LocalePakDirName) is False:
        return

    zip_dir(ScriptPakDirName)
    zip_dir(LocalePakDirName)
    pass

# ---------------------------------------------------------------------------
def zip_dir(source_dir):
    shutil.make_archive(
        source_dir, 
        'zip',           # the archive format - or tar, bztar, gztar 
        root_dir=source_dir,   # root for archive - current working dir if None
        base_dir=None)   # start archiving from here - cwd if None too

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
    pass
# ---------------------------------------------------------------------------