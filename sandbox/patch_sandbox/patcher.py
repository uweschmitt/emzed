

import module
from patch_decorator import patch

def do_patch():


    @patch(module.sum, module)
    def f_new(f_old, x,y):
        return f_old(x,y+1)

    @patch(module.Test.mult)
    def f_new(f_old, self,  x, y):
        return f_old(self, x,y)+1
