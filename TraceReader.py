# -*- coding: utf-8 -*-
#file: TraceReader.py
#author: object
#description: Andorid Trace文件解析

import sys
import struct
import string

def methodSplit(data,step):
    return [data[x:x+step] for x in range(0,len(data),step)]

def printHex(data,size):
    for i in range(0,size,16):
        for j in range(0,16):
            print "i=%d,j=%d,%x" %(i,j,ord(data[i+j]))
        #print "\n"
class TraceReader(object):
    def __init__(self,types,fileName):
        self.funcData = {}
        self.callInfo = []
        if types == 'f':
            self.fileName = fileName
            self.file_object = open(fileName,'rb')
            self._ParseFile()
            self.file_object.close()
            self.allData = self.file_object.read()
        else:
            self.allData = fileName
            self._ParseFile()
    def _ParseFile(self):
        start = False
        allData = self.allData
        pos = allData.find('SLOW')
        strData = allData[0:pos]
        for line in strData.split('\n'):
            if not line.find('*methods') == -1:
                start = True
                continue
            if not line.find('*end') == -1:
                start = False
            if start == True:
                dict2 = {}
                result = line.split('\t')
                methodId = string.atoi(result[0],16)
                self.funcData[methodId] = dict2
                dict2["class_name"] = result[1]
                dict2["method_name"] = result[2]
        hexData = allData[pos:]
        self._ParseDex(hexData)

    def _ParseDex(self,hexData):
        #parse header
        dictFunc = {}
        hexData = hexData[32:]
        pktSize = struct.calcsize('=hiii')
        methods = methodSplit(hexData,pktSize)
        for methodInfo in methods:
            tid,methodData,tTime,gTime=struct.unpack('=hiii',methodInfo)
            methodId = methodData & ~0x03
            methodAction = methodData & 0x03
            dictList = {}
            dictList["method_action"] = methodAction
            dictList["method_id"] = methodId
            self.callInfo.append(dictList)
        #printHex(hexData,100)



if __name__ == '__main__':
    trace = TraceReader('f',r'C:\698042338.trace')
    for meth in trace.callInfo:
        print meth