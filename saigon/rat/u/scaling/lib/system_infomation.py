'''
Created on Nov 19, 2010

1.check Flex master system memory usage

@author: webber.lin
'''

#python modules

import paramiko as para
import pdb
import logging
import subprocess
TYPE='local'
TARGET='172.17.18.31'
#from u.scaling.lib.dimark_control import createSSH
#from common_remote_control import createSSH,executeCmd

def createSSH(srv_ip='172.17.18.40',username='root',password=''):
    try:
        ssh = para.SSHClient()
        ssh.set_missing_host_key_policy(para.AutoAddPolicy())
        ssh.connect(srv_ip, username=username, password=password)
        return ssh
    except:
        raise Exception('Unable to crate SSH connection to %s ' % srv_ip)

def executeCmd(sshobj,cmd):
    #pdb.set_trace()
    try:
        stdin,stdout,stderr = sshobj.exec_command(cmd)
        return (stdout.readlines(),stderr.readlines())
    except:
        raise Exception('Error: execute command (%s) failed' % cmd)

class MemUsage(object):
    def __init__(self,total=1,used=1,free=1,shared=1,buffers=1,cached=1,type=TYPE,target=TARGET):
        self.total=total
        self.used=used
        self.free=free
        self.shared=shared
        self.buffers=buffers
        self.cached=cached
        self.type=type
        self.target=target
        self.init_data()         
    def getRemoteMem(self,user='root',password='!v54!scale'):
        #pdb.set_trace()
        ssh = createSSH(srv_ip=self.target,username=user,password=password)
        stdout,stderr = executeCmd(ssh,cmd='free')
        stdout.extend(stderr)
        ssh.close()
        #print stdout
        data=stdout[1].split()
        try:
            #print "[IP:%s] %s" % (self.target,data)
            if data[0] == "Mem:":
                self.total=float(data[1])
                self.used=float(data[2])
                self.free=float(data[3])
                self.shared=float(data[4])
                self.buffers=float(data[5])
                self.cached=float(data[6])
        except IndexError:
            logging.error('cannot get correct data')
    def getLocalMem(self,cmd='free'):
        process=subprocess.Popen(cmd,
        shell=True,
        stdout=subprocess.PIPE)
        stdout_list=process.communicate()[0].split('\n')
        for line in stdout_list:
            data=line.split()
            try:
                #print data
                if data[0] == "Mem:":
                    self.total=float(data[1])
                    self.used=float(data[2])
                    self.free=float(data[3])
                    self.shared=float(data[4])
                    self.buffers=float(data[5])
                    self.cached=float(data[6])
            except IndexError:
                continue
    def init_data(self):
        '''
        Two ways to initialize memory information: 
        1. get local mem information
        2. get remote memory information
        '''
        if self.type == 'local':
            logging.info('Get Local Memory Information')
            self.getLocalMem()
        elif self.type == 'remote':
            logging.info('Get Remote Machine (%s) Memory Information' % self.target)
            self.getRemoteMem()    
        else:
            logging.info('Error: type (remote/local) is not given')        
    def getTotalMem(self):
        return self.total
    def getUsedMem(self):
        return self.used
    def getFreeMem(self):
        return self.free
    def getSharedMem(self):
        return self.shared
    def getBuffers(self):
        return self.buffers
    def getcached(self):
        return self.cached
    def getMemoryUsage(self):
        ''' calculate the percentage of memory usage'''
        return ((self.used-self.buffers-self.cached)/self.total)*100
    def __repr__(self):
        return str(self.getMemoryUsage())

if __name__=="__main__":
    m_local = MemUsage()
    print "Local Memory Usage",m_local
    m_remote = MemUsage(type='remote')
    print "Remote site Memory Usage",m_remote