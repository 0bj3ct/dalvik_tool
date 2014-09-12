import jpype
import os
jvmPath = jpype.getDefaultJVMPath()
ext_classpath = r"jadx-core-0.5.2.jar;android-4.3.jar;dx-1.8.jar;slf4j-api-1.7.7.jar"
jvmArg = "-Djava.class.path=" + ext_classpath
jpype.startJVM(jvmPath,"-ea",jvmArg)
jadx = jpype.JPackage("jadx").api.JadxDecompiler()
File = jpype.JClass('java.io.File')
inFile = File('F:\\classes.dex')
jadx.loadFile(inFile)
clss = jadx.getClasses()
jprint = jpype.java.lang.System.out.println
for cls in clss:
    clsName = cls.getFullName()
    #if cmp(clsName,'com.example.debugapp.MainActivity') == 0:
    if cmp(cls.getPackage(),'com.example.debugapp') == 0:
        meths = cls.getMethods()
        for meth in meths:
            name = meth.getName()
            args = meth.getArguments()
            print args
            #if cmp(name,'testfun') == 0:
                #args = meth.getArguments()
                #line = meth.getDecompiledLine()
                #print line
jpype.shutdownJVM()
