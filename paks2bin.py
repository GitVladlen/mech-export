import os
import sys
import subprocess

import settings


def main():
    ScriptPackagePath = settings.EXPORT_PATH + settings.SCRIPT_PAKCAGE_NAME
    LocalePackagePaht = settings.EXPORT_PATH + settings.LOCALE_PACKAGE_NAME

    make_bin_from_xml(ScriptPackagePath)
    del_xml(ScriptPackagePath)

    make_bin_from_xml(LocalePackagePaht)
    del_xml(LocalePackagePaht)
    pass

# ------------------------------------------------------------
def make_bin_from_xml(package_path):
    InFilePath = package_path + "/Pak.xml"
    OutFilePath = package_path + "/Pak.bin"

    if os.path.exists(InFilePath) is False:
        print ("!ERROR! Pak.xml not exits by path {path}".format(
            path = InFilePath))
        sys.exit(-1)

    metawrite_cmd = "{Metawrite} --protocol {Protocol} --in {In} --out {Out}".format(
        Metawrite = settings.METAWRITE_EXE_PATH,
        Protocol = settings.METAWRITE_PROTOCOL_PATH,
        In = InFilePath,
        Out = OutFilePath)
    call_and_wait(metawrite_cmd)
    pass

def del_xml(package_path):
    InFilePath = package_path + "/Pak.xml"

    if os.path.exists(InFilePath) is False:
        print ("!ERROR! Pak.xml not exits by path {path}".format(
            path = InFilePath))
        sys.exit(-1)

    os.remove(InFilePath)
    pass

def call_and_wait(cmd):
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()
    pass
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
    pass
# ------------------------------------------------------------