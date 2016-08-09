from RuckusAutoTest.common.utils import *
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib

from RuckusAutoTest.models import Test


msg_cfg = dict(
    cfg_match=('Remote Mgmt config on FM Device View and AP is %s.',
               { True: 'matched', False: 'NOT matched', }),
    is_prov=('%s to provision after changing remote Mgmt config.',
             { True: 'Able', False: 'Unable', }),
    prov_match=('Subsequence provisioning config after changing remote Mgmt is %s.',
                { True: 'matched', False: 'NOT matched', }),
)

ap_ip = '192.168.20.170'
testcase = 0
test_cfg = [
    dict(
        ap_ip=ap_ip,
        precfg=dict(remote_mode='fm',),
        cfg=dict(remote_mode='auto',),
        device_cfg=dict(device_name='__superdog__'),
        expected=dict(cfg_match=True, is_prov=True, prov_match=True,),
    ),
    dict(
        ap_ip=ap_ip,
        precfg=dict(remote_mode='auto',),
        cfg=dict(remote_mode='fm',),
        device_cfg=dict(device_name='__superdog__'),
        expected=dict(cfg_match=True, is_prov=True, prov_match=True,),
    ),
    dict(
        ap_ip=ap_ip,
        precfg=dict(remote_mode='auto',),
        cfg=dict(remote_mode='snmp',),
        device_cfg=dict(device_name='__superdog__'),
        expected=dict(cfg_match=True, is_prov=False, prov_match='na',),
    ),
][testcase]


class FMDV_Mgmt_RemoteModes(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)

        self.ap.start()
        logging.info('Trying to set Mgmt > Remote Mgmt to pre-config on AP')
        lib.ap.acc.set(self.ap, self.p['precfg'])
        wait_for_sync(self.dv, self.p['precfg'], lib.fmdv.access.get)

        logging.info('Trying to restore Device config to default')
        try:
            lib.fmdv.dev.reset(self.dv, self.p['device_cfg'])
        except:
            log_trace()


    def test(self):
        self._cfg_access()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._cfg_device()
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
        if self.ap and self.dv:
            logging.info('Trying to restore Mgmt > Remote Mgmt to default on AP')
            lib.ap.acc.reset(self.ap, self.p['ks'])
            default_cfg = to_str_dict_items(
                dict_by_keys(self.dv.access_mgmt, self.p['ks']))
            wait_for_sync(self.dv, default_cfg, lib.fmdv.access.get)

            logging.info('Trying to restore Device config to default')
            lib.fmdv.dev.reset(self.dv, self.p['device_cfg'].keys())

            self.ap.stop()
            self.fm.cleanup_device_view(self.dv)
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = copy.deepcopy(cfg)
        #self.p = test_cfg # this is for unit testing
        init_coms(
            self,
            dict(tb=self.testbed, ap_ip=self.p['ap_ip'],dv_ip=self.p['ap_ip'],),
        )
        self.p['ks'] = join_keys(self.p['precfg'], self.p['cfg'])
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _cfg_access(self):
        logging.info('Provisioning the Remote Mgmt config from device view')
        log('config:\n%s' % pformat(self.p['cfg']))
        if not lib.fmdv.access.set(self.dv, self.p['cfg'])[0]:
            raise Exception('Failed to provision Remote Mgmt config from Device View')
        wait_for('Remote Management to be pushed to AP', 5)


    def _cfg_device(self):
        logging.info('Provisioning the Device config from device view')
        log('config:\n%s' % pformat(self.p['device_cfg']))
        self.p['is_prov'], d = lib.fmdv.dev.set(self.dv, self.p['device_cfg'])


    def _get_results(self):
        '''
        go to AP WebUI to get the provisioning configs
        '''
        logging.info('Get the config from AP WebUI...')
        wait_for_sync(self.ap, self.p['cfg'], lib.ap.acc.get, tries=5, interval=5)
        self.p['ap_cfg'] = lib.ap.acc.get(self.ap, self.p['cfg'].keys())
        log('AP config:\n%s\n' % pformat(self.p['ap_cfg']))

        if self.p['expected']['prov_match'] != 'na':
            self.p['ap_device_cfg'] = lib.ap.dev.get(self.ap, self.p['device_cfg'].keys())
            log('AP Device config:\n%s\n' % pformat(self.p['ap_device_cfg']))


    def _is_match(self, testcfg, apcfg):
        ''' should be in  lib_FM '''
        testcfg = to_str_dict_items(copy.deepcopy(testcfg))
        apcfg = to_str_dict_items(copy.deepcopy(apcfg))
        if apcfg != testcfg:
            logging.info('Config on AP does NOT match test config')
            log('Test config:\n%s\nAP config:\n%s\n' % (pformat(testcfg), pformat(apcfg)))
            return False
        return True


    def _test_results(self):
        '''
        based on the expected, deciding testing pass or fail
        '''
        e = self.p['expected']
        logging.info('Comparing the result with expected...')
        r = dict(
            cfg_match=self._is_match(self.p['cfg'], self.p['ap_cfg']),
            is_prov=self.p['is_prov'],
            prov_match='na' if e['prov_match'] == 'na'
                else self._is_match(self.p['device_cfg'], self.p['ap_device_cfg']),
        )
        log('\nExpected: %s\nResult:   %s\n' % (e, r))

        msg = ' '.join([msg_cfg[k][0] % msg_cfg[k][1][v]
                           for k, v in r.iteritems()
                           if k in msg_cfg and v in msg_cfg[k][1]])
        if r == e:
            self.passmsg = msg
            return
        self.errmsg = msg
        return
