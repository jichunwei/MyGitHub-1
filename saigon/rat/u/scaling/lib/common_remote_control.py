'''
Created on Aug 30, 2010
updated at: Oct 18,2010
@author: webber.lin
'''
import os
import logging
import time
from pprint import pformat
import subprocess
from RuckusAutoTest.components.LinuxPC import LinuxPC as LP

PORT='22' #telnet

def control_FM_Action(fm_obj,iso,action):
    ''' fm_obj: to control fm object
        iso: fm iso name
        action: 'backup', 'restore', 'install', 'uninstall'
    '''
    try:
        fm_obj.login()
        cmd_text_list = ['cd /tmp','python auto_install_FM.py %s %s' % (iso,action)]
        for cmd in cmd_text_list:
            print "[info] Command: %s" % cmd
            fm_obj.do_cmd(cmd)
            time.sleep(3)
            if action in ['backup','restore']:
                res = dict(result='PASS', message='%s FM database successfully' % action)
            else:
                res = dict(result='PASS',message='%s FM successfully' % action)
    except Exception, e:
        if action in ['backup','restore']:
            res = dict(
                       result='ERROR', message='Cannot %s FM database\nError: %s' % (action,e.__str__())
                       )
        else:
            res = dict(
                       result='ERROR', message='Cannot %s FM\nError: %s' % (action,e.__str__())
                       )
    return res


def restoreFMDB(fm_obj,iso):
    ''' This method is telnet to FM and restore db remotely on FM server
        After telnet to FM, run the below command:
        python auto_install_FM.py FM_9.0.0.0.126.20100719_0004.iso restore
    '''
    return control_FM_Action(fm_obj,iso,'restore')

def backupFMDB(fm_obj,iso):
    ''' This method is telnet to FM and restore db remotely on FM server
        After telnet to FM, run the below command:
        python auto_install_FM.py FM_9.0.0.0.126.20100719_0004.iso backup
    '''
    return control_FM_Action(fm_obj,iso,'backup')
    

def installFM(fm_obj,iso):
    ''' This method is telnet to FM and restore db remotely on FM server
        After telnet to FM, run the below command:
        python auto_install_FM.py FM_9.0.0.0.126.20100719_0004.iso install
    '''
    return control_FM_Action(fm_obj,iso,'install')
    

def uninstallFM(fm_obj,iso):
    ''' This method is telnet to FM and restore db remotely on FM server
        After telnet to FM, run the below command:
        python auto_install_FM.py FM_9.0.0.0.126.20100719_0004.iso uninstall
    '''
    return control_FM_Action(fm_obj,iso,'uninstall')
    

def pingFM(fm_ip='192.168.30.252'):
    '''Make sure FM is pingable and alive!!'''
    try:
        err=os.system("ping %s" % fm_ip)
        #status:
        # ping success: 0
        # ping failed: 1
        # ping unknown: 1
        return err
    except:
        logging.error('Failed: ping FM server')    

def createLinuxPc(ip_addr='192.168.30.252',user='lab',password='lab4man1'):
    ''' telnet to FM server'''
    return LP(dict(ip_addr=ip_addr,user=user,password=password))

def rebootLinuxPc(fm_term):
    try:
        res = fm_term.do_cmd('reboot')
        return res
    except:
        return "[Error] reboot Linux Pc doesn't work"
def loginLinuxPc(fm_term):
    try:
        fm_term.login(asRoot = True)
        logging.info('login as Root successfully')
    except:
        logging.error("login as Root failed")    
def restartFMserver(fm_term):
    try:
        res = fm_term.do_cmd('cd /opt/FlexMaster;./restart.sh')
        return res
    except:
        return "[Error] Restart FM server via restart.sh failed"
            
    
def checkFMIso(isoname,fm_ip):
    ''' Ensure Iso is already moved to /tmp'''
    fm = createLinuxPc(ip_addr=fm_ip)
    try:
        
        cmd = 'ls /tmp/%s' % isoname
        fm.do_cmd(cmd)
        res = dict(iso_message='iso: %s is existed' % isoname, fm_obj=fm)
    except Exception, e:
        res = dict(iso_message='iso: %s is not existed and Error: %s' %(isoname,e.__str__()),fm_obj=fm)
    return res    


def remoteCopyToAll(machineList=range(9,10),source='172.17.19.201',filePath=''):
    ''' copy configuration files to each test engine'''
    #Exmaple by batch file
    #FOR %%A IN (08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27) 
    #DO rcp \\172.17.19.201\saigon_49863\rat\u\fm\scaling\te_information\*
    # \\172.17.19.2%%A\saigon_49863\rat\u\fm\scaling\te_information\
    try:
        for i in machineList:
            if i < 10:
                target_ip = '172.17.19.20%s' % i
            else:
                target_ip = '172.17.19.2%s' % i
            print "[info] Copy files to Machine: %s IP: %s" % (i,target_ip)
            remoteCopy(source,target_ip,filePath)
    except:
        print "[Error] remoteCopyToAll failed"


def remoteCopy(source='172.17.19.201',target='172.17.19.202',folder=''):
    try:
        if folder == '':
            folder = r'saigon_49863\rat\u\fm\scaling\te_information'
        cmd = r'rcp \\%s\%s\* \\%s\%s' % (source,folder,target,folder)
        print "[debug] %s" % cmd
        os.system(cmd)
        print "[Info] remote copy files from %s to %s successfully" % (source,target)
    except:
        print "[error] remote copy files failed"


def scpBuildfromTEtoFM(kwa):
    
    config=dict(session='FM',\
                winscp=r'"\Documents and Settings\lab\Desktop\WinSCP.com"', \
                source=r'abc.iso',\
                source_dir=r'Integration\demo_saigon_56496\firmwares\fm_iso',\
                target_dir=r'/tmp/',\
                username='root',\
                password='lab4man1',\
                ip_addr=r'192.168.30.252',\
                hostkey=r'',)
    config.update(kwa)
    
    ''' 
        
        example of winscp.com:
        C:\Integration\demo_saigon_56496\firmwares\fm_iso>winscp.com /command "open ""root:lab4man1@192.168.30.252""" "cd ""/home/lab""" "put ""b.test""" "bye"
        
        Searching for host...
        Connecting to host...
        Authenticating...
        Using username "root".
        Authenticating with pre-entered password.
        Authenticated.
        Starting the session...
        Reading remote directory...
        Session started.
        Active session: [1] root@192.168.30.252
        /home/lab
        b.test                    |          0 KiB |    0.0 KiB/s | binary | 100%
        
        example2 of winscp.com:
        1. copy portable winscp.exe and winscp.com to the directory (c:\rat\)
        
        C:\Integration\demo_saigon_56496>winscp.com /command "open ""root:lab4man1@192.168.30.252""" "cd ""/home/lab""" "put ""runlog\Ruckus_db_091610_16_48.bak""" "bye"
        
        example3 of winscp.com: abs path
        C:\Integration\demo_saigon_56496>"\Documents and Settings\lab\Desktop\WinSCP.com" /command "open ""root:lab4man1@192.168.30.252""" "cd ""/home/lab""" "put ""runlog\Ruckus_db_091610_16_48.bak""" "bye"
        Searching for host...
        Connecting to host...
        Authenticating...
        Using username "root".
        Authenticating with pre-entered password.
        Authenticated.
        Starting the session...
        Reading remote directory...
        Session started.
        Active session: [1] root@192.168.30.252
        /home/lab
        Ruckus_db_091610_16_48.ba |         46 KiB |    0.0 KiB/s | binary | 100%
        
    '''
    
        
    source_path=r'%s\%s' %(config['source_dir'],config['source'])
    
    #/hostkey="ssh-rsa 1024 xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx"
    #ssh-rsa 2048 16:83:a4:96:31:04:39:c2:c5:3a:53:55:6c:05:df:6a
    
    cmd = _assembleWinScpCmd(winscp=config['winscp'],ip_addr=config['ip_addr'],\
                       source_path=source_path,\
                       target_dir=config['target_dir'],
                       user=config['username'],
                       password=config['password'],hostkey=config['hostkey'])
    
    logging.info( "CMD: %s" % cmd)
    try:
        #os.system(r'%s' % cmd) #os.system is not smart enough to deal with space on windows
        subprocess.call(cmd)
        logging.info( "Copy FM build from Test Engine to FM server successfully:\n%s" % (pformat(config)))
        res = dict(
                   result='PASS', message='Secure Copy FM build successfully'
                   )
    except Exception, e:
        logging.error( "remote copy file(%s) failed" % file)
        res = dict(
                       result='ERROR', message='Cannot secure copy FM\nError: %s' % (e.__str__())
                       )
        
    #cmd = r'"\Documents and Settings\lab\Desktop\WinSCP.com" /command "open ""lab:lab4man1@192.168.30.252""" "cd ""/tmp""" "put ""Integration\demo_saigon_56496\firmwares\fm_isoFM_9.0.0.0.155.iso""" "bye"'   
   
    return res

def _assembleWinScpCmd(winscp=r'',ip_addr='',source_path='',target_dir='',user='',password='',hostkey=''):
    '''
    this protected function is only for scpBuildFromTetoFM()
    
    example3 of winscp.com: abs path
    "\Documents and Settings\lab\Desktop\WinSCP.com" /command "open ""root:lab4man1@192.168.30.252""" "cd ""/home/lab""" "put ""runlog\Ruckus_db_091610_16_48.bak""" "bye"
    '''
    # some machine require ssh-rsa finger print
    if hostkey =='':
        winScp=r'%s /command "open ""%s:%s@%s""" "cd ""%s""" "put ""%s""" "bye"' % (winscp,user,password,ip_addr,target_dir,source_path)
    else:
        winScp=r'%s /command "open ""%s:%s@%s"" -hostkey=""%s""" "cd ""%s""" "put ""%s""" "bye"' % (winscp,user,password,ip_addr,hostkey,target_dir,source_path)
    print "Assemble WinSCP Command:\n%s" % winScp
    return winScp


def mergeLogFile(files_need_to_be_merge=[]):        
    pass
    
if __name__ == '__main__':
    pass
    #remoteCopyToAll()




