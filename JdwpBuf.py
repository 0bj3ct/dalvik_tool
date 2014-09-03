# -*- coding: utf-8 -*-
#file: JdwpHandle.py
#author: object
#description: Jdwp协议操作


from ctypes import *
import re
import JdwpNet
import struct

class PyBuf(object):
    def __init__(self,recvbuf = ''):
        self.buf = recvbuf
        self.pos = 0
    def clear(self):
        self.buf = ''
        self.pos = 0
    def packU8(self,data):
        self.buf += struct.pack('B',data)
    def packU16(self,data):
        self.buf += struct.pack('!H',data)
    def packU32(self,data):
        self.buf += struct.pack('!I',data)
    def packU64(self,data):
        self.buf += struct.pack('!Q',data)
    def packStr(self,data):
        size = len(data)
        self.buf += struct.pack('!I',size)
        self.buf += data
    def pack(self, fmt, *data):
        self.buf += struct.pack(fmt,*data)
    

    def unpackU8(self):
        size = struct.calcsize('!B')
        s = self.buf[self.pos:self.pos+size]
        data = struct.unpack('!B',s)
        self.pos += size
        return data[0]
    def unpackU16(self):
        size = struct.calcsize('!H')
        print self.pos
        s = self.buf[self.pos:self.pos+size]
        print len(s)
        data = struct.unpack('!H',s)
        self.pos += size
        return data[0]
    def unpackU32(self):
        size = struct.calcsize('!I')
        s = self.buf[self.pos:self.pos+size]
        data = struct.unpack('!I',s)
        self.pos += size
        return data[0]
    def unpackU64(self):
        size = struct.calcsize('!Q')
        s = self.buf[self.pos:self.pos+size]
        data = struct.unpack('!Q',s)
        self.pos += size
        return data[0]
    def unpackStr(self):
        size = struct.calcsize('!I')
        s = self.buf[self.pos:self.pos+size]
        strlen = struct.unpack('!I',s)[0]
        self.pos += size
        data = self.buf[self.pos:self.pos+int(strlen)]
        self.pos += int(strlen)
        return strlen,data
    def unpack(self,fmt):
        size = struct.calcsize(fmt)
        s = self.buf[self.pos:self.pos+size]
        data = ()
        data = struct.unpack(fmt,s)
        self.pos += size
        return data

'''
class JDWPBUFFER(Structure):
    _fields_ = [
        ("fSz", c_byte),
        ("mSz", c_byte),
        ("oSz", c_byte),
        ("tSz", c_byte),
        ("sSz", c_byte),
        ("ofs", c_int),
        ("len", c_int),
        ("cap", c_int),
        ("data", c_void_p)];

class PyBuf(object):
    def __init__(self):
        self.packfmt = {
            "1":self.packU8,
            "2":self.packU16,
            "4":self.packU32,
            "8":self.packU64,
        }
        self.unpackfmt = {
            "1":self.unpackU8,
            "2":self.unpackU16,
            "4":self.unpackU32,
            "8":self.unpackU64,
        }
        self.hDll = CDLL('XDalvikTool.dll')
        self.buf = JDWPBUFFER(0,0,0,0,0,0,0,1024,None)
        ret = self.hDll.JdwpInitBuffer(byref(self.buf))
    def packU8(self,data):
        self.hDll.JdwpPackU1(byref(self.buf),c_byte(data))
    def packU16(self,data):
        self.hDll.JdwpPackU2(byref(self.buf),c_short(data))
    def packU32(self,data):
        self.hDll.JdwpPackU4(byref(self.buf),c_int(data))
    def packU64(self,data):
        self.hDll.JdwpPackU8(byref(self.buf),c_longlong(data))
    def packStr(self,data):
        self.hDll.JdwpPackString(byref(self.buf),c_char_p(data))
    def pack(self, fmt, *data):
        j = 0
        for i in fmt:
            func = self.packfmt[i]
            func(data[j])
            j += 1
        return
    def unpackU8(self):
        data = c_byte(0)
        self.hDll.JdwpUnpackU1(byref(self.buf),byref(data))
        return data.value
    def unpackU16(self):
        data = c_short(0)
        a = self.hDll.JdwpUnpackU2(byref(self.buf),byref(data))
        return data.value
    def unpackU32(self):
        data = c_int(0)
        a = self.hDll.JdwpUnpackU4(byref(self.buf),byref(data))
        return data.value
    def unpackU64(self):
        data = c_longlong(0)
        self.hDll.JdwpUnpackU8(byref(self.buf),byref(data))
        return data.value
    def unpackStr(self):
        size = c_int(0)
        strdata = c_char_p(None)
        self.hDll.JdwpUnPackString(byref(self.buf),byref(data),byref(strdata))
        return size,strdata
    def unpack(self,fmt):
        data = ()
        for i in fmt:
            func = self.unpackfmt[i]
            value = func()
            data.append(value)
        return data
    def unpack(self,fmt,data):
        retData = ()
        self.buf.data = c_void_p(data)
        for i in fmt:
            func = self.unpackfmt[i]
            value = func()
            data.append(value)
        return retData


    def clear(self):
        a = self.hDll.JdwpClearData(byref(self.buf))
'''

if __name__ == '__main__':
    buf = PyBuf()
    buf.packStr('abcdef')
    size,data = buf.unpackStr()
    print size
    print data