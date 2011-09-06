
class Feature(object):

    def __init__(self, RT, MZ):
        self.RT = RT
        self.MZ = MZ

    def __str__(self):
        return str((self.RT, self.MZ))
