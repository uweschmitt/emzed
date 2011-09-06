from package import module

import sys


sys.modules["package.modules"] = __import__("patched")

import run

