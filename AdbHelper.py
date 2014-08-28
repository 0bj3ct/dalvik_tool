# -*- coding: utf-8 -*-
#file: JdwpHandle.py
#author: object
#description: Jdwp协议操作

import subprocess, threading, os, os.path
import re

RE_INT = re.compile('^[0-9]+$')

from cStringIO import StringIO

class ShellException( Exception ):
    def __init__( self, command, output, status ):
        self.command = command
        self.output = output
        self.status = status

def printout( prefix, data ):
    data = data.rstrip()
    if not data: return ''
    print prefix + data.replace( '\n', '\n' + prefix )

#创建一个进程，去执行一个指定的command
def sh( command, no_echo=True, no_fail=False, no_wait=False ):
    if not no_echo: 
        printout( '>>> ', repr( command ) )

    process = subprocess.Popen( 
        command,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        stdin = None,
        shell = True if isinstance( command, str ) else False
    )
    
    if no_wait: return process

    output, _ = process.communicate( )
    status = process.returncode
    #print "status=" + str(status)
    if status: 
        if not no_echo: printout( '!!! ', output )
        if not no_fail: raise ShellException( command, output, status )
    else:
        if not no_echo: printout( '::: ', output )

    return output

def ShellIO( command):
    '''
    临时增加以便解决多次输入的问题
    '''
    print "begin"
    process = subprocess.Popen( 
        command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        stdin = subprocess.PIPE,
        shell = True if isinstance( command, str ) else False
    )
    
    print "end"
    return process

def which( utility ):
    for path in os.environ['PATH'].split( os.pathsep ):
        path = os.path.expanduser( os.path.join( path, utility ) )
        if os.path.exists( path ):
            return path

def test( command, no_echo=False ):
    process = subprocess.Popen( 
        command,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        stdin = None,
        shell = True if isinstance( command, str ) else False
    )
    
    output, _ = process.communicate( )
    return process.returncode

def cat(*seqs):
    for seq in seqs:
        for item in seq:
            yield item

def seq(*args):
    return args

def adb(*args):
    try:
        return sh(seq("adb", *args))
    except OSError as err:
        raise ConfigError('could not find "adb" from the Android SDK in your PATH')

#函数用于获得设备信息，使用命令"adb devices"来获得
def find_dev(dev=None):
    'determines the device for the command based on dev'
    if dev:
		#当dev不为空时，检验dev中是否是devices值
        if dev not in map( 
            lambda x: x.split()[0], 
            adb('devices').splitlines()[1:-1]
        ):
            raise OptionError('device serial number not online')
    else:
		#当dev为空时，获取devices的值后保存到dev中
        lines = adb('devices').splitlines()
        if len(lines) != 3:
            raise OptionError(
                'you must specify a device serial unless there is only'
                ' one online'
            )
        dev = lines[1].split()[0]   
    return dev

#获得进程id的值，执行“adb shell ps” 命令
def find_pid(pid, dev=None):
    '''determines the process id for the command based on dev, pid and/or name
    返回值：如果在虚拟机中找到返回pid的值，如果没有找到返回None
    '''

    ps = ('-s', dev, 'shell', 'ps') if dev else ('shell', 'ps') 
    ps = adb(*ps)
    ps = ps.splitlines()
    head = ps[0]
    x = 0
    for name in head.split():
        if name == 'PID':
            break;
        x += 1
    find = False
    for p in ps[1:]:
    	#print p
        data = p.split()
        if len(data)>=x and data[x] == str(pid):
            find = True
            break;
    if find:
        return pid
    else:
        return None

def cur_file_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，
    #如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

if __name__ == '__main__':
    print find_pid(30067)