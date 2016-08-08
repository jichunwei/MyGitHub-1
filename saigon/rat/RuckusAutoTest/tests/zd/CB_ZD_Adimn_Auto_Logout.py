'''
verify admin auto logout
by west.li
@2012.4.9
'''

import time
from RuckusAutoTest.models import Test
import logging

class CB_ZD_Adimn_Auto_Logout(Test):

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        time_out=self.conf['time_out']
        logging.info('time out value:%s'%time_out)
        if self.conf['set_first']:
            result,msg=self.zd.set_session_timeout(time_out)
            if not result:
                return 'FAIL',msg
        logging.info('I will wait %d seconds and continue the test'%(time_out*60-30))
        time.sleep(time_out*60-30)
        if not self.zd.check_auto_logout_status(False):
            return 'FAIL','zd session timeout value is %d minutes(%d seconds),but auto logout after %d seconds '%(time_out,time_out*60,time_out*60-30)
        t_wait=time_out*60+30
        logging.info('I will wait %d seconds and continue the test'%(t_wait))
        time.sleep(t_wait)
        if not self.zd.check_auto_logout_status(True):
            log_out_error=True
            self.errmsg='zd session timeout value is %d minutes(%d seconds),but not auto logout after %d seconds '%(time_out,time_out*60,t_wait)
            while log_out_error and t_wait<time_out*60+60:
                t_wait+=10
                self.zd.refresh()
                logging.info('I will wait %d seconds and continue the test'%(t_wait))
                time.sleep(t_wait)
                if self.zd.check_auto_logout_status(True):
                    log_out_error=False
            if log_out_error:
                self.errmsg+=',also not logout after %d seconds'%t_wait
            else:
                self.errmsg+=',auto logout after %d seconds'%t_wait
            return 'FAIL',self.errmsg
        self.carrierbag['session_time_out']=time_out
        return 'PASS','zd session timeout value is %d minutes(%d seconds),not auto logout after %d seconds,auto logout after %d seconds'%(time_out,time_out*60,time_out*60-30,time_out*60+30)
    def cleanup(self):
        pass


    def _initTestParameters(self, conf):
        self.conf = {'time_out':3,
                     'set_first':True}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''


