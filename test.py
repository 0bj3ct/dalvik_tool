import jpype
import os
jvmPath = jpype.getDefaultJVMPath()
ext_classpath = r"jar/jadx-core-0.5.2.jar;jar/android-4.3.jar;jar/dx-1.8.jar;jar/slf4j-api-1.7.7.jar"
jvmArg = "-Djava.class.path=" + ext_classpath
jpype.startJVM(jvmPath,"-ea",jvmArg)
jadx = jpype.JPackage("jadx").api.JadxDecompiler()
File = jpype.JClass('java.io.File')
inFile = File('F:\\test22\\classes.dex')
jadx.loadFile(inFile)
clss = jadx.getClasses()
jprint = jpype.java.lang.System.out.println
for cls in clss:
    clsName = cls.getFullName()
    #if cmp(clsName,'com.example.debugapp.MainActivity') == 0:
    if cmp(cls.getPackage(),'com.droider.crackme0201') == 0:
        code = cls.getCode()
        print code
        #meths = cls.getMethods()
        #for meth in meths:
            #name = meth.getName()
            #args = meth.getArguments()
            #print args
            #if cmp(name,'testfun') == 0:
                #args = meth.getArguments()
                #line = meth.getDecompiledLine()
                #print line
jpype.shutdownJVM()
