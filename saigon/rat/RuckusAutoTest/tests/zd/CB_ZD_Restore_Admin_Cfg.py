'''

'''
import logging

from RuckusAutoTest.models import Test


class CB_ZD_Restore_Admin_Cfg(Test):
    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrive_carrier_bag()


    def test(self):
        self._restore_admin_cfg()

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self._update_carrier_bag()

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        '''
        '''
        self.conf = {}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ""
        self.passmsg = ""


    def _retrive_carrier_bag(self):
        '''
        '''
        self.admin_cfg = self.conf.get("admin_cfg")

        if not self.admin_cfg:
            self.admin_cfg = self.carrierbag.get("bak_admin_cfg")

        if not self.admin_cfg:
            raise Exception("No admin config provided.")


    def _update_carrier_bag(self):
        '''
        '''


    def _restore_admin_cfg(self):
        logging.info('Restore the admin configuration.')
        try:
            self.zd.set_admin_cfg(self.admin_cfg)

            self.passmsg = 'Restore the admin configuration successfully'

        except Exception, ex:
            self.errmsg = ex.message

