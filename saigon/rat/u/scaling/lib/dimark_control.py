#!/usr/bin/python 

'''

Enhancement: 

Nov 23,2010: Add System Memory check in testing cycle


Nov 19,2010: 2-tiers and 3-tiers dimark architecture

Nov 9,2010: event storm 

@author: Webber.lin
New added: syslog update

Created on Nov 2, 2010
@author: webber.lin

1.    Start scripts
2.    Login to each of 20 DimarkAP VMs 
3.    Cd /root/testApp
4.    Run CLI ./dmk_sys c assocstart -n 20 l 0 a  (lower case L and space and zero and dash and a)
5.    Wait for 60 minutes
6.    Run CLI ./dmk_sys c assocstop
7.    Wait for 60 minutes
8.    Do Loop for step 4 through step 7  6 times
9.    Allow the user to resubmit the scripts next day or on-demand 
10.    Allow only one user running this scripts, no other concurrent user allowed 

example of ssh code:

cmd    = "sudo /etc/rc.d/apache2 restart"
 
ssh    = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.17.18.40', username='root', password='')
stdin, stdout, stderr = ssh.exec_command(cmd)
stdin.write('secret\n')
stdin.flush()
print stdout.readlines()
ssh.close()

'''

#python pack
import paramiko as para

#python modules
import time
import os
import pdb
import logging
import sys
import inspect
import threading # to init dimark generator
import Queue

#ruckus python module
#from u.scaling.lib.syslog_client import syslog
from syslog_client import syslog
from system_infomation import MemUsage

import lib_KwList as kwlist #lib_Kwlist is moved to dimark controller as part of ratcontrol library

#logging format
#logging.basicConfig(
#                    level=logging.DEBUG,
#                    format='%(asctime)s %(levelname)-8s %(message)s',
#                    datefmt='%a, %d %b %Y %H:%M:%S',
#                    )

MYNAME = inspect.currentframe().f_code.co_filename

DimarkAP_LIST=['10.1.2.1','10.1.2.2','10.1.2.3','10.1.2.4',
         '10.1.2.11','10.1.2.12','10.1.2.13','10.1.2.14',
         '10.1.2.5','10.1.2.6','10.1.2.7','10.1.2.8',
         '10.1.2.15','10.1.2.16','10.1.2.17','10.1.2.18',
         '10.1.2.9','10.1.2.10','10.1.2.19','10.1.2.20',]
CLIENTS=5
HOURS=3600 # wait for 90 mins to verify both client association graphic and tables
CONFIG_TIME=300 # first time use (stop association time)20 minutes
COUNTS=6
FM_IP='172.17.18.31'
DIMARK_CONTROL='172.17.18.40'
SYSLOG_SERVER='172.17.19.201'
EVENT_LIST=['1 BOOT','0 BOOTSTRAP','2 PERIODIC','3 SCHEDULED',
       '4 VALUE CHANGE','5 KICKED','6 CONNECTION REQUEST',
       '7 TRANSFER COMPLETE','8 DIAGNOSTICS COMPLETE']
TIERS=3
MEMORY_CHECK=5
#debug/unit test mode:
#DimarkAP_LIST=['10.1.2.1','10.1.2.2','10.1.2.3','10.1.2.4']

EVENT_LIST=['1 BOOT',]

class dmkGenerator(threading.Thread):
    
    def __init__ ( self, obj,ip):
        self.dmkobj = obj
        self.dmkip = ip
        threading.Thread.__init__ ( self )
    
    def run(self):
        #init dimark generator
        stdout,stderr = executeCmd(self.dmkobj,cmd=self.initDimark())
        stdout.extend(stderr) 
        message = '%s' % (stdout)
        sendtoSyslog(message=message,source_ip=self.dmkip)
            
    def initDimark(self):
        cmd = r'cd /root/testApp/;./dmk_init -c init.conf < /dev/null > /dev/null 2>&1 &'
        print cmd
        return cmd
    def killDimarkAP(self):
        cmd = r'cd /root/testApp/;./dmk_sys -c kill -a'
        print cmd
        return cmd
    def startEvent(self,event):
        cmd = r"cd /root/testApp/;./dmk_sys -c eventstart -a -k '%s' -j 1000 -i 30" % event
        print cmd
        return cmd
    def stopEvent(self):
        cmd = r'cd /root/testApp/;./dmk_sys -c eventstop -a'
        print cmd
        return cmd    

def createSSH(srv_ip='172.17.17.40',username='root',password=''):
    try:
        ssh = para.SSHClient()
        ssh.set_missing_host_key_policy(para.AutoAddPolicy())
        ssh.connect(srv_ip, username=username, password=password)
        return ssh
    except:
        raise Exception('Unable to crate SSH connection to %s ' % srv_ip)

def createSFTP(sshobj,srv_ip='172.17.17.40'):
    ''' this function must work with a ssh connection '''
    try:
        if sshobj:
            sftpobj = sshobj.open_sftp()
        return sftpobj
    except:
        raise Exception('Unable to crate SFTP connection to %s ' % srv_ip)
    
def putConfigsViaSFTP(sftpobj,local=r'/root/testApp',target=r'/root/testApp',files=['init_2_tiers.conf','init_3_tiers.conf',]):
    pass

def scpConfigToDmkGenerator(dimark_generators=DimarkAP_LIST,source_dir=r'/root',target_dir=r'/root/testApp'):
    ''' copy init_2_tiers.conf and init_3_tiers.conf to dimark generator'''
    for ip in dimark_generators:
        cmd = r'scp %s/init_*.conf root@%s:%s' %(source_dir,ip,target_dir)
        print 'IP(%s)\n Command: %s' % (ip,cmd)
        os.system(cmd)

def executeCmd(sshobj,cmd):
    #pdb.set_trace()
    try:
        stdin,stdout,stderr = sshobj.exec_command(cmd)
        return (stdout.readlines(),stderr.readlines())
    except:
        raise Exception('Error: execute command (%s) failed' % cmd)



def changeDir(dir=r'/root/testApp'):
    cmd = r'cd /root/testApp/'
    print cmd
    return cmd

def verifyCurrentDir():
    cmd = r'pwd'
    print cmd
    return cmd

def startAssoc(clients=20):
    '''3.    ./dmk_sys -c assocstart -n <# of clients> -l 0 -a'''
    cmd = r'cd /root/testApp/;./dmk_sys -c assocstart -n %s -l 0 -a' % str(clients)
    print cmd
    return cmd

def stopAssoc():
    cmd='cd /root/testApp/;./dmk_sys -c assocstop -a'
    print cmd
    return cmd
    
def initDimark(tiers):
    if tiers == 3:
        cmd = r'cd /root/testApp/;./dmk_init -c init_3_tiers.conf < /dev/null > /dev/null 2>&1 &'
    else:
        cmd = r'cd /root/testApp/;./dmk_init -c init_2_tiers.conf < /dev/null > /dev/null 2>&1 &'
    print cmd
    return cmd
def removeDimarkAP():
    cmd = r'cd /root/testApp/;./dmk_sys -c kill -a'
    print cmd
    return cmd
 
def createDimarkAPs(dimark_aps=DimarkAP_LIST):
    #dimark_aps=DimarkAP_LIST
    ssh_dict={}
    #create ssh connections for 20 aps
    try:
        for ap in dimark_aps:
            if not pingDimarkAp(ap): 
                #logging.info('CREATE SSH Connection to dimark AP (%s)' % ap)
                print '\n\nCREATE SSH Connection to dimark AP (%s)' % ap
                ssh_dict[ap] = createSSH(srv_ip=ap,username='root',password='')
            ssh_dict['result'] = 'Create APs successfully'
        sorted(dimark_aps.items())
        return ssh_dict
    except:
        ssh_dict['result'] = 'Create APs failed'
        return ssh_dict

def startEvent(self,event):
    cmd = r"cd /root/testApp/;./dmk_sys -c eventstart -a -k '%s' -j 1000 -i 30" % event
    print cmd
    return cmd

def stopEvent(self):
    cmd = r'cd /root/testApp/;./dmk_sys -c eventstop -a'
    print cmd
    return cmd  

def pingDimarkAp(ip='192.168.30.252',counts=2):
    '''Make sure FM is pingable and alive!!'''
    try:
        err=os.system("ping %s -c %d" % (ip,counts))
        #status:
        # ping success: 0
        # ping failed: 1
        # ping unknown: 1
        return err
    except:
        print 'Failed: ping dimark AP (%s)' % ip    




def sendtoSyslog(message='',host=SYSLOG_SERVER,source_ip=DIMARK_CONTROL):
    
    syslog(message=message,
           host=host,
           source_ip=source_ip,
           )
    print "[source_ip: %s]\n\n%s" % (source_ip,message)

    
def printOutput(out):
    for line in out.readlines():
        print "output: %s " % line
def killDimarkAP(aps=DimarkAP_LIST,syslog=SYSLOG_SERVER,dimark_controller_ip=DIMARK_CONTROL):
    try:
        sendtoSyslog(message="Create SSH Connections to Dimark Generators from Dimark Controller",source_ip=dimark_controller_ip)
        dimark_aps=createDimarkAPs(dimark_aps=aps)
        for key in dimark_aps:
            #pdb.set_trace()
            if key != 'result':
                print "Kill AP from Dimark Generator(%s)" % key
                stdout,stderr = executeCmd(dimark_aps[key],cmd=removeDimarkAP())
                stdout.extend(stderr)
                message = '%s' % (stdout)
                time.sleep(1)
                getDimarkSimMemoryUsage(target=key)
                sendtoSyslog(message=message,source_ip=key)
        
        #close ssh connections to dimark generator
        for key in dimark_aps:
            if key != 'result':
                dimark_aps[key].close()
                message = 'Close the SSH connection to AP (%s)' % key
                sendtoSyslog(message=message,source_ip=key )
    except:
        sendtoSyslog(message='Error: Kill dimark failed')
                         
def initDimarkGenerator(aps=DimarkAP_LIST,syslog=SYSLOG_SERVER,dimark_controller_ip=DIMARK_CONTROL,tiers=TIERS):
    try:
        #create SSH connection to dimark generators
        #./DimarkController.sh initiate 10.1.2 1 20
        sendtoSyslog(message="Create SSH Connections to Dimark Generators from Dimark Controller",source_ip=dimark_controller_ip)
        dimark_aps=createDimarkAPs(dimark_aps=aps)
        #dmk_thread={}
        for key in dimark_aps:
            if key != 'result':
                print "Running dmk_init on %s:" % key
                #pdb.set_trace()
                stdout,stderr = executeCmd(dimark_aps[key],cmd=initDimark(tiers=tiers))
                #AP, Dimark AP is designed to redirect output to standard err
                #Merge two of (stderr,stdout) to stdout
                stdout.extend(stderr)
                message = '%s' % (stdout)
                time.sleep(3)
                getDimarkSimMemoryUsage(target=key)
                sendtoSyslog(message=message,source_ip=key)
                #create dimark generator thread
                #dmk_thread[key] = dmkGenerator(dimark_aps[key],key)
                #dmk_thread[key].start()
        #close ssh connections to dimark generator
        for key in dimark_aps:
            if key != 'result':
                dimark_aps[key].close()
                message = 'Close the SSH connection to AP (%s)' % key
                sendtoSyslog(message=message,source_ip=key )
    except:
        sendtoSyslog(message='Error: init dimark failed')

def controlEvent():
    pass

def getFMMemoryUsage(target=FM_IP):
    #check FM server system memory usage
        fmSysMem=MemUsage(type='remote')
        sendtoSyslog(message='FM Total Memory: %s' % fmSysMem.getTotalMem(),source_ip=target)
        sendtoSyslog(message='FM Used Memory: %s' % fmSysMem.getUsedMem(),source_ip=target)
        sendtoSyslog(message='FM Free Memory: %s' % fmSysMem.getFreeMem(),source_ip=target)
        sendtoSyslog(message=r'FM server System Memory Usage: %s' % fmSysMem.getMemoryUsage(),source_ip=target)

def getDimarkSimMemoryUsage(target='1.1.1.123'):
    #check FM server system memory usage
        simSysMem=MemUsage(type='remote')
        sendtoSyslog(message='sim Total Memory: %s' % simSysMem.getTotalMem(),source_ip=target)
        sendtoSyslog(message='FM Used Memory: %s' % simSysMem.getUsedMem(),source_ip=target)
        sendtoSyslog(message='FM Free Memory: %s' % simSysMem.getFreeMem(),source_ip=target)
        sendtoSyslog(message=r'FM server System Memory Usage: %s' % simSysMem.getMemoryUsage(),source_ip=target)
                         
def testDimarkClientAssociation(times=COUNTS,
                                test_time=HOURS,
                                config_time=CONFIG_TIME,
                                clients=CLIENTS,
                                dimark_controller_ip=DIMARK_CONTROL,
                                syslog=SYSLOG_SERVER,
                                aps=DimarkAP_LIST,
                                ):
    try:
        #create dimark aps
        
        dimark_aps=createDimarkAPs(dimark_aps=aps)
        #client association stop
        
        sendtoSyslog(message="Dimark VM needs to stop client association before start testing ",source_ip=dimark_controller_ip)
        sendtoSyslog(message="Client Association Stop",source_ip=dimark_controller_ip)
        
        
        
        try:
            for key in dimark_aps:
                if key != 'result':
                    
                    stdout,stderr = executeCmd(dimark_aps[key],cmd=stopAssoc())
                    #AP, Dimark AP is designed to redirect output to standard err
                    #Merge two of (stderr,stdout) to stdout
                    stdout.extend(stderr)
                      
                    message = '%s' % (stdout)
                    sendtoSyslog(message=message,source_ip=key)
        except:
            sendtoSyslog(message="[Error]: unable to stop client association")
          
                
        #waiting time: 1 hour
        #time.sleep(test_time)
        #pdb.set_trace()
        sendtoSyslog(message="\n\n wait for %s minutes to start sending Client Association message" % str(config_time/60),source_ip=dimark_controller_ip)
        time.sleep(config_time) #debug
        
        #check FM server system memory usage
#        fmSysMem=MemUsage(type='remote')
#        sendtoSyslog(message='FM Total Memory: %s' % fmSysMem.getTotalMem())
#        sendtoSyslog(message='FM Used Memory: %s' % fmSysMem.getUsedMem())
#        sendtoSyslog(message='FM Free Memory: %s' % fmSysMem.getFreeMem())
#        sendtoSyslog(message='FM server System Memory Usage (%): %s' %fmSysMem.getMemoryUsage())
        getFMMemoryUsage()
        
        #print "Dimark Client Association Command Cycle: %s" % times
        sendtoSyslog(message="Dimark Client Association Command Cycle: %s" % times,source_ip=dimark_controller_ip)
        sendtoSyslog(message="Client Association",source_ip=dimark_controller_ip)
        
        for count in range(times):
            #print "Client Assciation Start: %s" % str(count+1)
            sendtoSyslog(message="Client Asscoiation Start: %s" % str(count+1),source_ip=dimark_controller_ip)
            for key in dimark_aps:
                if key != 'result':
                    #pdb.set_trace()
                    #stdin, stdout,stderr = executeCmd(dimark_aps[key],cmd=stopAssoc())
                    stdout,stderr = executeCmd(dimark_aps[key],cmd=startAssoc(clients=clients))
                    stdout.extend(stderr)
              
                    message = '%s' % (stdout)
                    getDimarkSimMemoryUsage(target=key)
                    sendtoSyslog(message=message,source_ip=key )
            #waiting time: 1 hour
            #time.sleep(HOUR)
            sendtoSyslog(message="\n\n wait for %s minutes to stop client association" % str(test_time/60),source_ip=dimark_controller_ip)
            time.sleep(test_time) #debug
            
            #client association stop
            sendtoSyslog(message= "Client Assciation Stop: %s" % str(count+1),source_ip=dimark_controller_ip)
            for key in dimark_aps:
                if key != 'result':
                    stdout,stderr = executeCmd(dimark_aps[key],cmd=stopAssoc())
                    stdout.extend(stderr)
                    message = '%s' % (stdout)
                    getDimarkSimMemoryUsage(target=key)
                    sendtoSyslog(message=message,source_ip=key )
            #waiting time: 1 hour
            sendtoSyslog(message='\n\n wait for %s minutes to start client association' % str(test_time/60),source_ip=dimark_controller_ip)
            
            for check in range(MEMORY_CHECK):
                sendtoSyslog(message='Check Memory Usage: %s' % check)
                getFMMemoryUsage()
                time.sleep(test_time/MEMORY_CHECK)
        
        sendtoSyslog(message="Close the SSH connection",source_ip=dimark_controller_ip)
        for key in dimark_aps:
            if key != 'result':
                getDimarkSimMemoryUsage(target=key)
                dimark_aps[key].close()
                message = 'Close the SSH connection to AP (%s)' % key
                sendtoSyslog(message=message,source_ip=key )
                
    except:
        sendtoSyslog(message='Error: Dimark client association commands start/stop failed')
        #raise Exception(message='Error: Dimark client association commands start/stop failed')

def usage_02():
    from string import Template
    print Template("""
Usage: python ${MYNAME} <type> [[<key]<=[<value>]] ...]

    where:
        <type>: type of dimark control. 2 type: client(client association) and ap (ap control)
    
        <key> <=[<value>]...: any word that this script will take
        
        times: times to execute client association start/stop. (default=6)
        dimark_controller_ip: ip address of dimark controller (default ip 172.17.18.40)
        syslog_ip: ip address of syslog server (default ip 172.17.16.68)
        test_time: time to wait between launch "associate client" start and stop (default 90 minutes, 5400 second)
        config_time: Before entering test cycle, time to wait reset dimark client association message (default 20 minutes)
        clients: client association amount need to be sent out (default=20, total clients(100,000) = 20 client X 250 AP X 20 dimark VM)
           
Examples:
   python ${MYNAME} client syslog=172.17.16.68
   python ${MYNAME} client times=6 dimark_controller_ip=172.17.18.40 test_time=5400 config_time= 1200
   python ${MYNAME} init tiers=2
   python ${MYNAME} init tiers=3
   python ${MYNAME} client
   python ${MYNAME} kill
   python ${MYNAME} event
   python ${MYNAME} mem
   python ${MYNAME} mem target='172.17.18.31'
""").substitute(dict(MYNAME = MYNAME))



        
if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        # only sys.argv[0] = dimark_control.py
        # defalt working command: python dimark_control.py type=client
        usage_02()
        exit(1)
    type=sys.argv[1]
    kwdict = kwlist.as_dict2(sys.argv[2:])
    #pdb.set_trace()
    print "sys.argv:%d,%s" % (len(sys.argv),sys.argv)
    print "kwdict:",kwdict
    
    if type == 'client':
        testDimarkClientAssociation(**kwdict)
    elif type == 'init':
        #default will start 2 tiers architecture
        initDimarkGenerator(**kwdict)
    elif type == 'kill':
        killDimarkAP(**kwdict)
    elif type == 'event':
        controlEvent(**kwdict)
    elif type == 'mem':
        #MemUsage(type='remote')
        getFMMemoryUsage()
    else:
        usage_02()
        exit(0)
        
    #testDimarkClientAssociation(times=COUNTS)