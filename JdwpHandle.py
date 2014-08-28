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
        self.sendbuf = JdwpBuf.PyBuf()
        self.conn = JdwpNet.connect(JdwpNet.forward(pid, dev))

    def acquireIdent(self):
        ident = self.next_id
        self.next_id += 2
        return ident


class ReferenceType(object):
    def __init__(self,sess):
        self.sess = sess
class MethodContext(object):
    def __init__(self,sess):
        self.sess = sess
class ThreadContext(object):
    def __init__(self,sess):
        self.sess = sess
class ClassContext(object):
    def __init__(self,sess):
        self.sess = sess
class DalvkVm(object):
    def __init__(self, sess):
        self.sess = sess
        self.classList = []
    def classes(self):
        if len(self.classList):
            return self.classList
        return self.getallclass()
    def getallclass(self):
        cmd = 20
        cmdSet = 1
        cmds = (cmdSet << 8) | cmd
        ident = self.sess.acquireIdent()
        self.sess.sendbuf.clear()
        self.sess.sendbuf.pack('!IIBH',11,ident,0,cmds)
        code,data = self.sess.conn.request(ident,cmds,self.sess.sendbuf.buf)
        if not code:
            buf = JdwpBuf.PyBuf(data)
            classCnt = buf.unpackU32()
            for i in range(classCnt[0]):
                refTypeTag = buf.unpackU8()
                refTypeId = buf.unpackU64()
                strlen,strClassName = buf.unpackStr()
                status = buf.unpackU16()
                print strClassName


if __name__ == '__main__':
    sess = Session(8350,None)
    vm = DalvkVm(sess)
    vm.classes()

    