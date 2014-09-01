# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\cil.ui'
#
# Created: Mon Sep 01 09:57:46 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_CilWindow(object):
    def setupUi(self, CilWindow):
        CilWindow.setObjectName(_fromUtf8("CilWindow"))
        CilWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(CilWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.ilTextBrowser = QtGui.QTextBrowser(self.centralwidget)
        self.ilTextBrowser.setReadOnly(False)
        self.ilTextBrowser.setOpenLinks(False)
        self.ilTextBrowser.setObjectName(_fromUtf8("ilTextBrowser"))
        self.gridLayout.addWidget(self.ilTextBrowser, 0, 0, 1, 1)
        CilWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(CilWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        CilWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(CilWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        CilWindow.setStatusBar(self.statusbar)

        self.retranslateUi(CilWindow)
        QtCore.QMetaObject.connectSlotsByName(CilWindow)

    def retranslateUi(self, CilWindow):
        CilWindow.setWindowTitle(_translate("CilWindow", "Cil", None))

