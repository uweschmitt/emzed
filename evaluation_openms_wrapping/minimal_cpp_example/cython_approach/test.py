
import wrap

c = wrap.PyContainer()
print len(c)

wrap.fill(1000, c)
print len(c)
print c.getFront().getD()
print c.getBack().getD()

items =  c.getItems()
print type(items)
print type(items[0])
print items[0].getD()
print items[-1].getD()

i = wrap.PyItem()
i.setD("dtest")
print i.getD()

