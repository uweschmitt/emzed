cpdef paramFromFile(char *path):
    p = _Param()
    p.load(path)
    return p
