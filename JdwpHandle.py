# -*- coding: utf-8 -*-
#file: JdwpHandle.py
#author: object
#description: Jdwp协议操作

from ctypes import *
import re
import JdwpBuf
import JdwpNet


def printBuf(buf):
    bdata = cast(buf.buf.data,POINTER(c_byte))
    for i in xrange(buf.buf.len):
        print bdata[i]


def printHex(data,size):
    for i in range(0,size,16):
        for j in range(0,16):
            print "i=%d,j=%d,%x" %(i,j,ord(data[i+j]))

class Session(object):
    def __init__(self, pid, dev):
        self.next_id = 3
        self._hSize = 11
        self.sendbuf = JdwpBuf.PyBuf()
        self.conn = JdwpNet.connect(JdwpNet.forward(pid, dev))

    def acquireIdent(self):
        ident = self.next_id
        self.next_id += 2
        return ident
    def packJdwpHeader(self,datalen,cmdSet,cmd):
        lens = datalen+self._hSize
        ident = self.sess.acquireIdent()
        cmds = (cmdSet << 8) | cmd
        self.sendbuf.pack('!IIBH',lens,ident,0,cmds)


class ReferenceType(object):
    def __init__(self,sess):
        self.sess = sess
class MethodContext(object):
    def __init__(self,sess,rtId,methId):
        self.sess = sess
        self.methId = methId
        self.rtId = rtId
    def getBytecodes(self):
        lens = 12
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,ident,199,1)
        self.sess.sendbuf.packU64(self.rtId)
        self.sess.sendbuf.packU32(self.methId)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        elif:
            print 'erro'
    def setbreak(self,callback_func):

class ThreadContext(object):
    def __init__(self,sess,tid):
        self.sess = sess
        self.tid = tid
    def framCnt(self):
        lens = 8
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,ident,199,1)
        self.sess.sendbuf.packU64(self.tid)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        elif:
            print 'erro'
    def frams(self):
        lens = 16
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,ident,199,1)
        cnt = self.framCnt()
        self.sess.sendbuf.packU64(self.tid)
        self.sess.sendbuf.packU32(0)
        self.sess.sendbuf.packU32(cnt)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        elif:
            print 'erro'
    def suspend(self):
        lens = 16
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,ident,199,1)
        cnt = self.framCnt()
        self.sess.sendbuf.packU64(self.tid)
        self.sess.sendbuf.packU32(0)
        self.sess.sendbuf.packU32(cnt)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        elif:
            print 'erro'
    def resume(self):
        lens = 16
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,ident,199,1)
        cnt = self.framCnt()
        self.sess.sendbuf.packU64(self.tid)
        self.sess.sendbuf.packU32(0)
        self.sess.sendbuf.packU32(cnt)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        elif:
            print 'erro'


class ClassContext(object):
    def __init__(self,sess,refTypeTag,refTypeId,strClassName):
        self.sess = sess
        self.refTypeTag = refTypeTag
        self.refTypeId = refTypeId
        self.strClassName = strClassName
    def methods(self):
        pass
class DalvkVm(object):
    def __init__(self, sess):
        self.sess = sess
        self.classList = []
    def classes(self):
        if len(self.classList):
            return self.classDict
        return self.getallclass()
    def getallclass(self):
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(0,ident,1,20)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            buf = JdwpBuf.PyBuf(data)
            classCnt = buf.unpackU32()
            for i in range(classCnt[0]):
                refTypeTag = buf.unpackU8()
                refTypeId = buf.unpackU64()
                strlen,strClassName = buf.unpackStr()
                status = buf.unpackU16()
                self.classDict[strClassName] = ClassContext(self.sess,refTypeTag,refTypeId,strClassName)
        return self.classDict

    def start_trace(self):
        lens = 8
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,ident,199,1)
        self.sess.sendbuf.packU32()
        self.sess.sendbuf.packU32(0)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        elif:
            print 'erro'
    def end_trace(self):
        lens = 8
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,ident,199,1)
        self.sess.sendbuf.packU32()
        self.sess.sendbuf.packU32(0)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        elif:
            print 'erro'
    def trace_callback(self):
        pass
class VmManage(object):
    def 
if __name__ == '__main__':
    sess = Session(8350,None)
    vm = DalvkVm(sess)
    vm.classes()

'''todo list
堆栈回溯
函数修改
'''
    