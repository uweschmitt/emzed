
import wrap

c = wrap.PyContainer()
print len(c)

wrap.fill(1000, c)
print len(c)

print c.getFront().getD()
