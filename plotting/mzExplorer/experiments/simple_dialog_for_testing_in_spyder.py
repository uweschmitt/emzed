# -*- coding: utf-8 -*-
"""
Created on Tue Aug 09 10:32:46 2011

@author: Administrator
"""

from PyQt4.QtGui import QMainWindow, QDialog
import guidata

win = QDialog()
win.show()

app = guidata.qapplication()
app.exec_()