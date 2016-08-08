'''
set session timeout via zdcli
by west.li
@2012.4.9
'''

import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient
from RuckusAutoTest.components import create_zd_cli_by_ip_addr
import logging

class CB_ZDCLI_Admin_Auto_Logout(Test):

    def config(self, conf):
        self._initTestParameters(conf)


    def test(self):
        time_out=self.conf['session_time_out']
        logging.info('session time out value to set:%s'%time_out)
        if self.conf['username'] != 'admin':
            tmp_username = 'test5'
            tmp_password = 'lab4man1'
        else:
            tmp_username = self.conf['username']
            tmp_password = self.conf['password']
        zdcli = create_zd_cli_by_ip_addr(ip_addr=self.zdcli.ip_addr, username=tmp_username, password=tmp_password)
        result,msg=zdcli.set_session_timeout(time_out)
        zdcli.close()
        
        if self.conf['logout_first']:
            try:
                logging.info('logout zd cli first')
                self.zdcli.logout()
            except:
                logging.info('logout zdcli met issue')
                pass
            
        try:
            self.zdcli.do_cmd('')
        except:
            self.zdcli.close()
            logging.info('connect zdcli by ssh')
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,self.conf['username'],self.conf['password'])
            self.zdcli.username,self.zdcli.password=self.conf['username'],self.conf['password']
            logging.info('loggin zdcli use new ip, username-%s and password-%s' % (self.conf['username'], self.conf['password']))
            self.zdcli.login(set_session_timeout=False)
            logging.info('login zd cli use ip %s by %s/%s successfully'%(self.zdcli.ip_addr,self.conf['username'],self.conf['password']))
        
        logging.info('==wait session timeout for %s mins==' % time_out)
        t0=time.time()
        t=t0
        if self.conf['telnet_check']:
            result,msg = self.zdcli.start_telnet_cli()
            t0=time.time()
            t=t0
        if not result:
            return ('FAIL', msg)
        while True:
            if t-t0>time_out*60+30:
                return 'FAIL','session time out to %d mins(%d seconds),but admin not auto logout after %d second'%(time_out,time_out*60,t-t0)
            if self.zdcli.check_auto_logout_status(telnet_zdcli=self.conf['telnet_check']):
                t=time.time()
                self.carrierbag['session_time_out']=time_out
                if t-t0>=time_out*60-30:
                    return 'PASS','session time out to %d mins(%d seconds),and admin auto logout after %d second'%(time_out,time_out*60,t-t0)
                else:
                    return 'FALI','session time out to %d mins(%d seconds),but admin auto logout after %d second'%(time_out,time_out*60,t-t0)
            else:
                t=time.time()

    def cleanup(self):
        if self.conf['ip']:
            self.zdcli.ip_addr = self.ip_bak
            logging.info('restore zdcli ip to %s'%self.zdcli.ip_addr)
        
        if self.conf['relogin']:
            logging.info('try to logout zdcli')
            try:
                self.zdcli.logout(telnet=self.conf['telnet_check'])
                logging.info('logout zdcli succ')
            except:
                logging.info('logout zdcli met problem')
                
            logging.info('try to connect zd by ssh')
            self.zdcli.close()
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,self.zdcli.username,self.zdcli.password)
            logging.info('try to login zdcli')
            self.zdcli.login()
            logging.info('login zd cli use ip %s by %s/%s successfully'%(self.zdcli.ip_addr,self.zdcli.username,self.zdcli.password))
        else:
            try:
                logging.info('reset session timeout to 600')
                self.zdcli.do_shell_cmd('')
                self.zdcli.set_session_timeout(600)
            except:
                logging.info('set session timeout error,relogin zdcli')
                self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,self.conf['username'],self.conf['password'])
                self.zdcli.username,self.zdcli.password=self.conf['username'],self.conf['password']
                self.zdcli.login()
        self.zdcli.username,self.zdcli.password=self.username_bak,self.password_bak
        logging.info('restore zdcli username and password to %s/%s'%(self.zdcli.username,self.zdcli.password))

    def _initTestParameters(self, conf):
        self.conf = {'logout_first':False,
                     'session_time_out':3,
                     'telnet_check':False,
                     'username':'admin',
                     'password':'admin',
                     'ip':'',
                     'relogin':False}
        self.conf.update(conf)

        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.username_bak,self.password_bak=self.zdcli.username,self.zdcli.password
        self.zdcli.username,self.zdcli.password=self.conf['username'],self.conf['password']
        
        if self.conf['ip']:
            self.ip_bak = self.zdcli.ip_addr
            self.zdcli.ip_addr = self.conf['ip']
        self.errmsg = ''
        self.passmsg = ''
        