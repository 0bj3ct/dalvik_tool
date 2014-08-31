# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\xmono.ui'
#
# Created: Sun Aug 31 14:18:30 2014
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Consolas"))
        MainWindow.setFont(font)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.filterLineEdit = QtGui.QLineEdit(self.centralwidget)
        self.filterLineEdit.setText(_fromUtf8(""))
        self.filterLineEdit.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.filterLineEdit.setObjectName(_fromUtf8("filterLineEdit"))
        self.horizontalLayout.addWidget(self.filterLineEdit)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.funcGroupBox = QtGui.QGroupBox(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.funcGroupBox.sizePolicy().hasHeightForWidth())
        self.funcGroupBox.setSizePolicy(sizePolicy)
        self.funcGroupBox.setObjectName(_fromUtf8("funcGroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.funcGroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(self.funcGroupBox)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.count = QtGui.QWidget()
        self.count.setObjectName(_fromUtf8("count"))
        self.gridLayout_5 = QtGui.QGridLayout(self.count)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.funcCntTableWidget = QtGui.QTableWidget(self.count)
        self.funcCntTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.funcCntTableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.funcCntTableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.funcCntTableWidget.setGridStyle(QtCore.Qt.DashLine)
        self.funcCntTableWidget.setObjectName(_fromUtf8("funcCntTableWidget"))
        self.funcCntTableWidget.setColumnCount(0)
        self.funcCntTableWidget.setRowCount(0)
        self.funcCntTableWidget.verticalHeader().setVisible(False)
        self.gridLayout_5.addWidget(self.funcCntTableWidget, 0, 0, 1, 1)
        self.tabWidget.addTab(self.count, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.statTabWidget = QtGui.QTabWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.statTabWidget.sizePolicy().hasHeightForWidth())
        self.statTabWidget.setSizePolicy(sizePolicy)
        self.statTabWidget.setObjectName(_fromUtf8("statTabWidget"))
        self.logTab = QtGui.QWidget()
        self.logTab.setObjectName(_fromUtf8("logTab"))
        self.gridLayout_3 = QtGui.QGridLayout(self.logTab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.logTextBrowser = QtGui.QTextBrowser(self.logTab)
        self.logTextBrowser.setReadOnly(True)
        self.logTextBrowser.setObjectName(_fromUtf8("logTextBrowser"))
        self.gridLayout_3.addWidget(self.logTextBrowser, 0, 0, 1, 1)
        self.statTabWidget.addTab(self.logTab, _fromUtf8(""))
        self.statTab = QtGui.QWidget()
        self.statTab.setObjectName(_fromUtf8("statTab"))
        self.gridLayout_4 = QtGui.QGridLayout(self.statTab)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.cmdText = QtGui.QTextBrowser(self.statTab)
        self.cmdText.setObjectName(_fromUtf8("cmdText"))
        self.gridLayout_4.addWidget(self.cmdText, 0, 0, 1, 1)
        self.cmdLineEdit = QtGui.QLineEdit(self.statTab)
        self.cmdLineEdit.setObjectName(_fromUtf8("cmdLineEdit"))
        self.gridLayout_4.addWidget(self.cmdLineEdit, 1, 0, 1, 1)
        self.statTabWidget.addTab(self.statTab, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.splitter, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.statTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MonoHack", None))
        self.label.setText(_translate("MainWindow", "过滤器", None))
        self.funcGroupBox.setTitle(_translate("MainWindow", "函数 : 0", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.count), _translate("MainWindow", "计数", None))
        self.statTabWidget.setTabText(self.statTabWidget.indexOf(self.logTab), _translate("MainWindow", "日志", None))
        self.statTabWidget.setTabText(self.statTabWidget.indexOf(self.statTab), _translate("MainWindow", "统计", None))

