import zipfile
import os
import fnmatch


files="""
    ms libms batches/ startup/ patched_modules/ msWorkbench.py
    msWorkbenchPatches.py tab.py db.py elements.py abundance.py
    config_logger.py configs.py convert_universals.py example_scripts/
    installConstants.py mass.py msWorkbench.bat splash.png  userConfig.py
    spyderlib/ """.split()


def split(path):
    drive, path = os.path.splitdrive(path)
    parts = []
    while path and path != os.path.sep:
        path, basename = os.path.split(path)
        parts.insert(0, basename)

    if drive:
        parts.insert(0, drive)
    return parts

def buildZipFile(zip_name, files, exclude=[], relocate_path="."):

    zf = zipfile.ZipFile(zip_name, "w")

    relocate_path = os.path.abspath(relocate_path)
    nparts = len(split(relocate_path))

    for p in files:
        p = p.strip()
        print "add", p
        for dirname, _, filenames in os.walk(os.path.join(relocate_path, p)):
            parts = split(dirname)[nparts:]
            if any(fnmatch.fnmatch(p, ex) for p in parts for ex in exclude):
                continue
            for f in filenames:
                if exclude is not None:
                    if any(fnmatch.fnmatch(f, ex) for ex in exclude):
                        continue


                target_path = os.path.join(*parts)
                zf.write(os.path.join(dirname, f), os.path.join(target_path, f))
        break

    zf.close()


# todo: relocate_path mit files verwurschteldn ?
buildZipFile("emzed.zip", files, exclude = [".*", "*.pyc"], relocate_path="..")
