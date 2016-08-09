from RuckusAutoTest.common.utils import *
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib

from RuckusAutoTest.models import Test


UNABLE_SET_MSG = 'Unabled to set all managements to disabled on Device View '
MSGS = [
    'Able to set all managements to disabled',
    UNABLE_SET_MSG + 'but these configs are propagated to AP',
    UNABLE_SET_MSG + 'and these configs are NOT propagated to AP',
]


class FMDV_Mgmt_DisableAll(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)
        try:
            logging.info('Trying to set Mgmt to pre-config on device view')
            lib.fmdv.access.set(self.dv, self.p['mgmt_precfg'])
        except:
            logging.debug('It seems Mgmt is in pre-config state')
            log_trace()
        lib.fmdv.access.nav_to(self.dv, force=True)


    def test(self):
        self._cfg_access()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._get_results()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_results()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        '''
        . restoring to default configs
        . log out flex master
        '''
        if self.dv:
            try:
                logging.info('Trying to set Mgmt to default config on device view')
                lib.fmdv.access.reset(self.dv, self.p['mgmt_cfg'].keys())
            except:
                log_trace()
            self.fm.cleanup_device_view(self.dv)
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = dict(
            ap_ip='192.168.20.171',
            mgmt_cfg=dict(
                http_enabled='disabled',
                https_enabled='disabled',
                telnet_enabled='disabled',
                ssh_enabled='disabled',
            ),
            mgmt_precfg=dict(
                http_enabled='enabled',
                https_enabled='enabled',
                telnet_enabled='enabled',
                ssh_enabled='enabled',
            ),
            ap_mgmt_cfg = None,
        )
        update_dict(self.p, cfg)

        # init common used aliases/components:
        init_coms(
            self,
            dict(tb=self.testbed,ap_ip=self.p['ap_ip'],dv_ip=self.p['ap_ip'],)
        )
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _cfg_access(self):
        '''
        it is expected that this config can not be set
        so an exception is expected here
        '''
        logging.info('Provisioning the mgmt config from device view')
        logging.debug('Mgmt config:\n%s' % pformat(self.p['mgmt_cfg']))
        try:
            if not lib.fmdv.access.set(self.dv, self.p['mgmt_cfg'])[0]:
                raise Exception('Failed to provisioning from Device View')
            self.errmsg = MSGS[0]
            return
        except:
            logging.info('Expected behavior: Cannot set this config from Device View')
            log_trace()
        lib.fmdv.access.nav_to(self.dv, force=True)


    def _get_results(self):
        '''
        go to AP WebUI to get the mgmt config
        '''
        logging.info('Get the mgmt config from AP WebUI..')
        self.ap.start()
        self.p['ap_mgmt_cfg'] = lib.ap.acc.get(self.ap, self.p['mgmt_cfg'].keys())
        self.ap.stop()
        del self.ap
        log('AP mgmt configs:\n%s\n' % pformat(self.p['ap_mgmt_cfg']))


    def _test_results(self):
        if self.p['mgmt_cfg'] == self.p['ap_mgmt_cfg']:
            self.errmsg = MSGS[1]
            return
        self.passmsg = MSGS[2]
        return

