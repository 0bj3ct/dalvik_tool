# -*- coding: utf-8 -*-
#file: JdwpHandle.py
#author: object
#description: Jdwp协议操作

from ctypes import *
from threading import *
import re
import JdwpBuf
import JdwpNet
import TraceReader
import time

JDWP_EVENT_SIZE = 56
DDMSBUF_SIZE = 1024*1024*8

CHUNK_MPSS = 0x4d505353
CHUNK_MPSE = 0x4d505345


#JdwpEventKind
EK_SINGLE_STEP          = 1
EK_BREAKPOINT           = 2
EK_FRAME_POP            = 3
EK_EXCEPTION            = 4
EK_USER_DEFINED         = 5
EK_THREAD_START         = 6
EK_THREAD_END           = 7
EK_CLASS_PREPARE        = 8
EK_CLASS_UNLOAD         = 9
EK_CLASS_LOAD           = 10
EK_FIELD_ACCESS         = 20
EK_FIELD_MODIFICATION   = 21
EK_EXCEPTION_CATCH      = 30
EK_METHOD_ENTRY         = 40
EK_METHOD_EXIT          = 41
EK_VM_INIT              = 90
EK_VM_DEATH             = 99
EK_VM_DISCONNECTED      = 100  #/* "Never sent across JDWP */
EK_VM_START             = EK_VM_INIT
EK_THREAD_DEATH         = EK_THREAD_END

#JdwpModKind
MK_COUNT                = 1
MK_CONDITIONAL          = 2
MK_THREAD_ONLY          = 3
MK_CLASS_ONLY           = 4
MK_CLASS_MATCH          = 5
MK_CLASS_EXCLUDE        = 6
MK_LOCATION_ONLY        = 7
MK_EXCEPTION_ONLY       = 8
MK_FIELD_ONLY           = 9
MK_STEP                 = 10
MK_INSTANCE_ONLY        = 11

class BreakInfo:
    def __init__(self):
        self.breakId = 0
        self.requestID = 0
        self.eventKind = 0
        self.loc = None
        self.callbackFunc = None
class Location:
    def __init__(self,typeTag,rtId,mId,idx):
        self.typeTag = typeTag
        self.rtId = rtId
        self.mId = mId
        self.idx = idx
class Slot:
    def __init__(self,codeIndex,name,signature,genericSignature,length,slot):
        self.codeIndex = codeIndex
        self.name = name
        self.signature = signature
        self.genericSignature = genericSignature
        self.length = length
        self.slot = slot
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
        self._traceDict = {}
        self._eventDict = {}
        self.sendbuf = JdwpBuf.PyBuf()
        self.ctxt = Context()
        if pid == None:
            self.conn = JdwpNet.connect(20086)
        else:
            self.conn = JdwpNet.connect(JdwpNet.forward(pid, dev))

    def initCb(self):
        self.conn.setcallback(0xc701,self._traceHandle)
        self.conn.setcallback(0x4064,self._eventRequest)
    def acquireIdent(self):
        ident = self.next_id
        self.next_id += 2
        return ident
    def packJdwpHeader(self,datalen,cmdSet,cmd):
        lens = datalen+self._hSize
        ident = self.acquireIdent()
        cmds = (cmdSet << 8) | cmd
        self.sendbuf.pack('!IIBH',lens,ident,0,cmds)
    def _eventRequest(self,cmds,data):
        buf = JdwpBuf.PyBuf(data)
        suspendPolicy = buf.unpackU8()
        eventCnt = buf.unpackU32()
        eventKind = buf.unpackU8()
        requestId = buf.unpackU32()
        tid = buf.unpackU64()
        bpInfo = self._eventDict[requestId]
        print bpInfo.callbackFunc
        bpInfo.callbackFunc(bpInfo,tid)
    def _traceHandle(self,cmds,data):
        for k in self._traceDict.keys():
            cb = self._traceDict[k]
            cb(cmds,data)

    #flags默认为当前函数，当flags相同时，回调会覆盖掉以前的
    #可以以发起函数为flags
    def addTraceCb(self,cbFunc,flags = "D"):
        self._traceDict[flags] = cbFunc

    def addeventHandle(self,requestId,bpInfo):
        self._eventDict[requestId] = bpInfo

    def deleventHandle(self,requestId):
        bpInfo = self._eventDict[requestId]
        del self._eventDict[requestId]
        return bpInfo
class MethodContext(object):
    def __init__(self, rtId, methId, sess):
        self.sess = sess
        self.methId = methId
        self.rtId = rtId
        self.funcMap = {}
        self.name = "test"

    def setbreak(self,idx,callback_func,key):
        lens = JDWP_EVENT_SIZE
        sendbuf = self.sess.sendbuf
        sendbuf.clear()
        self.sess.packJdwpHeader(lens,15,1)
        
        if idx==0:
            sendbuf.packU8(EK_METHOD_ENTRY)  #eventKind
            sendbuf.packU8(1) #suspendPolicy
            sendbuf.packU32(1) #modCnt
            sendbuf.packU8(MK_LOCATION_ONLY) #modKind

            #loc
            sendbuf.packU8(1) #typeTag
            sendbuf.packU64(self.rtId)
            sendbuf.packU32(self.methId)
            sendbuf.packU64(idx)
            for i in xrange(39,67):
                sendbuf.packU8(0)
        else:
            sendbuf.packU8(EK_BREAKPOINT)  #eventKind
            sendbuf.packU8(1) #suspendPolicy
            sendbuf.packU32(1) #modCnt
            sendbuf.packU8(MK_LOCATION_ONLY) #modKind

            #loc
            sendbuf.packU8(1) #typeTag
            sendbuf.packU64(self.rtId)
            sendbuf.packU32(self.methId)
            sendbuf.packU64(idx)

            #len= 39,总共大小67，不足的填充为0
            for i in xrange(39,67):
                sendbuf.packU8(0)
        code,data = self.sess.conn.request(sendbuf)
        print "suss"
        if not code:
            recvbuf = JdwpBuf.PyBuf(data)
            requestId = recvbuf.unpackU32()
            loc = Location(1,self.rtId,self.methId,idx)
            bp = BreakInfo()
            bp.requestId = requestId
            bp.loc = loc
            bp.callbackFunc = callback_func
            self.sess.addeventHandle(requestId,bp)
            self.funcMap[key] = requestId
        else:
            print 'erro'
    def unsetbreak(self,key):
        requestId = self.funcMap[key]
        bp = self.sess.deleventHandle(requestId)
        eventKind = bp.eventKind
        lens = 5
        sendbuf = self.sess.sendbuf
        sendbuf.clear()
        self.sess.packJdwpHeader(lens,15,2)
        sendbuf.packU8(eventKind)
        sendbuf.packU32(requestId)
        code,data = self.sess.conn.request(sendbuf)
        if not code:
            pass
        else:
            print 'erro'

    def getBytecodes(self):
        lens = 12
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,6,3)
        self.sess.sendbuf.packU64(self.rtId)
        self.sess.sendbuf.packU32(self.methId)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            buf = JdwpBuf.PyBuf(data)
            codelen = buf.unpackU32()
            bytecode = data[4:codelen*2+4]
            print codelen
            print len(bytecode)
            print repr(bytecode)
            return codelen,bytecode
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
    def getVariableTable(self):
        lens = 8+4
        slots = []
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,6,5)
        sendbuf = self.sess.sendbuf
        sendbuf.packU64(self.rtId)
        sendbuf.packU32(self.methId)
        code,data = self.sess.conn.request(sendbuf)
        if not code:
            buf = JdwpBuf.PyBuf(data)
            argCnt = buf.unpackU32()
            slotCnt = buf.unpackU32()
            for i in range(0,slotCnt):
                codeIndex = buf.unpackU64()
                strlen,name = buf.unpackStr()
                strlen,jni = buf.unpackStr()
                strlen,gen = buf.unpackStr()
                length = buf.unpackU32()
                slot_id = buf.unpackU32()
                slot = Slot(codeIndex,name,jni,gen,length,slot_id)
                slots.append(slot)

        else:
            print 'erro'
        return slots,argCnt

class FrameInfo(object):
    def __init__(self,frameID,loc,tid,sess):
        self.frameID = frameID
        self.loc = loc
        self.tid = tid
        self.sess = sess
    #todo
    def GetValues(self):
        vals = []
        if self.native: return vals  #如果是系统函数返回空
        sess = self.sess
        sendbuf = sess.sendbuf
        ctxt = sess.ctxt
        method = ctxt.objpool(MethodContext,self.loc.rtId,self.loc.mId,sess)
        slots,argCnt = method.getVariableTable()
        slotCnt = len(slots)
        lens = 8+8+4+5*slotCnt

        sendbuf.clear()
        self.sess.packJdwpHeader(lens,16,1)
        sendbuf.packU64(self.tid)
        sendbuf.packU64(self.frameID)  
        sendbuf.packU32(len(slots))

        for slot in slots:
            sendbuf.packU32(slot.slot)  #局部变量的索引值
            tag = slot.signature[0]
            print slot.signature
            sendbuf.packU8(ord(tag)) #标志变量类型的标签
        code,data = self.sess.conn.request(sendbuf)
        if not code:
            buf = JdwpBuf.PyBuf(data)
            ct = buf.unpackU32()
            print "ct: %d" % ct

            for x in range(0, ct):
                s = slots[x]

                #unpack_value
                #print "%s:%d" % (s.name,self.unpack_value(s.signature[0],buf))
                vals.append((s.name,self.unpack_value(s.signature[0],buf)))
        return vals

    def unpack_value(self,tag,buf):
        if tag=="[":
            return buf.unpackU64()
        elif tag=="B":
            return buf.unpackU8()
        elif tag=="C":
            return buf.unpackU16()
        elif tag=="L":
            return buf.unpackU64()
        elif tag=="F":
            return buf.unpackU32()
        elif tag=="D":
            return buf.unpackU64()
        elif tag=="I":
            return buf.unpackU32()
        elif tag=="J":
            return buf.unpackU64()
        elif tag=="S":
            return buf.unpackU16()
        elif tag=="V":
            return 99999
            #return buf.unpackU64()
        elif tag=="Z":
            return buf.unpackU8()
        elif tag=="s":
            return buf.unpackU64()
        elif tag=="t":
            return buf.unpackU64()
        elif tag=="g":
            return buf.unpackU64()
        elif tag=="l":
            return buf.unpackU64()
        elif tag=="c":
            return buf.unpackU64()
        else:
            print "unpack_value erro"
    @property
    def native(self):
        print self.loc.idx 
        return self.loc.idx == -1

class ThreadContext(object):
    def __init__(self, tid, sess):
        self.sess = sess
        self.tid = tid
    def framCnt(self):
        lens = 8
        sendbuf = self.sess.sendbuf
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,11,7)
        sendbuf.packU64(self.tid)
        code,data = self.sess.conn.request(sendbuf)
        if not code:
            buf = JdwpBuf.PyBuf(data)
            cnt = buf.unpackU32()
        else:
            print 'framCnt erro'
        return cnt
    def frams(self):
        framsList = []
        lens = 16
        cnt = self.framCnt()
        sendbuf = self.sess.sendbuf
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,11,6)
        sendbuf.packU64(self.tid)
        sendbuf.packU32(0)
        sendbuf.packU32(cnt)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            buf = JdwpBuf.PyBuf(data)
            framesCount = buf.unpackU32()
            for i in range(framesCount):
                frameID = buf.unpackU64()

                #loc
                typeTag = buf.unpackU8()
                classId = buf.unpackU64()
                methodId = buf.unpackU32()
                idx = buf.unpack64()

                loc = Location(typeTag,classId,methodId,idx)
                framsList.append((frameID,loc))
            return framsList
        else:
            print 'frams erro'
    def suspend(self):
        lens = 8
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,11,2)
        self.sess.sendbuf.packU64(self.tid)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            pass
        else:
            print 'erro'
    def resume(self):
        lens = 8
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,11,3)
        self.sess.sendbuf.packU64(self.tid)
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
        self.jni,self.gen = self.getSignature()
        self.name = self.getName(self.jni)
        self.methodMap = {}

    #todo 
    def methods(self):
        tid = self.rtId
        sess = self.sess
        conn = sess.conn
        lens = 8
        sess.sendbuf.clear()
        sess.packJdwpHeader(lens,2,15)
        sess.sendbuf.packU64(self.rtId)
        code,data = conn.request(sess.sendbuf)

        if not code:
            buf = JdwpBuf.PyBuf(data)
            methCnt = buf.unpackU32()
            for i in range(methCnt):
                mid = buf.unpackU32()
                strlen,name = buf.unpackStr()
                strlen,jni = buf.unpackStr()
                strlen,gen = buf.unpackStr()
                flags = buf.unpackU32()
                self.methodMap[mid] = (name,jni)
        else:
            print "methods erro"
    def getMethodName(self,mId):
        if len(self.methodMap)==0:
            self.methods()
        return self.methodMap[mId]

    def getSignature(self):
        rtId = self.rtId
        sess = self.sess
        conn = sess.conn
        lens = 8
        sess.sendbuf.clear()
        sess.packJdwpHeader(lens,2,13)
        sess.sendbuf.packU64(rtId)
        code,data = conn.request(sess.sendbuf)

        if not code:
            buf = JdwpBuf.PyBuf(data)
            strlen,jni = buf.unpackStr()
            strlen,gen = buf.unpackStr()
            return jni,gen
        else:
            return None,None
    def getName(self,name):
        if name.startswith('L'): name = name[1:]
        if name.endswith(';'): name = name[:-1]
        return name
'''
rtTag :1 ClassType
        2 interface
        3 array
'''
class ClassType(ReferenceType):
    def __init__(self, refTypeId, sess):
        ReferenceType.__init__(self, 1, refTypeId, sess)
        
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
        self.traceCb = None
        self.classDict = {}
        self.classes()
    def classes(self):
        if len(self.classDict):
            return self.classDict
        return self.getallclass()
    def getClass(self,clsName):
        if clsName in self.classDict.keys():
            return self.classDict[clsName]
        else:
            return None
    def getallclass(self):
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(0,1,20)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        if not code:
            buf = JdwpBuf.PyBuf(data)
            classCnt = buf.unpackU32()
            for i in range(0,classCnt):
                refTypeTag = buf.unpackU8()
                refTypeId = buf.unpackU64()
                strlen,strClassName = buf.unpackStr()
                strlen,strgen = buf.unpackStr()
                status = buf.unpackU32()
                #print "refTypeTag %d" % refTypeTag
                if int(refTypeTag) == 1:
                    self.classDict[strClassName] = self.sess.ctxt.objpool(ClassType, refTypeId, self.sess)

                        
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
    def end_trace(self,traceCb=None):
        lens = 8
        self.sess.sendbuf.clear()
        self.sess.packJdwpHeader(lens,199,1)
        #self.sess.conn.setcallback(0xc701,self._trace_end)
        self.traceCb = traceCb
        self.sess.addTraceCb(self.trace_end)
        self.sess.sendbuf.packU32(CHUNK_MPSE)
        self.sess.sendbuf.packU32(0)
        code,data = self.sess.conn.request(self.sess.sendbuf)
        print code
        if not code:
            pass
        else:
            print 'erro'
    def trace_end(self,cmds,data):
        reader = TraceReader.TraceReader('m',data) 
        print "trace_end"
        '''for m in reader.callInfo:
            if m["method_action"]:
                method_info = reader.funcData[m["method_id"]]
                print "enter %s:%s" % (method_info["class_name"],method_info["method_name"])'''
        if self.traceCb != None:
            self.traceCb(reader)
        else:
            print "please regist traceCb"
class Context(object):
    def __init__(self):
        self.lock = Lock()
        self.pools = {}
    def objpool(self,*ids):
        with self.lock:
            obj = self.pools.get(ids)
            if obj is None:
                obj = ids[0](*ids[1:])  #构造一个obj出来
                self.pools[ids] = obj
            return obj
    #def obj(self,objtype,*ident)

#Context ctxt
if __name__ == '__main__':
    sess = Session(21631,None)
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
    