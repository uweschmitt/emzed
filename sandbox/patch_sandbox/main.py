import module
print "3+4 was ", module.sum(3,4)
print "3*4 was ", module.Test().mult(3,4)


import patcher
patcher.do_patch()

print "3+4 is ", module.sum(3,4)
print "3*4 is ", module.Test().mult(3,4)
