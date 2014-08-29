# -*- coding: utf-8 -*-
#file: JdwpHandle.py
#author: object
#description: Jdwp协议操作

import socket
import AdbHelper
import threading
import JdwpBuf
from threading import Thread, Lock
from Queue import Queue, Empty as EmptyQueue


class HandshakeError(Exception):
    'signals that the JDWP handshake failed'
    def __init__(self):
        Exception.__init__(
            self, 'handshake error, received message did not match'
        )

class ProtocolError(Exception):
    pass

HANDSHAKE_MSG = 'JDWP-Handshake'
HEADER_FORMAT = '4412'
IDSZ_REQ = (
    '\x00\x00\x00\x0B' # Length
    '\x00\x00\x00\x01' # Identifier
    '\x00'             # Flags
    '\x01\x07'         # Command 1:7  IDSizes Command (7)
)

#adb -s [dev] forward localfilesystem: [temp] jdwp [pid]
#adb -s emulator-5554 forward  localfilesystem:/tmp/tmpzeJZR5 jdwp:333 
#与虚拟机建立链接
def forward(pid, dev=None):
    'constructs an adb forward for the context to access the pid via jdwp'
    if dev:
        dev = AdbHelper.find_dev(dev)
    pid = AdbHelper.find_pid(pid)
    cmd = ('-s', dev) if dev else ()  #'-s', 'emulator-5554'
    cmd += ('forward', 'tcp:8888',  'jdwp:%s' % pid) #'-s', 'emulator-5554', 'forward', 'localfilesystem:/tmp/tmpSSCNAl', 'jdwp:843')
    AdbHelper.adb(*cmd)
    return 8888
def connect(addr, portno = None, trace=False):
    'connects to an AF_UNIX or AF_INET JDWP transport'
    if addr and portno:
        conn = socket.create_connection((addr, portno))
    elif isinstance(addr, int):
        conn = socket.create_connection(('127.0.0.1', addr))
    else:
        conn = socket.socket(socket.AF_UNIX)
        conn.connect(addr)

    #负责读出数据的函数
    def read(amt):
        req = amt
        buf = ''
        while req:
            pkt = conn.recv(req)
            if not pkt: raise EOF()
            buf += pkt
            req -= len(pkt)
        if trace:
            print ":: RECV:", repr(buf)
        return buf 
    
    #负责写入数据的函数
    def write(data):
        try:
            if trace:
                print ":: send:", repr(data)
            print ":: send:", repr(data)
            conn.sendall(data)
        except Exception as exc:
            raise EOF(exc)
        
    p = Connection(read, write)  #定义一个Connection对象
    p.start()
    return p

class Connection(Thread):
    def __init__(self,read,write):
        Thread.__init__(self)
        self.recvbuf = JdwpBuf.PyBuf()
        self.initialized = False
        self._read = read
        self.write = write
        self.bindqueue = Queue()  #定义一个先进先出的队列
        self.qmap = {}   #初始化一个空的字典
        self.rmap = {}   #初始化一个空的字典
        self.evtq = Queue() #定义一个evt请求队列
        self.callback_func = {}
        self.ethd = threading.Thread(
            name='Connection', target=self.handrun  #线程的名称，线程的执行函数
        )
        self.ethd.daemon=1  #主线程结束时，会把子线程也杀死。
        self.ethd.start()

    #读数据的函数，sz准备读取数据的长度，
    def read(self, sz):
        'read size bytes'
        if sz == 0: return ''
        pkt = self._read(sz)  #返回值是读到的数据
        if not len(pkt): raise EOF()   #如果读到的数据的长度为0，抛出EOF异常
        return pkt
    
    def readHeader(self):
        data = self.read(11)
        buf = JdwpBuf.PyBuf(data)
        retdata = buf.unpack('!IIBH')
        return retdata
    #接收握手数据
    def readHandshake(self):
        data = self.read(len(HANDSHAKE_MSG))
        if data != HANDSHAKE_MSG:
            raise HandshakeError()  #抛出握手失败异常
    #发送握手数据    
    def writeHandshake(self):
        return self.write(HANDSHAKE_MSG)

    #接受虚拟机请求的线程，死循环
    def handrun(self):
        while True:
            self.dispatchRequest(*self.evtq.get())
            print "recved from VM"

    def dispatchRequest(self,cmds,buf):
        func = self.callback_func[cmds]
        return func(cmds,buf)

    #设置从虚拟机发过来的请求的回调函数    
    def setcallback(self,cmds,func):
        self.callback_func[cmds] = func
        self.bindqueue.put(('r', cmds, self.evtq))


    def request(self, buf, timeout=None):
        lens,ident,flags,cmds = buf.unpack('!IIBH')
        queue = Queue()
        self.bindqueue.put(('q', ident, queue))
        self.write(buf.buf)
        try:
            return queue.get(1, timeout)
        except EmptyQueue:
            return None, None

    #以下函数在收包线程中运行
    #process函数在死循环中运行
    def process(self):
        size, ident, flags, code = self.readHeader()
        size -= 11
        data = self.read(size) 
        try: 
            while True:
                self.processBind(*self.bindqueue.get(False)) 
        except EmptyQueue:
            pass

        #TODO: update binds with all from bindqueue
        #对于来自虚拟机的事件消息，self.processBind(*self.bindqueue.get(False))不起作用，直接触发EmptyQueue异常，后续调用processRequest函数
        if flags == 0x80:  
            self.processResponse(ident, code, data)  #答复数据包的flag是0x80
        else:
            self.processRequest(ident, code, data)  #请求数据包的flag是0x00
    #函数调用的参数为：qr="r" ident=16484=0x4064 chan 是一个在Session类中定义的一个队列。qr="q" ident=3 其中ident是请求的编号id，调试器发往虚拟机的id从3开始
    def processBind(self, qr, ident, chan):
        if qr == 'q':
            self.qmap[ident] = chan  
        elif qr == 'r':
            self.rmap[ident] = chan
           

    #处理请求
    ##请求数据包的flag是0x00
    def processRequest(self, ident, cmds, data):
        chan = self.rmap.get(cmds)  #所有中断都由该chan队列处理，每次只是从rmap读出内容，而没有将rmap对应的chan清除
        if not chan:
            print "get erro"
            return #TODO
        return chan.put((cmds, data)) #将解析后的数据压入队列中
     
    def processResponse(self, ident, code, data):
        chan = self.qmap.pop(ident, None) #从字典中读取，并删除该数据
        if not chan: return
        return chan.put((code, data))

    def start(self):
        self.daemon = True  #守护线程

        if not self.initialized: #如果为false初始化尚未完成，完成下面初始化工作
            self.writeHandshake()
            self.readHandshake()
            #self.writeIdSzReq()
            #self.readIdSzRes()
            self.initialized = True #确认完成初始话
            Thread.start(self)
        return None
    def run(self):
        try:
            while True:
                self.process()
        except 'EOF':
            return

if __name__ == '__main__':
    pid = 12368
    dev = None
    conn = connect(forward(pid, dev))
    while True:
        pass