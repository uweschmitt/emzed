from version import version
import zipfile
import os
import fnmatch


files="""
    emzed.ico
    ms libms batches/ startup/ patched_modules/ emzed.pyw
    emzedPatches.py tab.py db.py elements.py abundance.py
    config_logger.py configs.py convert_universals.py example_scripts/
    installConstants.py mass.py splash.png  userConfig.py
    tables spyderlib/ """.split()


def split(path):
    drive, path = os.path.splitdrive(path)
    parts = []
    while path and path != os.path.sep:
        path, basename = os.path.split(path)
        parts.insert(0, basename)

    if drive:
        parts.insert(0, drive)
    return parts

def buildZipFile(zip_name, files, exclude=[], relocate_path=".", prefixpath="."):

    zf = zipfile.ZipFile(zip_name, "w")

    relocate_path = os.path.abspath(relocate_path)
    nparts = len(split(relocate_path))

    print
    print "BUILD", zip_name

    for p in files:
        p = p.strip()
        print "    ADD", p
        full_path = os.path.join(relocate_path, p)
        assert os.path.exists(full_path), "%s does not exist" % full_path
        if os.path.isfile(full_path):
            zf.write(full_path, os.path.join(prefixpath, p))
        else:
            for dirname, _, filenames in os.walk(full_path):
                parts = split(dirname)[nparts:]
                if any(fnmatch.fnmatch(p, ex) for p in parts for ex in exclude):
                    continue
                for f in filenames:
                    if exclude is not None:
                        if any(fnmatch.fnmatch(f, ex) for ex in exclude):
                            continue

                    target_path = os.path.join(*parts)
                    file_path = os.path.join(dirname, f)
                    zip_path = os.path.join(prefixpath, os.path.join(target_path, f))

                    #print file_path, zip_path
                    zf.write(file_path, zip_path)

    zf.close()


# todo: relocate_path mit files verwurschteldn ?
buildZipFile("installer_files/emzed_files.zip", files, exclude = [".*", "*.pyc"])

emzedzip = "emzed_%s.zip" % version
try:
    os.remove(emzedzip)
except:
    pass

buildZipFile(emzedzip, ["README", "installer.py", "install.bat", "License.txt", "emzed_files.zip"], prefixpath="emzed_1.0.1", relocate_path="installer_files")

os.remove("installer_files/emzed_files.zip")

