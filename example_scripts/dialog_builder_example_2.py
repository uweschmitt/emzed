
import sys
sys.path.insert(0, "..")
sys.path.insert(0, ".")
import ms
b = ms.DialogBuilder()
b.addInt("hi", colspan=2)
b.addInt("hi2")
b.addInt("hi3", col=1)
values = "1 2 3 4 5 6 7 8 9 10 11 12".split()
b.addMultipleChoice("a", values, horizontal=3)
b.addMultipleChoice("b", values, vertical=3)
b.show()
