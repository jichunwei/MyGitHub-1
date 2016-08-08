"""
Component to manage VeriWave Automated Test Appliance through telnet session.

All resouce created by an user will be kept even the user logout.
"""
import os
import sys
import time
import re
import telnetlib as TNET
import socket
from RuckusAutoTest.components.lib.zdcli import output_as_dict as OAD
#from xlogger import XLogger

PS_L_01 ="Hit Enter to proceed: "
PS_L_02 = "Enter username: "
PS_R_02 = "Welcom, %s"

PS_ATA="(\w+)\s+ready>"
PS_ATA_USER="%s\s+ready>"
PS_OK_RESPONSE=r"cmdStatus=ok\s(.*)"


class AtaTelnet(object):
    def __init__(self, ip_addr,username,**kwargs):
        self.ip_addr = ip_addr
        self.cfg=dict(port=23,init=True,timeout=10,loglevel=0)
        self.cfg.update(kwargs)
        self.username = username
        self.u_prompt = re.compile(PS_ATA_USER % self.username)
        self.r_prompt = re.compile(PS_OK_RESPONSE+(PS_ATA_USER % self.username))
        self.loglevel=self.cfg.pop('loglevel')
        if self.cfg['init']:
            self.login()


    def login(self):
        self.ata = TNET.Telnet(self.ip_addr,self.cfg['port'])
        self.ata.expect([PS_L_01,])
        self.ata.write('\n')
        self.ata.expect([PS_L_02,])
        self.ata.write(self.username+'\n')
        self.ata.expect([self.u_prompt])


    def close(self):
        try:
            self.ata.write('exit\n')
            time.sleep(0.05)
            self.ata.close()
        except:
            pass


    def exc_cmd(self, cmd_str,timeout=0):
        self.raw_output = ''
        tout = timeout if timeout > 0 else self.cfg['timeout']
        try:
            if self.loglevel: print "S: %s" % cmd_str
            self.ata.write(cmd_str+"\n")
            self.outx = self.ata.expect([self.u_prompt],timeout=tout)
            if self.loglevel: print "R: %s" % self.outx[2]
        except (EOFError, socket.error):
            return None
        return self.outx[2]        

    def perform(self,cmd_str,timeout=0,ofmt='dict'):
        self.exc_cmd(cmd_str,timeout)
        l2=self.outx[2].find("\n") + 1
        self.r_status = self.outx[2][:l2-1]
        outx = self.outx[2][l2:]
        mm = re.search(self.u_prompt,outx)
        if not mm:
            self.r_output = ''
            return None
        self.r_output = outx[:mm.start()-1]
        if ofmt!='dict': return self.r_output
        rdict = OAD.parse(self.r_output)
        return rdict

    def list_all(self):
        ports = self.perform('list ports')
        servers = self.perform('list servers')
        clients = self.perform('list clients')
        flows = self.perform('list flows')
        options = self.perform('list options')
        return dict(ports=ports,
                    servers=servers,
                    clients=clients, 
                    flows=flows,
                    options=options)


#
#
#
def list_admin(ip_addr='10.150.4.97',username='admin'):
    ata = AtaTelnet(ip_addr,username,init=False)
    ata.login()
    return ata.list_all()

