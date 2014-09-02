# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\stack_trace.ui'
#
# Created: Tue Sep 02 21:32:18 2014
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

class Ui_stackTraceForm(object):
    def setupUi(self, stackTraceForm):
        stackTraceForm.setObjectName(_fromUtf8("stackTraceForm"))
        stackTraceForm.resize(762, 422)
        self.centralwidget = QtGui.QWidget(stackTraceForm)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.groupBox = QtGui.QGroupBox(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.stackTraceTreeWidget = QtGui.QTreeWidget(self.groupBox)
        self.stackTraceTreeWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.stackTraceTreeWidget.setColumnCount(0)
        self.stackTraceTreeWidget.setObjectName(_fromUtf8("stackTraceTreeWidget"))
        self.gridLayout.addWidget(self.stackTraceTreeWidget, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.splitter)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.stackTraceListWidget = QtGui.QListWidget(self.groupBox_2)
        self.stackTraceListWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.stackTraceListWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.stackTraceListWidget.setObjectName(_fromUtf8("stackTraceListWidget"))
        self.gridLayout_2.addWidget(self.stackTraceListWidget, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)
        stackTraceForm.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(stackTraceForm)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 762, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        stackTraceForm.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(stackTraceForm)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        stackTraceForm.setStatusBar(self.statusbar)

        self.retranslateUi(stackTraceForm)
        QtCore.QMetaObject.connectSlotsByName(stackTraceForm)

    def retranslateUi(self, stackTraceForm):
        stackTraceForm.setWindowTitle(_translate("stackTraceForm", "堆栈回溯", None))
        self.groupBox.setTitle(_translate("stackTraceForm", "回溯结果", None))
        self.groupBox_2.setTitle(_translate("stackTraceForm", "监控函数列表", None))

