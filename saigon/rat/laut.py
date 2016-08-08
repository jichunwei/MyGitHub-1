"""
laut.py (Launch Testbuild, QA Test Runner) allows user to telnet laut to launch
testbuild.py to execute a specific testbed/buildstream/buildno build that is
defined in the RAT's AutotestConfig record.

Examples to ask to test build number 18 of ZD3000_7.1.1.0_production:

Telent to the laut server, say it is at 172.16.22.98

telnet 172.16.22.98 10880
HI ('192.168.0.22', 35205)
Command# dev ZD3000_7.1.1.0_production 18 debug=True
Command# pp
Command# exit

Tea Program Example
Command# tea u.fm.multi_user_login 172.17.18.31 9 1 1

command example:
command# rcp 172.17.19.201 saigon_49863\rat * .\test
"""

#Jacky.Luh updated the script on 2013-1-23

_LAUT_VERSION = '1.0.0.1'
from SocketServer import ThreadingTCPServer, StreamRequestHandler
import time
import os
import sys
import copy
import pprint
import re
import traceback
import subprocess as sp
import threading
from RuckusAutoTest.common.lib_KwList import *

from ratenv import *
from RuckusAutoTest import models as DB
from RuckusAutoTest.components import clean_up_rat_env
import pdb


try:
    laut['tm_init'] = time.time()
    laut['flag']=False
except:
    laut = dict(tm_init=time.time(), qarun=None, cmd_list=[], exec_cmd = ['', '', ('', '')])
    laut['flag']=False

laut['laut.pid'] = os.getpid()
os.environ['LAUT_SIGNATURE'] = 'rat_at_%s_pid_%d' % (str(laut['tm_init']), laut['laut.pid'])

CurrClient = {'init': time.time()}
_one_user_only = r"SORRY %s. I only serve one client a time. Login later. Thanks.\r\n"

def startLaut(tbname, **kwargs):
    global laut
    laut['tbname'] = tbname
    tcfg = dict(port=10880)
    tcfg.update(kwargs)
    if tcfg.has_key('debug') and tcfg['debug']: pdb.set_trace()
    if tcfg.has_key('h') or tcfg.has_key('help'):
        pprint.pprint(tcfg)
        return
  
    msg = "Launch build test service [version %s] [pid %s] at port %s on logical testbed name %s" \
        % ( str(_LAUT_VERSION), str(laut['laut.pid']), str(tcfg['port']), laut['tbname'])
    dln = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dln, msg, dln)
    laut['server'] = ThreadingTCPServer(('', int(tcfg['port'])), LautServiceHandler)
    laut['server'].serve_forever()

def stopLaut():
    global laut
    if laut['server']:
        laut['server'].server_close()
        laut['server'] = None
def startScalingTE(te_ip_address,tea_module,fm_ip_address,fm_version,te_id,duration,**kwargs):
    """
    date:07/08/2010
    To start tea program on test engine remotely
    1. Start laut server on test engine
    2. log in to laut server from controller via telnet
    3. Start tea program automatically if testbed name == 'tea'
    This function saves a lot of time to start many machines at a time.
    ex:
    tea.py u.fm.multi_user_log_in fm_ip_addr=172.17.18.31 fm_version=9 te_id=2 day=3
    [args]
    te_ip_address: test engine ip address (172.17.19.201), and it is caught by socket
    tea_module: ex:  u.XXX.XX.XX
    fm_ip_address: fm server ip address
    fm_version: usually it's 9
    te_id: test engine id: ex: ip_addr: 172.17.19.201 then te_id=1
    duration: Usually duration is 3 days
    
    EX:
    Command# tea u.fm.multi_user_log_in 172.17.18.31 9 1 1
    
    """

    #date:7/22/2010
    #set keyword arguments for phase II enhancement
    #tcfg = dict(te_ip_address='172.17.19.201', tea_module='u.fm.multi_user_log_in',\
    #            fm_ip_address='172.17.18.31',fm_version='9',te_id='1',duration='1')
    #tcfg.update(kwargs)
    #[DOS start command] Enables a user to start a separate window in Windows from the Windows command line.
    #title is the name for the opened window 
    #date:7/22/2010
    #title = 'tea.py %s fm_ip_addr=%s fm_version=%s te_id=%s day=%s' \
    #        % (tcfg['tea_module'],tcfg['fm_ip_address'], tcfg['fm_version'],tcfg['te_id'],tcfg['duration'])
    global laut
    title = 'tea.py %s fm_ip_addr=%s fm_version=%s te_id=%s day=%s' \
            % (tea_module,fm_ip_address,fm_version,te_id,duration)
    tea= os.path.join(os.getcwd(),'tea.py')
    
    #,
    
    #Comments:
    #cmd need to be enhanced
    #engineer: Webber Lin
    #With Variables
    cmd = 'start "%s" python %s %s fm_ip_addr=%s fm_version=%d te_id=%d day=%d ' % (title, tea, tea_module\
                                                                                    ,fm_ip_address,\
                                                                                    int(fm_version)\
                                                                                    ,int(te_id)\
                                                                                    ,int(duration))  

    #With Dictionary
    #cmd = 'start "%s" python %s %s fm_ip_addr=%s fm_version=%d te_id=%d day=%d ' % (title, tea, tcfg['tea_module']\
    #                                                                                ,tcfg['fm_ip_address'],\
    #                                                                                int(tcfg['fm_version'])\
    #                                                                                ,int(tcfg['te_id'])\
    #                                                                                ,int(tcfg['duration']))  

    print "Lauch Command: %s" % cmd
    
    #With Dictionary
    #if not (tcfg['tea_module'], tcfg['fm_ip_address'],tcfg['fm_version'],tcfg['te_id'],tcfg['duration']):
    #With Var
    if not (tea_module, fm_ip_address,fm_version,te_id,duration):
        laut['tea'] = None
        return None
    laut['command'] = cmd
    laut['testrunner.start'] = int(time.time())
    
    try:
        #laut['tea'] = TestBuild(tcfg['te_ip_address'],cmd)
        print "[info] Start Selenium"
        laut['tea'] = TestBuild(te_ip_address,cmd)
        laut['tea'].start()
        time.sleep(5)
        return laut['tea']
    except:
        # run c:\bin\win\pskill java 
        sp.call(r'c:\bin\win\pskill java')
        time.sleep(120)
    return None        
    
    
def startTestRunner(client_address, tbname, bstream, bno, cmdopts):
    #Update by cwang@20130607 for release testing limitation.
#    if bstream.split("_")[1] not in ["9.7.0.0",'0.0.0.99']:
#       print "The build stream %s not in range ['9.7.0.0', '0.0.0.99'], please check." % bstream
#       return None
    #JLIN@20100415 change testbuild.py to qarun.py
    global laut
    title = 'qarun.py %s %s bno=%d %s' % ( bstream, tbname, int(bno), cmdopts)
        
    #CWANG@20100623 append file path
    qarun = os.path.join(os.getcwd(), 'qarun.py')
    cmd = 'start "%s" python %s %s %s bno=%d %s' % (title, qarun, bstream, tbname, int(bno), cmdopts)  
#    cmd = 'start "%s" python qarun.py %s %s bno=%d %s' % (title, bstream, tbname, int(bno), cmdopts)
    print "Lauch command: %s" % cmd
    
    
    if not bno:
        laut['qarun'] = None
        return None
    laut['command'] = cmd
    laut['testrunner.start'] = int(time.time())
    while (int(time.time()) - laut['testrunner.start'] < 7*60):
        try:
            laut['qarun'] = TestBuild(client_address,cmd)
            laut['qarun'].start()
            time.sleep(5)
            return laut['qarun']
        except:
            # run c:\bin\win\pskill java 
            sp.call(r'c:\bin\win\pskill java')
            time.sleep(120)
    return None

def noneQARunner():
    global laut
    try:
        del(laut['qarun'])
    except:
        pass
    laut['qarun'] = None
def noneTEARunner():
    global laut
    try:
        del(laut['tea'])
    except:
        pass
    laut['tea'] = None
    
def processBuildRequest(client_address, who, cmdstr):
    global laut
    laut['cmdstr'] = cmdstr
    tea = None
    qarun = None
    if laut['qarun'] and not laut['qarun'].isDone():
        return ('NORESOURCE', 'There is a build test running: %s' % laut['qarun'].command)

    testbuildRemovePidFile()
    noneQARunner()
    noneTEARunner()
    
    if re.match('dev', who, re.I):
        qarun = processDevTestRunner(client_address, cmdstr)
    #tea program enhancement
    elif re.match('tea',who,re.I):
        tea = processTeaTestRunner(client_address, cmdstr)
    else:
        qarun = processQaTestRunner(client_address, cmdstr)
    
    if not tea and not qarun:
        return ('BAD', 'Incompleted command, expect: "DEV <buildstream> <buildno>" or "QA <testbed> <buildstream> <buildno>"')
    else:
        if tea:
            return ('OK', 'TEA program launch command: %s' % laut['tea'].command) 
        elif qarun:
            return ('OK', 'Build test launch command: %s' % laut['qarun'].command)
        else:
            return ('Wrong', 'it could be something wrong here')

def processTeaTestRunner(te_ip_address, cmdstr):
    '''
    date:07/08/2010
    update: 07/22/2010
    '''
    global laut
    #For Variables
    m = re.match(r'\s*([^\s]+)\s*([^\s]+)\s+(\d+)\s+(\d+)\s+(\d+)', cmdstr)
    #for Dict
    #m = re.match(r'\s*\w+=([^\s]+)\s+\w+=([^\s]+)\s+\w+=(\d+)\s+\w+=(\d+)\s+\w+=(\d+)', cmdstr)
    #tcfg['tea_module'],tcfg['fm_ip_address'], tcfg['fm_version'],tcfg['te_id'],tcfg['duration']
    
    if m:
        tea = startScalingTE(te_ip_address, m.group(1),m.group(2),m.group(3),m.group(4),m.group(5))
        #startScalingTE(te_ip_address, tea_module, fm_ip_address,fm_version,te_id,duration)
        return tea
    print "TEA: bad command: %s" % cmdstr
    return None
def processRcpRunner(te_ip_address, cmdstr):
    '''
    date:07/26/2010
    
    '''
    global laut
    #For Variables
    m = re.match(r'\s*([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)', cmdstr)
    # group1 to group4 
    #copyTeaFiles(source_ip,source_file_path,file,target_file_path)
    
    if m:
        tea = copyTeaFiles(te_ip_address, m.group(1),m.group(2),m.group(3),m.group(4))
        #startScalingTE(te_ip_address, tea_module, fm_ip_address,fm_version,te_id,duration)
        return tea
    print "TEA: bad command: %s" % cmdstr
    return None

def processDevTestRunner(client_address, cmdstr):
    # m = re.match(r'\s*([^\s]+)\s+(\d+)(|\s+(.*))', cmdstr)
    global laut
    m = re.match(r'\s*([^\s]+)\s+(\d+)(.*)', cmdstr)
    if m:
        if laut.has_key('bstream'):
            if laut.get('btream') == m.group(1) and laut.get('bno') == m.group(2):
                laut['flag'] = True
            else:
                laut['flag'] = False
                
        laut['bstream'] = m.group(1)
        laut['bno'] = int(m.group(2))        
        
        qarun = startTestRunner(client_address, laut['tbname'], m.group(1), m.group(2), m.group(3))
        for qarun_pid in laut['cmd_list']:
            list_id = 0
            if laut['cmd_list'][list_id][0] == ('dev ' + str(cmdstr)) and laut['cmd_list'][list_id][2] == client_address:
                laut['cmd_list'][list_id][1] = laut['qarun.pid']
            list_id += 1
        return qarun
    print "DEV: bad command: %s" % cmdstr
    return None

def processQaTestRunner(client_address, cmdstr):
    # m = re.match(r'\s*([^\s]+)\s*([^\s]+)\s+(\d+)(|\s+(.*))', cmdstr)
    global laut
    m = re.match(r'\s*([^\s]+)\s*([^\s]+)\s+(\d+)(.*)', cmdstr)
    if m:
        qarun = startTestRunner(client_address, m.group(1), m.group(2), m.group(3), m.group(4))
        return qarun
    print "QA: bad command: %s" % cmdstr
    return None

def mojoOutput(output):
    output = output.replace('\n', '\r\n')
    return output
 
def stepIntoDebug():
    print "\n--- Debugging? --"
    pdb.set_trace()
#date: 7/26/2010
#added by: Webber Lin
def delTeaDirectory(target_file_path):
    
    try:
        cmd = 'rmdir %s /s /q' % target_file_path
        print "Delete old files and wait for 10 seconds........"
        sp.call(cmd)
        time.sleep(10)
    except:
        print "subprocess delete function error"
    

    
def copyTeaFiles(te_ip_address,source_ip,source_file_path,file,target_file_path):
    ''' copy files from controller to other testengines
        1. implemented in laut.py
        2. get updated files from controller
        3. Save time to copy files.
        example:
        C:\> rcp -r \\172.17.19.201\saigon_49863\rat\laut.py .
        output: \\172.17.19.201\saigon_49863\rat\laut.py
                1 File(s) copied
            
    '''
    
    cmd = r'rcp \\%s\%s\%s %s' % (source_ip,source_file_path,file,target_file_path)
    #command example:
    #command# rcp 172.17.19.201 saigon_49863\rat * .\test
    try:
        #delTeaDirectory(target_file_path)
        print "Copying files...."
        print "Lauch Command: %s" % cmd
        sp.call(cmd)
        time.sleep(5)
        print "Copied files..Success!!"
        
    except:
        print "Copy files ...failed!!"
    return None


class QARunner(threading.Thread):
    '''
    QARun executor
    '''               
    def __init__(self):
        global laut        
        threading.Thread.__init__(self)        
        self.lock = threading.Lock()        
        
           
    def run(self):
        global laut
        while True:
            tbname,bstream,bno='', '', ''
            if laut['qarun'] == None and laut['cmd_list']:
               laut['exec_cmd'] = copy.deepcopy(laut['cmd_list'][0])
               del laut['cmd_list'][0]
               m = re.match(r'^(QA|DEV|TEA)\s{1,2}(ZD\d{4,5}\_(\d+\.){3}\d+\_(production|Mainline)\s{1,2}\d+\s{0,2}(.*))$', laut['exec_cmd'][0], re.I)

               (status, mesg) = processBuildRequest(laut['exec_cmd'][2], m.group(1), m.group(2))
               q = re.match(r'\s*([^\s]+)\s+(\d+)(.*)', m.group(2))                            
               print '%s: %s\r\nCommand# ' % (status, mesg)
            if laut['qarun'] and laut['qarun'].isDone() and laut['flag']:
                #Re-check if current build run successfully.
                obj= None
                bno = laut.get('bno', 0)
                bstream = laut.get('bstream')
                tbname = laut.get('tbname')
                try:
                    print 'build number:%d' % bno
                    obj = DB.Batch.objects.filter(testbed__name=tbname, 
                        build__build_stream__name=bstream, 
                        build__number=bno)
                except:
                    traceback.print_exc()
                    
                if obj:
                    obj=obj[0]
                    #Test Pass is None, it means that all of test cases are not RUN.           
                    if obj.tests_pass:
                        del laut['cmd_list'][0]
                        print 'This build have been tested successfully.'
                else:
                    print "Doesn't found it about this build number"       

            if laut['qarun'] and laut['qarun'].isDone() and laut['cmd_list']:
               laut['exec_cmd'] = laut['cmd_list'][0]               
               m = re.match(r'^(QA|DEV|TEA)\s{1,2}(ZD\d{4,5}\_(\d+\.){3}\d+\_(production|Mainline)\s{1,2}\d+\s{0,2}(.*))$', laut['exec_cmd'][0], re.I)
               (status, mesg) = processBuildRequest(laut['exec_cmd'][2], m.group(1), m.group(2))
               print '%s: %s\r\nCommand# ' % (status, mesg)
               
            if laut['cmd_list'] == [] and laut['exec_cmd'] == ['', '', ('', '')]:
                if laut['qarun'] == None:
                    break
                if laut['qarun'] and laut['qarun'].isDone():
                    break
            
#            print 'qarun %s, qarun is DONE %s' % (laut['qarun'], laut['qarun'].isDone()) 
            #time.sleep(12)


class LautServiceHandler(StreamRequestHandler):

    def setup(self):
        global laut
        StreamRequestHandler.setup(self)
        print self.client_address, 'connected'
        CurrClient[self.client_address] = time.time()
        self.request.send('HI ' + str(self.client_address) + '\r\nCommand# ') 
        self.inbuf = ''

    def handle(self):
        global laut
        while True:
            #Jacky.Luh updated by 2012-06-12
            global laut
            e_cmd = self.rfile.readline().strip()
            m = re.match(r'^(QA|qa|DEV|dev|TEA|tea)\s+([a-zA-Z]+\d+)\s*_{,1}(([0-9]\.){3}\d+)\s*_{,1}(Mainline|production)\s+\d+', e_cmd)
            if len(e_cmd) == 0:
                self.wfile.write('\rCommand# ')
            else:
                if m:
                    laut['cmd_list'].append([e_cmd, '', self.client_address])
                      
                if e_cmd == "p":
                    self.wfile.write('INFO: %s\r\nCommand# ' % str(laut))
                    import pprint
                    pprint.pprint(laut)
                elif e_cmd == "pp":
                    result = mojoOutput(pprint.pformat(laut))
                    self.wfile.write('INFO:\r\n%s\r\nCommand# ' % result)
                    print result
                elif e_cmd == "KiLL":
                    self.wfile.write("KILLED!")
                    (status, msg) = killTestBuildProcess()
                    # should be killed already
                    return
                elif re.match('^(rcp)\s+(.*)', e_cmd, re.I):
                    #date: 7/26/2010
                    #added by: Webber Lin
                    #command: remote copy
                    m = re.match('^(rcp)\s+(.*)', e_cmd, re.I)
                    self.wfile.write("remote sync tea program files")
                    (status, mesg) = processRcpRunner(self.client_address, m.group(2))
                    self.wfile.write('%s: %s\r\nCommand# ' % (status, mesg))
                    
                elif re.match('^(close|shutdown)$', e_cmd, re.I):
                    # not a correct solution
                    self.wfile.write('SHUTDOWN:')
                    laut['server'].server_close()
                    return
                elif re.match('^(exit|stop|quit|bye)', e_cmd, re.I):
                    self.wfile.write('BYE.BYE!')
                    break

                elif re.match('^debug$', e_cmd, re.I):
                    stepIntoDebug()       
                    #WLin edited at 07/08/2010        
                elif re.match(r'^(QA|qa|DEV|dev|TEA|tea)\s{1,2}(ZD\d{4,5}\_(\d+\.){3}\d+\_(production|Mainline)\s{1,2}\d+\s{0,2}(.*))$', e_cmd):
                    show_info_id = True                 
                    if laut['qarun'] == None:
                        laut['executor'] = QARunner()
                        laut['executor'].start()
                           
                    elif laut['qarun'] and laut['qarun'].isDone():
                        laut['executor'] = QARunner()
                        laut['executor'].start()
                
                    else:
                        if show_info_id:
                            self.wfile.write('Running: %s \r\n' % laut['exec_cmd'][0])
                            num = 1
                            for cml in laut['cmd_list']:
                                if cml[0] == laut['exec_cmd'][0]:
                                    continue
                                self.wfile.write('Wait to exec %d: %s \r\n' % (num, cml[0]))
                                num += 1
                            
                            show_info_id = False
                    time.sleep(1)
                    self.wfile.write('\rCommand# ')
                            
                elif e_cmd == "execlist":
                    if laut['qarun'] == None:
                        self.wfile.write('Not any build running \r\n')
                    elif laut['qarun'] and laut['qarun'].isDone():
                        self.wfile.write('Not any build running \r\n')
                    else:
                        try:
                            if laut['exec_cmd'][0]:
                                self.wfile.write('Running: %s \r\n' % laut['exec_cmd'][0])
                        except:
                            self.wfile.write('Not any build running \r\n')
                    num = 1
                    
                    if laut['cmd_list'] is not None:
                        for cml in laut['cmd_list']:
                            if cml[0] == laut['exec_cmd'][0]:
                                continue
                            self.wfile.write('Wait to exec %d: %s \r\n' % (num, cml[0]))
                            num += 1
                    self.wfile.write('\rCommand# ')
                elif re.match(r'^del\s+((QA|qa|DEV|dev|TEA|tea)\s+([a-zA-Z]+\d+)\s*_{,1}(([0-9]\.){3}\d+)\s*_{,1}(Mainline|production)\s+\d+)', e_cmd):
                    if re.match(r'^del\s+((QA|qa|DEV|dev|TEA|tea)\s+([a-zA-Z]+\d+)\s*_{,1}(([0-9]\.){3}\d+)\s*_{,1}(Mainline|production)\s+\d+)',\
                                 e_cmd).group(1).lower() == laut['exec_cmd'][0].lower():
                        killQarunProcess()
                        try:
                            if laut['cmd_list']:
                                laut['exec_cmd'] = laut['cmd_list'][0]
                        except:
                            pass
                        self.wfile.write('\rCommand# ')
                    else:
                        if laut['cmd_list'] is not None:
                            for cm in laut['cmd_list']:
                                if re.match(r'^del\s+((QA|qa|DEV|dev|TEA|tea)\s+([a-zA-Z]+\d+)\s*_{,1}(([0-9]\.){3}\d+)\s*_{,1}(Mainline|production)\s+\d+)',\
                                             e_cmd).group(1).lower() == cm[0].lower():
                                    laut['cmd_list'].remove(cm)
                                    self.wfile.write('%s: deleted successfully!\r\nCommand# ' % cm[0])  
                                else:
                                    self.wfile.write('HELP: %s\r\nINFO: Invalid command, or incorrected format.\r\nCommand# ' % e_cmd)                
                else:
                    self.wfile.write('HELP: %s\r\nINFO: Invalid command, or incorrected format.\r\nCommand# ' % e_cmd)
                

    def handleChar(self):
        while True:
            data = self.request.recv(2048)
            time.sleep(2)
            self.request.send('Got:\n%s\n? ' % data)
            self.inbuf += data
            if self.inbuf.startswith('stop'):
                return

    def finish(self):
        print self.client_address, 'disconnected!'
        self.request.send('BYE ' + str(self.client_address) + '\r\n') 
        del(CurrClient[self.client_address])
        StreamRequestHandler.finish(self)

LAUT_PID_FNAME = '_laut.pid'
def testbuildIsRunning():
    return os.path.exists(LAUT_PID_FNAME)

def testbuildCreatePidFile(pid):
    f = open(LAUT_PID_FNAME, "w")
    f.write("%s" % str(pid))
    f.close()

def testbuildRemovePidFile():
    # if pid of LAUT_PID_FNAME is running; don't delete the file
    try:
        os.remove(LAUT_PID_FNAME)
    except:
        pass
    
def killQarunProcess():
    global laut
    try:         
        clean_up_rat_env()
        pid = laut['qarun.pid']    
        printProcessInfo(pid)
        print "Is about to Kill qarun.pid %s" % str(pid)
        sp.call(r'c:\bin\win\pskill -t %s' % str(pid))
        sp.call(r'c:\bin\win\pskill java')
        sp.call(r'c:\bin\win\pskill firefox')
        time.sleep(10)
    except:
        import traceback
        traceback.print_exc()


def killTestBuildProcess():
    global laut
    print 'PERFORM killTestBuildProcess()'
    testbuildRemovePidFile()
    try:
        pid = os.getpid()
        printProcessInfo(pid)
        print "Is about to Kill myself.pid %s" % str(pid)
        sp.call(r'c:\bin\win\pskill -t %s' % str(pid))
    except:
        pass

def printProcessInfo(pid):
    global laut
    pipe = sp.Popen(r'c:\bin\win\pslist -t %s' % str(pid), shell=True, stdout=sp.PIPE)
    data = pipe.stdout.read()
    print data

def etimeStr(etime):
    sec = etime % 60
    min = int(etime / 60)
    if min > 60:
        hou = min / 60
        min = min % 60
        return "%d hours %d minutes %0.2f seconds" % (hou, min, sec)
    elif min > 0:
        return "%d minutes %0.2f seconds" % (min, sec)
    else:
        return "%0.2f seconds" % sec 

def timeList():
    curtime = time.localtime()
    return [time.asctime(curtime), time.strftime('%Y%m%d-%H%M%S', curtime), time.mktime(curtime), curtime]

# cmd = 'start "mesh.fanout Zd1000 bno=30" python testbuild.py mesh.fanout zd1000 bno=30 debug=True'
# ss = laut2.TestBuild(0, cmd)
# ss.start()
# ss.pid
# ss.isDone()
# del(ss)
class TestBuild(threading.Thread):
    tlock = threading.Lock()
    id = 0
    def __init__(self,client_address,start_cmd):
        global laut
        if testbuildIsRunning():
            raise Exception('There is one TestBuild processing running')
        threading.Thread.__init__(self)
        self.myid = TestBuild.id
        TestBuild.id += 1
        self.client_address = client_address
        self.command = start_cmd
        self.status = 0
        self.pid = -1
        laut['qarun.tm.00.start'] = timeList()
        print "Start TestBuild at %s" % (laut['qarun.tm.00.start'][1])

    def run(self):
        global laut
        self.pipe = sp.Popen(self.command, shell=True,
                             stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE)
        self.status = 1
        # well, this is not the PID of testbuild.py which is started up using START command
        # solution: testbuild.py should write its PID to LAUT_PID_FNAME
        laut['qarun.pid'] = self.pid = self.pipe.pid
        testbuildCreatePidFile(self.pid)

        # pipe.stdout.read() is blocked until program exit
        # This is not the best solution.
        self.data = self.pipe.stdout.read()
        self.status = 2
        laut['qarun.tm.01.end'] = timeList()
        print "Terminated TestBuild [pid %d] at %s" % (laut['qarun.pid'], laut['qarun.tm.01.end'][1])
        for cur_exec_tu in laut['cmd_list']:
            if cur_exec_tu == laut['exec_cmd']:
                laut['cmd_list'].remove(cur_exec_tu)
        laut['exec_cmd'] = ['', '', ('', '')]
        try:
            laut['qarun.tm.03.elapsed'] = etimeStr(laut['qarun.tm.01.end'][2] - laut['qarun.tm.00.start'][2])
            print "TestBuild [pid %d] lasts for %s" % laut['qarun.tm.03.elapsed']  
        except:
            pass

    def pid(self):
        return self.pid

    def isDone(self):
        return (self.status != 1)

    def __del__(self):
        laut['qarun.tm.01.end'] = timeList()
        print "Terminated TestBuild at %s" % (laut['qarun.tm.01.end'][1])

# Examples:
#
#   laut.py help
#   laut.py port=10333 debug=True
#
if __name__ == '__main__':
    from RuckusAutoTest.common.lib_KwList import *
    _dict = as_dict(sys.argv[2:])
    try:
        startLaut(sys.argv[1], **_dict)
    except:
        import traceback

        print "\n\n%s" % ('!' * 68)
        ex =  traceback.format_exc()
        print ex

