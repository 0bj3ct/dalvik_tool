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
                dict2["jni"] = result[3]
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

def jniparse_p(jni):
    strpar = ""
    sig = jni[0]
    if sig=="[":
        aLen,arrayName = jniparse_p(jni[1:])
        strpar += arrayName+"[]"
        return aLen+1,strpar
    elif sig=="B":
        return 1,"byte"
    elif sig=="C":
        return 1,"char"    
    elif sig=="L":
        nPos = jni[1:].index(';')
        substr = jni[1:nPos+1]
        return nPos+2,substr
    elif sig=="F":
        return 1,"float"
    elif sig=="D":
        return 1,"double"
    elif sig=="I":
        return 1,"int"
    elif sig=="J":
        return 1,"long"
    elif sig=="Z":
        return 1,"bool"

def jniparse(jni):
    strpar = "("
    nPos = jni.index(")")
    substr = jni[1:nPos]
    subLen = len(substr)
    cPos = 0
    #print "sublen :%d" % subLen 
    #print substr
    while cPos<subLen:
        #print "cPos :%d" % cPos
        jni_signature = substr[cPos]
        #print "jni_signature %s" % jni_signature
        cPos += 1
        if jni_signature=="[":
            strlen,strData = jniparse_p(substr[cPos:])
            strpar += strData+"[]"
            cPos += strlen
        elif jni_signature=="B":
            strpar += "byte"
        elif jni_signature=="C":
            strpar += "char"   
        elif jni_signature=="L":
            nPos = substr[cPos:].index(';')
            clsstr = substr[cPos:cPos+nPos]
            cPos += len(clsstr)+1
            strpar += clsstr   
        elif jni_signature=="F":
            strpar += "float" 
        elif jni_signature=="D":
            strpar += "double" 
        elif jni_signature=="I":
            strpar += "int" 
        elif jni_signature=="J":
            strpar += "long" 
        elif jni_signature=="Z":
            strpar += "bool" 
        if cPos<subLen:
            strpar += ", "
    strpar += ")"
    return strpar
if __name__ == '__main__':
    strpar = jniparse("([Ljava/lang/long;IF)I")
    print strpar