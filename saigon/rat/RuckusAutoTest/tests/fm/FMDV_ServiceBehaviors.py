import logging
import copy
import re

from pprint import pformat

from RuckusAutoTest.common.utils import (
    log, wait_for, to_str_dict_items, dict_by_keys, join_keys, try_interval
)
from RuckusAutoTest.tests.fm.lib_FM import (
    wait_for_sync, remove_incompatible_cfg, init_coms
)
from RuckusAutoTest.components import Helpers as lib

from RuckusAutoTest.models import Test


PS_RE=dict(
    tr069=r'/usr/sbin/tr069d',
    apmgr=r'/usr/sbin/apmgr',
    snmp=r'snmpd.*',
)

STATE_CHANGE_WAIT=6*60 # 6 mins

msg_cfg = dict(
    tr069=('TR069 process is %s on AP CLI.',
           { True: 'found', False: 'NOT found', }),
    apmgr=('APMGR process is %s on AP CLI.',
           { True: 'found', False: 'NOT found', }),
    snmp= ('SNMP process is %s on AP CLI.',
           { True: 'found', False: 'NOT found', }),
    cfg_match=('Remote Mgmt config on FM Device View and AP is %s.',
               { True: 'matched', False: 'NOT matched', }),
)

ap_ip = '192.168.20.170'
testcase = 1
test_cfg = [
    # ACS Avail + Auto mode
    dict(
        ap_ip=ap_ip,
        precfg=dict(inform_interval='1m'),
        cfg=dict(remote_mode='auto',),
        prov_from='ap',
        expected=dict(tr069=True, snmp=False, apmgr=True),
    ),
    # ACS Avail + Auto mode + Prov from FM
    dict(
        ap_ip=ap_ip,
        precfg=dict(
            inform_interval='1m',
            remote_mode='fm',
        ),
        cfg=dict(remote_mode='auto',),
        prov_from='fm',
        #expected=dict(cfg_match=True), # for provisioning from FMDV
        expected=dict(tr069=True, snmp=False, apmgr=True, cfg_match=True),
    ),
    # ACS Un-avail + Auto mode: snmp change state case
    dict(
        ap_ip=ap_ip,
        precfg=dict(
            remote_mode='fm',
            inform_interval='1m'
        ),
        cfg=dict(
            remote_mode='auto',
            fm_url='http://192.168.0.252/intune/server',
        ),
        prov_from='ap',
        expected=dict(tr069=True, snmp=True, apmgr=True),
    ),
][testcase]


class FMDV_ServiceBehaviors(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)

        self.ap.start()
        logging.info('Trying to set Mgmt > Remote Mgmt to pre-config on AP')
        lib.ap.acc.set(self.ap, self.p['precfg'])
        if self.p['prov_from'] == 'fm':
            wait_for_sync(
                self.dv,
                remove_incompatible_cfg(self.p['precfg'], self.p['incompatible_ks']),
                lib.fmdv.access.get
            )


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
        . restoring to default configs on AP
          why? fm_url is not there in FMDV
        . log out flex master
        '''
        if self.ap:
            logging.info('Trying to restore Mgmt > Remote Mgmt to default on AP')
            lib.ap.acc.reset(self.ap, self.p['ks'])
            if self.dv:
                default_cfg = to_str_dict_items(
                    dict_by_keys(self.dv.access_mgmt, self.p['ks'])
                )
                default_cfg = remove_incompatible_cfg(default_cfg, self.p['incompatible_ks'])
                wait_for_sync(self.dv, default_cfg, lib.fmdv.access.get)
                self.fm.cleanup_device_view(self.dv)

            self.ap.stop()
        if self.ap_cli:
            del self.ap_cli
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        #self.p = test_cfg
        self.p = copy.deepcopy(cfg)

        com_cfg = dict(tb=self.testbed, ap_ip=self.p['ap_ip'],
                       apcli_cfg=dict(ip_addr=self.p['ap_ip']))
        if self.p['prov_from'] == 'fm': # FM Device View is optional
            com_cfg['dv_ip']=self.p['ap_ip']
        init_coms(self, com_cfg)

        self.p['ks'] = join_keys(self.p['cfg'], self.p['precfg'])

        self.p['wait_for'] = dict(
            [(k, self.p['expected'][k]) for k in PS_RE if k in self.p['expected']]
        )

        # TODO: should impl on AP_feature!!!
        self.p['incompatible_ks'] = ['fm_url', 'inform_interval']
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _cfg_access(self):
        logging.info('Provisioning the Remote Mgmt config from %s' %
                     ('Device View' if self.p['prov_from'] == 'fm' else 'AP WebUI'))
        log('config:\n%s' % pformat(self.p['cfg']))
        if self.p['prov_from'] == 'fm': # FM Device View is optional
            if not lib.fmdv.access.set(self.dv, self.p['cfg'])[0]:
                raise Exception('Failed to provision Remote Mgmt config from Device View')
        else:
            lib.ap.acc.set(self.ap, self.p['cfg'])
        wait_for('Remote Management config to be sync', 5)


    def _get_process_status(self, name, log):
        ''' is the process alive? '''
        if re.search(PS_RE[name], log):
            return True
        return False


    def _is_cond_match(self, log):
        ''' is the expected condition match? '''
        for ps, status in self.p['wait_for'].iteritems():
            if self._get_process_status(ps, log) != status:
                return False
        return True


    def _get_results(self):
        '''
        go to AP WebUI to get the provisioning configs
        '''
        logging.info('Get the processes on AP CLI...')
        # after trying interval, if the state of the process is not changed
        # then no worry, it will be retrieved again in _test_results
        for z in try_interval(STATE_CHANGE_WAIT, 10):
            logging.info('Wait for process state changing...')
            pslog = self.ap_cli.get_processes()
            if self._is_cond_match(pslog):
                break
        self.p['pslog'] = pslog
        log('Processes in CLI:\n%s\n' % pslog)

        if self.p['prov_from'] == 'fm':
            self.p['ap_cfg'] = lib.ap.acc.get(self.ap, self.p['cfg'].keys())


    def _is_match(self, testcfg, apcfg):
        ''' TODO: should be in  lib_FM '''
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
        r = dict([(k, self._get_process_status(k, self.p['pslog']))
                  for k in PS_RE.keys()])
        if self.p['prov_from'] == 'fm':
            r['cfg_match'] = self._is_match(self.p['cfg'], self.p['ap_cfg'])
        log('\nExpected: %s\nResult:   %s\n' % (e, r))

        msg = ' '.join([msg_cfg[k][0] % msg_cfg[k][1][v]
                           for k, v in r.iteritems()
                           if k in msg_cfg and v in msg_cfg[k][1]])
        if r == e:
            self.passmsg = msg
            return
        self.errmsg = msg
        return
