# -*- coding: utf-8 -*-
#file: cil.py
#author: object
#description: cil显示,编辑,反编译，编译模块

from PyQt4 import QtCore, QtGui
import cilUI
import jpype
import re, struct
import decompli

class CilWindow(QtGui.QMainWindow):
    """cil主类"""
    compiledSig = QtCore.pyqtSignal(str, int, tuple, name = 'compiled')
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = cilUI.Ui_CilWindow()
        self.ui.setupUi(self)
        self._createActions()
        self._createMenus()
        self._slotConnects()
        #self._initJava()
    def _initJava(self, filePath):
        jvmPath = jpype.getDefaultJVMPath()
        ext_classpath = r"jadx-core-0.5.2.jar;android-4.3.jar;dx-1.8.jar;slf4j-api-1.7.7.jar"
        jvmArg = "-Djava.class.path=" + ext_classpath
        jpype.startJVM(jvmPath,"-ea",jvmArg)
        self.jadx = jpype.JPackage("jadx").api.JadxDecompiler()
        File = jpype.JClass('java.io.File')
        self.inFile =  File('F:\\classes.dex')
        self.jadx.loadFile(inFile)

    def _createActions(self):
        self.compileAct = QtGui.QAction(u"编译", self)
        self.sendAct = QtGui.QAction(u"发送到客户端", self)

    def _createMenus(self):
        menuBar = self.menuBar()

        funcMenu = menuBar.addMenu(u"函数")
        funcMenu.addAction(self.compileAct)
        funcMenu.addAction(self.sendAct)

    def _slotConnects(self):
        self.compileAct.triggered.connect(self._compile)

    def showCil(self, funcName, code):
        self.show()
        code = str(code)
        d = decompli.DexDecompiler()
        d.load_bytearray(code)
        bytecode = d.disassemble()
        self.ui.ilTextBrowser.clear()
        funcName = funcName+':'
        self.ui.ilTextBrowser.append(funcName)
        print bytecode
        print repr(code)
        for x in bytecode:
            line = 'line_'+str(x[0])+':    '+x[1]
            self.ui.ilTextBrowser.append(line)
    
    #显示反编译信息
    def showDecode(self,funcName):
        nameList = funcName.split('@')
        clsName = nameList[0]
        methName = nameList[1]
        clsName = clsNameFormart(clsName)
        print clsName
        clses = self.jadx.getClasses()
        for cls in clses:
            if cmp(clsName,'com.example.debugapp.MainActivity') == 0:
                print cls
    def clsNameFormart(clsName):
        name = clsName.replace('/','.')
        return name
    def WinInit(self):
        return

    def _compile(self):
        s = str(self.ui.ilTextBrowser.toPlainText())
        err, result = cil_compile(s)
        if err:
            print "编译成功!"
            msg_box = QtGui.QMessageBox()
            msg_box.setText(u"编译成功!")
            msg_box.exec_()
            self.compiledSig.emit(result[0], result[1], (result[2], result[3]))
        else:
            print "编译失败: {0}".format(result)
            msg_box = QtGui.QMessageBox()
            msg_box.setText(u"{0}".format(result.decode('utf-8')))
            msg_box.exec_()


class LineInfo(object):
    def __init__(self):
        self.labels = []
        self.opcode = None
        self.jmps = []

class ExceptionClause(object):
    def __init__(self):
        self.try_offset = 0
        self.try_len = 0
        self.handler_offset = 0
        self.handler_len = 0

def _strip_comment(line):
    line = line.strip()
    i = line.find('//')
    if i == -1:
        return line
    else:
        return line[:i]

#假设传入的是非空字符串
def _read_label(line):
    return None, line

#假设传入的是非空字符串
def _read_opcode(line):
    pass

def _read_op_argment(op, line):
    pass


#假设传入的是非空字符串
def _parse_first(line):
    '''line = line.strip()
    #print "_parse_first : " + line
    line_info = LineInfo()
    label, line = _read_label(line)
    line_info.labels.append(label)
    if line == '':
        return line_info
    op, line = _read_opcode(line)
    jmps, line = _read_op_argment(op, line)  #感觉这里返回jmps不清晰, 但传入line_info也好不到哪去
    if line != '':
        print line
        raise Exception("多余的字节出现")
    line_info.opcode = op
    line_info.jmps = jmps
    return line_info'''

def _encode_line(line):
    '''opcode = line.opcode
    if opcode and opcode.size > 0:
        return "".join(opcode.op) + "".join(opcode.args)
    return ""'''


def cil_compile(s):
    pass
if __name__ == '__main__':
    a, err = cil_compile(s, None)
    if not a:
        print err
    else:
        code = err[0]
        print len(code)
        f = open("1.bin", "wb")
        f.write(code)
        f.close()
        n = 0
        x = []
        for i in code:
            if n % 16 == 0:
                print " ".join(x)
                x = []
            x.append("{0}".format(hex(ord(i))))
            n = n + 1
        print " ".join(x)
        ex = err[1]
        for i in ex.keys():
            e = ex[i]
            print e.try_offset, e.try_len
            print e.handler_offset, e.handler_len
