#coding=utf-8
import os,win32com.client,thread,time,random
from pydbg import *
import hashlib,shutil
from pydbg.defines import *
  
MAX_HTML_COUNT=1
WMI = win32com.client.GetObject('winmgmts:')
  
def random_str(randomlength=8):
    strValue = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789~!@#$%^&*()'
    length = len(chars) - 1
    for i in range(randomlength):
        strValue+=chars[random.randint(0, length)]
    return strValue
  
def buildDir():
    try:
        os.mkdir(os.path.abspath(os.path.dirname(__file__))+"\\Data")
    except:
        pass
    try:
        os.mkdir(os.path.abspath(os.path.dirname(__file__))+"\\Data\\Cases")
    except:
        pass
    try:
        os.mkdir(os.path.abspath(os.path.dirname(__file__))+"\\Data\\Crash")
    except:
        pass
  
  
def av(dbg):
    if dbg.dbg.u.Exception.dwFirstChance:
        return DBG_EXCEPTION_NOT_HANDLED
    h=hashlib.md5()
    h.update(dbg.disasm(dbg.context.Eip))
    if(os.path.exists(os.path.abspath(os.path.dirname(__file__))+"\\Data\\Crash\\"+h.hexdigest())):
        dbg.terminate_process()
        return DBG_EXCEPTION_NOT_HANDLED
    shutil.copytree(os.path.abspath(os.path.dirname(__file__))+"\\Data\\Cases",os.path.abspath(os.path.dirname(__file__))+"\\Data\\Crash\\"+h.hexdigest())#½«´ËÂÖ²âÊÔÀý¿½±´
  
def start_debugger(debugger, pid):
    try:
        debugger.set_callback(EXCEPTION_ACCESS_VIOLATION, av)
        debugger.attach(pid)
        debugger.debug_event_loop()
    except Exception as err:
        print err
  
def EnumerateProcesses(processName):
    processList = WMI.ExecQuery("SELECT * FROM Win32_Process where name = '%s'"%processName)
    return processList
  
def fuzz(crash_wait_time):
    kernel32 = windll.kernel32
    while 1:
        os.popen('taskkill.exe /im:iexplore.exe /f')
        os.popen('taskkill.exe /im:WerFault.exe /f')
        buildDir()
        generate()
        db=pydbg()
        kernel32.WinExec("C:\Program Files (x86)\Internet Explorer\iexplore.exe "+os.path.abspath(os.path.dirname(__file__))+"\\Data\\Cases\\0.html",6)
        for process in EnumerateProcesses("iexplore.exe"):
            thread.start_new_thread(start_debugger, (db,int(process.Handle)))
        time.sleep(crash_wait_time)

def generate():
    for i in range(0,MAX_HTML_COUNT):
        html="<!doctype html>\n\t<html>\n\t\t<HEAD></HEAD>\n"
        html+="\t<body>\n"
        html+="\t"+random_str(8)+"\n"
        html+="\t</body>\n\t</html>"
        f=open(os.path.abspath(os.path.dirname(__file__))+'\\Data\\Cases\\%d.html'%i,'w')
        f.write(html)
        f.close()

if __name__=="__main__":
    crash_wait_time = 0.1
    fuzz(crash_wait_time)