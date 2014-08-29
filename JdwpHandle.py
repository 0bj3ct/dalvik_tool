# -*- coding: utf-8 -*-
#file: JdwpHandle.py
#author: object
#description: Jdwp协议操作

from ctypes import *
import re
import JdwpBuf
import JdwpNet
import TraceReader
import time

JDWP_EVENT_SIZE = 56
DDMSBUF_SIZE = 1024*1024*8

CHUNK_MPSS = 0x4d505353
CHUNK_MPSE = 0x4d505345
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
        ident = self.acquireIdent()
        cmds = (cmdSet << 8) | cmd
        self.sendbuf.pack('!IIBH',lens,ident,0,cmds)


class MethodContext(object):
    def __init__(self,sess,rtId,methId):
        self.sess = sess
        self.methId = methId
        self.rtId = rtId
    def getBytecodes(self):
        lens = 12
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,199,1)
        self.sess.sendbuf.packU64(self.rtId)
        self.sess.sendbuf.packU32(self.methId)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        else:
            print 'erro'
    def setbreak(self,idx,callback_func):
        lens = JDWP_EVENT_SIZE
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,15,1)
        
        #todo
        self.sess.sendbuf.packU64(self.rtId)
        self.sess.sendbuf.packU32(self.methId)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        else:
            print 'erro'
    def setBytecodes(self,data):
        lens = 12+len(data)
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,6,6)
        self.sess.sendbuf.packU64(self.rtId)
        self.sess.sendbuf.packU32(self.methId)
        self.sess.sendbuf.packU32(len(data))
        self.sess.sendbuf.buf += data
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        else:
            print 'erro'
class ThreadContext(object):
    def __init__(self,sess,tid):
        self.sess = sess
        self.tid = tid
    def framCnt(self):
        lens = 8
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,199,1)
        self.sess.sendbuf.packU64(self.tid)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        else:
            print 'erro'
    def frams(self):
        lens = 16
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,199,1)
        cnt = self.framCnt()
        self.sess.sendbuf.packU64(self.tid)
        self.sess.sendbuf.packU32(0)
        self.sess.sendbuf.packU32(cnt)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        else:
            print 'erro'
    def suspend(self):
        lens = 16
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,199,1)
        cnt = self.framCnt()
        self.sess.sendbuf.packU64(self.tid)
        self.sess.sendbuf.packU32(0)
        self.sess.sendbuf.packU32(cnt)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        else:
            print 'erro'
    def resume(self):
        lens = 16
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,199,1)
        cnt = self.framCnt()
        self.sess.sendbuf.packU64(self.tid)
        self.sess.sendbuf.packU32(0)
        self.sess.sendbuf.packU32(cnt)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        else:
            print 'erro'


class ReferenceType(object):
    def __init__(self,rtTag,rtId,sess):
        self.sess = sess
        self.rtTag = rtTag
        self.rtId = rtId
    def load_methods(self):
        tid = self.rtId
        sess = self.sess
        conn = sess.conn
        lens = 8
        sess.sendbuf.clear()
        sess.packJdwpHeader(lens,ident,2,15)
        sess.sendbuf.packU64(self.rtId)
        code,data = conn.request(sess.sendbuf)

        if code != 0:
            raise RequestError(code)

        ct = buf.unpackU32()
                
        def load_method():
            mid, name, jni, gen, flags = buf.unpack('m$$$i') #method_id str str str int
            obj = pool(Method, sess, tid, mid)
            obj.name = name
            obj.jni = jni
            obj.gen = gen
            obj.flags = flags       
            return obj

'''
rtTag :1 ClassType
        2 interface
        3 array
'''
class ClassType(ReferenceType):
    def __init__(self, sess, refTypeId):
        RefType.__init__(self, sess, 1, refTypeId)
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return '<class %s>' % self

    def hookEntries(self, func = None, queue = None):
        '''
        1 命令： 0x0f 0x01
        2 功能：设置事件
        3 解释：[EventRequest Command Set (15)][Set Command (1)]
        '''
        conn = self.conn
        buf = conn.buffer()
        # 40:KEK_METHOD_ENTRY, 1: EVENT_THREAD, 1：modifiers（只有一个mod） 4：modKind是4，含义是 condition of type ClassRef (4)
        # 针对4这个modkind值，需要传入一个指定的Reference TypeID 
        buf.pack('11i1t', 40, 1, 1, 4, self.tid)  #tid为type id
        log.debug("study", "call jdwp 0x0F 01")
        code, buf = conn.request(0x0F01, buf.data(), g_jdwp_request_timeout)
        if code != 0:
            raise RequestError(code)
        eid = buf.unpackInt() #返回值是一个requestID ：ID of created request
        log.debug("study", "eid=" + str(eid)) #eid=536870915
        return self.sess.hook(eid, func, queue, self)


class DalvkVm(object):
    def __init__(self, sess):
        self.sess = sess
        self.classList = []
        self.traceCb = []
    def classes(self):
        if len(self.classList):
            return self.classDict
        return self.getallclass()
    def getallclass(self):
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(0,1,20)
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
        lens = 8+8
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,199,1)
        self.sess.sendbuf.packU32(CHUNK_MPSS)
        self.sess.sendbuf.packU32(8)
        self.sess.sendbuf.packU32(DDMSBUF_SIZE)
        self.sess.sendbuf.packU32(8)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            print data
        else:
            print 'erro'
    def end_trace(self):
        lens = 8
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,199,1)
        self.sess.conn.setcallback(0xc701,self._trace_end)
        self.sess.sendbuf.packU32(CHUNK_MPSE)
        self.sess.sendbuf.packU32(0)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        print code
        if not code:
            pass
        else:
            print 'erro'
    def _trace_end(self,cmds,data):
        buf = data[8:]
        print buf
        reader = TraceReader.TraceReader('m',data)

    def set_trace_callback(self,cbFunc):
        #self.traceCb[0] = cbFunc
        pass
class Context(object):
    def __init__(self):
        self.ta = 0
    #def obj(self,objtype,*ident)
if __name__ == '__main__':
    sess = Session(12368,None)
    vm = DalvkVm(sess)
    vm.start_trace()
    time.sleep(1)
    vm.end_trace()
    while True:
        pass

'''todo list
堆栈回溯
函数修改
'''
    