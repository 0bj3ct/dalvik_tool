# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from xmono import *
import sys

if __name__ == '__main__':
    if sys.argv[0] == '10086':
        app = QtGui.QApplication(sys.argv)
        #app.setWindowIcon(QtGui.QIcon("./res/q108.png")); 
        window = XMonoWindow()
        window.show()
        app.exec_()
    raise Exception('please input sn')
