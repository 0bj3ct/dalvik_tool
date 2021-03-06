# -*- coding: utf-8 -*-
#file: ecmd.py
#author: skeu
#description: xmono客户端主程序

from PyQt4 import QtCore, QtGui
import xmonoUI
import cil, stack_trace
import stack_trace
import TraceReader
import JdwpHandle
import os
import re
from JdwpNet import *
from JdwpHandle import *
from xres import *

#log辅助类
class Log(object):
    """log辅助类"""
    def regHandle(self, end):
        """end为输出到后端的接口函数,其参数为:
            msg   : str log内容
            level : int log的等级"""
        self._handle = end

    def _log(self, msg, level):
        """level WARNING INFO DEBUG ERROR"""
        self._handle(msg, level)

    def w(self, msg):
        """log中的warring接口
            msg: str, 需要打印到log的字符串"""
        self._log(msg, 'WARNING')

    def i(self, msg):
        """log中的info接口
            msg: str, 需要打印到log的字符串"""
        self._log(msg, 'INFO')

    def d(self, msg):
        """log中的debug接口
            msg: str, 需要打印到log的字符串"""
        self._log(msg, 'DEBUG')

    def e(self, msg):
        """log中的error接口
            msg: str, 需要打印到log的字符串"""
        self._log(msg, 'ERROR')

class XMonoWindow(QtGui.QMainWindow):
    """xmono主类"""

    #声明信号槽
    cilDisasmed = QtCore.pyqtSignal(str,QtCore.QByteArray)
    onTraceRecv = QtCore.pyqtSignal(object)
    onStacktraceRecv = QtCore.pyqtSignal(object,long)

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = xmonoUI.Ui_MainWindow()
        self.ui.setupUi(self)
        self.cilWindow = cil.CilWindow(self)
        self.stackTraceWindow = stack_trace.StackTraceWindow(self)
        self.log = Log()
        self.log.regHandle(self._print2Log)
        #self._ecmd = ecmd.Ecmd(self)
        self.sess = None
        self.pid = 7295
        self.dex = None
        self._createActions()
        self._createMenus()
        self._createToolBar()
        self._slotConnects()
        self._WinInit()
        #self._jdwpInit()
        self._initVariate()

    def _initVariate(self):
        """初始化一些要用到功能性全局变量, 放到这里是为了让__init__看起来舒服点"""
        self._traceFuncCntDict = {}

    def _createActions(self):
        icon = QtGui.QIcon(":/icons/res/icons/connect.png")
        self.connectAct = QtGui.QAction(icon, u"连接", self)

        icon = QtGui.QIcon(":/icons/res/icons/play.png")
        self.startTraceAct = QtGui.QAction(icon, u"开始记录", self)

        icon = QtGui.QIcon(":/icons/res/icons/stop.png")
        self.stopTraceAct = QtGui.QAction(icon, u"停止记录", self)

        icon = QtGui.QIcon(":/icons/res/icons/trace_win.png")
        self.showStackWinAct =  QtGui.QAction(icon, u"显示堆栈回溯窗口", self)

        self.stackTraceAct = QtGui.QAction(u"堆栈跟踪", self)

    def _createMenus(self):
        menuBar = self.menuBar()

        connectMenu = menuBar.addMenu(u"连接")
        connectMenu.addAction(self.connectAct)

        traceMenu = menuBar.addMenu(u"记录")
        traceMenu.addAction(self.startTraceAct)
        traceMenu.addAction(self.stopTraceAct)

        subwinMenu = menuBar.addMenu(u"窗口")
        subwinMenu.addAction(self.showStackWinAct)

        #这里创建func list窗口的右键菜单, 如果代码增长, 考虑移出到单独函数
        self.flRMenu = QtGui.QMenu(self.ui.funcCntTableWidget)
        self.flRMenu.addAction(self.stackTraceAct)
        self.ui.funcCntTableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def _createToolBar(self):
        connectToolBar = self.addToolBar(u"Connect")
        connectToolBar.addAction(self.connectAct)

        traceToolBar = self.addToolBar(u"Trace")
        traceToolBar.addAction(self.startTraceAct)
        traceToolBar.addAction(self.stopTraceAct)

        subwinToolBar = self.addToolBar(u"Windows")
        subwinToolBar.addAction(self.showStackWinAct)

    def _WinInit(self):
        """初始化界面, 当连接断开时会被调用"""
        self.connectAct.setEnabled(True)
        self.startTraceAct.setEnabled(False)
        self.stopTraceAct.setEnabled(False)
        self.cilWindow.WinInit()
        self.stackTraceWindow.WinInit()

    def _slotConnects(self):
        _actTriggered = lambda act,slot:self.connect(act, QtCore.SIGNAL("triggered()"), slot)
        _actTriggered(self.connectAct, self._connect)
        _actTriggered(self.startTraceAct, self._startTrace)
        _actTriggered(self.stopTraceAct, self._stopTrace)
        _actTriggered(self.stackTraceAct, self._stackTraceMethod)
        _actTriggered(self.showStackWinAct, self.stackTraceWindow.show)


        self.onTraceRecv.connect(self._recvFuncTrace)
        self.onStacktraceRecv.connect(self._recvStackTrace)
        self.ui.funcCntTableWidget.customContextMenuRequested.connect(self._showFuncCntRMenu)
        self.ui.filterLineEdit.returnPressed.connect(self._filterOutRequest)
        self.ui.funcCntTableWidget.itemDoubleClicked.connect(self._funcDoubleClicked)
        self.cilDisasmed.connect(self.cilWindow.showCil)
        self.stackTraceWindow.deleteMethod.connect(self._untraceMethod)
        self.stackTraceWindow.selectMethod.connect(self._disasmMethod)
        self.ui.cmdLineEdit.returnPressed.connect(self._cmdHandle)

        '''self.ui.tabWidget.currentChanged.connect(self._traceCntShow)
        self.cilWindow.compiled.connect(self._replaceMethod)'''

    def _connect(self):
        self._jdwpInit()

    def _showFuncCntRMenu(self, pos):
        p = self.ui.funcCntTableWidget.mapToGlobal(pos)
        self.flRMenu.exec_(p)

    def _jdwpInit(self):
        erro = False
        '''try:
            self.sess = Session(19530,None)
        except HandshakeError:
            erro = True
            self._ecmdErr(u"进程出错")
        except:
            erro = True
            self._ecmdErr(u"adb 运行失败")
        if erro: return False'''

        #self.sess = Session(self.pid,None)

        #for ligang
        self.sess = Session(None, None)
        self._ecmdConnected()
        self.sess.initCb()
        self.vm = DalvkVm(self.sess)
        self.connectAct.setEnabled(False)
        return True

    def _ecmdConnected(self):
        self.log.i(u"连接建立")
        self.startTraceAct.setEnabled(True)

    def _ecmdErr(self, err):
        self.log.e(u"连接错误 : {0}".format(err))
        self._WinInit()

    def _cmdHandle(self):
        t = self.ui.cmdLineEdit.text()
        self.ui.cmdText.append(t)
        self.ui.cmdLineEdit.clear()
        cmds = str(t)
        #do thing
        args = cmds.split(' ')
        if cmp(args[0],'inject') == 0:
            self.pid = int(args[1])
            tmp = open('inject','r+')
            txt = open('inject.txt','w+')
            lines = tmp.readlines()
            for line in lines:
                newline = line.replace(r'%pid',args[1])
                txt.writelines(newline)
            txt.close()
            tmp.close()
            os.system('inject.bat')
        elif cmp(args[0],'dex') == 0:
            self.dex = args[1]


    def _startTrace(self):
        self._traceFuncCntDict.clear()
        self._clearFuncCntTableWidget()
        self.ui.funcGroupBox.setTitle (u"正在跟踪...")
        self.startTraceAct.setEnabled(False)
        self.stopTraceAct.setEnabled(True)
        self.vm.start_trace()

    def _stopTrace(self):
        self.startTraceAct.setEnabled(True)
        self.stopTraceAct.setEnabled(False)
        self.vm.end_trace(self.recvFuncTraceWraper)
        self.ui.funcGroupBox.setTitle (u"暂无跟踪结果...")

    def _traceLogFilterOut(self, data):
        flr = str(self.ui.filterLineEdit.text())
        if flr == "":
            return data
        pattern = re.compile(flr, re.I)
        return [i for i in data if re.search(pattern, i) != None]

    def _filterOutRequest(self):
        self._funcTraceCntFilteShow()

    def _funcTraceCntFilteShow(self):
        d = {}
        namelist = []
        b = self._traceFuncCntDict
        for key in self._traceFuncCntDict.keys():
            namelist.append(key)
        f_k = self._traceLogFilterOut(namelist)
        for k in f_k:
            d[k] = self._traceFuncCntDict[k]
        self._traceCntShow(d)

    def _tabChange(self, index):
        if index == 0: #cnt
            self._funcTraceCntFilteShow()

    def _clearFuncCntTableWidget(self):
        w = self.ui.funcCntTableWidget
        w.clear()
        while w.rowCount() != 0:
            w.removeRow(0)
        w.horizontalHeader().hide()

    def _traceCntShow(self, d):
        self._clearFuncCntTableWidget()
        w = self.ui.funcCntTableWidget
        w.setColumnCount(3)
        labels = QtCore.QStringList()
        labels.append("")
        labels.append("function")
        labels.append("count")
        w.setHorizontalHeaderLabels(labels)
        w.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        w.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        w.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        w.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        w.horizontalHeader().show()
        w.verticalHeader().hide()
        for k in d.keys():
            row = w.rowCount()
            w.insertRow(row)
            #设置序数
            v = QtGui.QTableWidgetItem()
            v.setData(0, d[k][1])
            w.setItem(row, 0, v)
            #设置函数名
            w.setItem(row, 1, QtGui.QTableWidgetItem(k))
            #设置调用次数
            v = QtGui.QTableWidgetItem()
            v.setData(0, d[k][0])  #这里用setData是为了方便排序
            w.setItem(row, 2, v)
        w.sortItems(0, QtCore.Qt.AscendingOrder)

    def _traceCntHandle(self, reader):
        sort = 1
        for m in reader.callInfo:
            if m["method_action"]:
                try:
                    method_info = reader.funcData[m["method_id"]]
                except:
                    print m["method_id"]
                    continue
                funcName = method_info["method_name"]
                className = method_info["class_name"]
                jniName = method_info["jni"]
                parfunc = funcName+TraceReader.jniparse(jniName)
                fullFuncName = '@'.join([className,parfunc])

                if fullFuncName in self._traceFuncCntDict.keys():
                    data = self._traceFuncCntDict[fullFuncName]
                    callCnt = data[0]
                    callCnt += 1
                    self._traceFuncCntDict[fullFuncName] = (callCnt,data[1],data[2])
                else:
                    self._traceFuncCntDict[fullFuncName] = (1, sort,m["method_id"])
                    sort += 1
        self._funcTraceCntFilteShow()

    def recvFuncTraceWraper(self, reader):
        #print "enter recvFuncTraceWraper"
        self.onTraceRecv.emit(reader)
    def _recvFuncTrace(self, reader):
        self.log.d(u"recv func trace data : {0}".format(123))
        self._traceCntHandle(reader)
        self.ui.funcGroupBox.setTitle (u"函数 : {0}".format(len(self._traceFuncCntDict)))

    def _funcDoubleClicked(self, item):
        if item.column() != 0:
            item = self.ui.funcCntTableWidget.item(item.row(), 1)
        s = item.text()
        self._disasmMethod(str(s))

    def _disasmMethod(self, s):
        s = str(s)
        d = self._traceFuncCntDict
        vm = self.vm
        ctxt = self.sess.ctxt
        namelist = s.split('@')
        funcNameWithPar = namelist[1]
        clsName = namelist[0]
        nPos = funcNameWithPar.index('(')
        funcName = funcNameWithPar[:nPos]
        mId = d[s][2]
        clsName = "L"+clsName+";"
        clsObj = vm.getClass(clsName)
        mObj = ctxt.objpool(MethodContext,clsObj.rtId,mId,self.sess)
        print mObj;
        print "%s mId:%x" %(funcName,mId)
        codelen,code = mObj.getBytecodes()
        self.cilDisasmed.emit(s,code)


    def _replaceMethod(self, iname, token, t):
        code = t[0]
        ex = t[1]
        req = xmono_pb2.ReplaceMethodReq()
        req.domain_id = 0
        req.image_name = str(iname)
        req.method_token = token
        req.new_code = code
        if (len(ex.keys()) > 0):
            keys = ex.keys()
            keys.sort()
            for k in keys:
                e = req.ex.add()
                e.index = k
                e.try_offset = ex[k].try_offset
                e.try_len = ex[k].try_len
                e.handler_offset = ex[k].handler_offset
                e.handler_len = ex[k].handler_len
        pkg = ecmd.EcmdPacket(XMONO_ID_REPLACE_METHOD_REP, req.SerializeToString())
        self._ecmd.sendPacket(pkg)
        self.log.d(u"_replaceMethod over")

    def _listDomain(self):
        pkg = ecmd.EcmdPacket(XMONO_ID_LIST_DOMAIN_REP, "")
        self._ecmd.sendPacket(pkg)

    def _getFuncCntItemStr(self):
        item = self.ui.funcCntTableWidget.currentItem()
        if item == None:
            return
        if item.column() != 0:
            item = self.ui.funcCntTableWidget.item(item.row(), 1)
        return str(item.text())

    def _untraceMethod(self, s):
        self._traceMethod(s, False)
    def _traceMethod(self, s, sw):
        s = str(s)
        d = self._traceFuncCntDict
        ctxt = self.sess.ctxt
        namelist = s.split('@')
        funcNameWithPar = namelist[1]
        clsName = namelist[0]
        mId = d[s][2]
        clsName = "L"+clsName+";"
        clsObj = self.vm.getClass(clsName)
        methObj = ctxt.objpool(MethodContext,clsObj.rtId,mId,self.sess)
        if sw:
            methObj.setbreak(0,self._recvStackTraceWraper,s)
        else:
            methObj.unsetbreak(s)


    def _stackTraceMethod(self):
        s = self._getFuncCntItemStr()
        self._traceMethod(s, True)
        self.stackTraceWindow.addMethod(s)

    def _recvReplaceMethodRsp(self, packet):
        rsp = xmono_pb2.ReplaceMethodRsp()
        rsp.ParseFromString(packet.data)
        if rsp.err:
            self.log.i(u"{0}".format(rsp.msg))
        else:
            self.log.e(u"{0}".format(rsp.msg))
        return

    def _recvListDomain(self, packet):
        rsp = xmono_pb2.ListDomainRsp()
        rsp.ParseFromString (packet.data)
        self.log.i(u"Domain List :")
        for i in rsp.id:
            self.log.i(u"\t{0}".format(i))

    def _recvStackTraceWraper(self,bpInfo,tid):
        self.onStacktraceRecv.emit(bpInfo,tid)

    def _recvStackTrace(self, bpInfo, tid):
        ctxt = self.sess.ctxt
        l = []
        tcObj  = ctxt.objpool(ThreadContext,tid,self.sess)
        framList = tcObj.frams()
        bGetvaule = True
        for  fram in framList:
            fId = fram[0]
            loc = fram[1]
            args = []
            clsObj = ctxt.objpool(ClassType,loc.rtId,self.sess)
            clsName = clsObj.name
            funcName = clsObj.getMethodName(loc.mId)
            methObj = ctxt.objpool(MethodContext,loc.rtId,loc.mId,self.sess)
            parfunc = funcName[0]+TraceReader.jniparse(funcName[1])
            funcFullName = '@'.join([clsName,parfunc])
            if cmp(funcFullName,"com/android/internal/os/ZygoteInit$MethodAndArgsCaller@run()") == 0:
                bGetvaule = False
            if bGetvaule:
                framObj = ctxt.objpool(FrameInfo,fId,loc,tid,self.sess)
                args = framObj.GetValues()
            l.append((funcFullName,loc.idx,args))
        tcObj.resume()
        self.stackTraceWindow.addTraceResult(l)

    def _print2Log(self, msg, level):
        """level WARNING INFO DEBUG ERROR"""
        title = {'ERROR':'<font color="#FF2D2D">','DEBUG':'<font color="#2828FF">',
                 'WARNING':'<font color="#D200D2">', 'INFO':'<font>',}
        if level not in title.keys(): return
        self.ui.logTextBrowser.append("%s[+]%s</font>" % (title[level], msg.replace('\n', '<br/>')))
