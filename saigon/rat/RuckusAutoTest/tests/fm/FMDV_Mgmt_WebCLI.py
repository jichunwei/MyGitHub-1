import copy
import logging
import socket
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_com

from RuckusAutoTest.common.utils import wait_for, dict_by_keys, join_keys, log, log_trace
from RuckusAutoTest.tests.fm.lib_FM import wait_for_sync, reboot_ap, to_str_dict_items, \
        init_coms


ACCESSIBLE_MSGS = { True: 'accessible', False: 'NOT accessible', }
MATCH_MSGS = { True: 'matched', False: 'NOT matched', }

msg_cfg = dict(
    cfg_match=('Mgmt config on FM Device View and AP is %s.', MATCH_MSGS),
    web=('Web is %s.', ACCESSIBLE_MSGS),
    cli=('CLI is %s.', ACCESSIBLE_MSGS),
)

'''
write down the constraints for these configs:
. cfg: must have enabled, port in case enabling
. cannot disable all web services because tr069 based on web services
'''
AP_IP='192.168.20.180'
testcase = 2
test_cfg = [
    # http: enabled, default port
    dict(
        ap_ip=AP_IP,
        precfg=dict(http_enabled='disabled', https_enabled='enabled',),
        cfg=dict(http_enabled='enabled', http_port=80,
                 https_enabled='disabled'),
        ap_cfg=dict(ip_addr='%s:%s' % (AP_IP, 80), https=False,),
        expected=dict(web=True, cli='na', cfg_match=True),
    ),
    # http: enabled, custom port
    dict(
        ap_ip=AP_IP,
        precfg=dict(http_enabled='disabled', https_enabled='enabled',),
        cfg=dict(http_enabled='enabled', http_port=9999,
                 https_enabled='disabled',),
        ap_cfg=dict(ip_addr='%s:%s' % (AP_IP, 9999), https=False,),
        expected=dict(web=True, cli='na', cfg_match=True),
    ),

    # https: enabled, default port
    dict(
        ap_ip=AP_IP,
        precfg=dict(https_enabled='disabled', http_enabled='enabled',),
        cfg=dict(https_enabled='enabled', https_port=443,
                 http_enabled='disabled',),
        ap_cfg=dict(ip_addr='%s:%s' % (AP_IP, 443), https=True,),
        expected=dict(web=True, cli='na', cfg_match=True),
    ),
    # https: enabled, custom port
    dict(
        ap_ip=AP_IP,
        precfg=dict(https_enabled='disabled', http_enabled='enabled',),
        cfg=dict(https_enabled='enabled', https_port=9998,
                 http_enabled='disabled',),
        ap_cfg=dict(ip_addr='%s:%s' % (AP_IP, 9998), https=True,),
        expected=dict(web=True, cli='na', cfg_match=True),
    ),

    # telnet: enabled, default port
    dict(
        ap_ip=AP_IP,
        precfg=dict(telnet_enabled='disabled', telnet_port=9997,
                    ssh_enabled='disabled', https_enabled='enabled',),
        cfg=dict(telnet_enabled='enabled', telnet_port=23,),
        ap_cfg=dict(ip_addr=AP_IP, https=True,),
        apcli_cfg=dict(ip_addr=AP_IP, port=23, telnet=True, force_telnet=True),
        expected=dict(web=True, cli=True, cfg_match=True),
    ),
    # telnet: enabled, custom port
    dict(
        ap_ip=AP_IP,
        precfg=dict(telnet_enabled='disabled', telnet_port=23,
                    ssh_enabled='disabled', https_enabled='enabled',),
        cfg=dict(telnet_enabled='enabled', telnet_port=9997,),
        ap_cfg=dict(ip_addr=AP_IP, https=True,),
        apcli_cfg=dict(ip_addr=AP_IP, port=9997, telnet=True, force_telnet=True),
        expected=dict(web=True, cli=True, cfg_match=True),
    ),
    # telnet: disabled
    dict(
        ap_ip=AP_IP,
        precfg=dict(telnet_enabled='enabled', telnet_port=23,
                    https_enabled='enabled',),
        cfg=dict(telnet_enabled='disabled',),
        ap_cfg=dict(ip_addr=AP_IP, https=True,),
        apcli_cfg=dict(ip_addr=AP_IP, port=23, telnet=True, force_telnet=True),
        expected=dict(web=True, cli=False, cfg_match=True),
    ),

    # ssh: enabled, default port
    dict(
        ap_ip=AP_IP,
        precfg=dict(ssh_enabled='disabled', ssh_port=9996,
                    telnet_enabled='disabled', https_enabled='enabled',),
        cfg=dict(ssh_enabled='enabled', ssh_port=22,),
        ap_cfg=dict(ip_addr=AP_IP, https=True,),
        apcli_cfg=dict(
                ip_addr=AP_IP, port=23, telnet=False, ssh_port = 22,
        ),
        expected=dict(web=True, cli=True, cfg_match=True),
    ),
    # ssh: enabled, custom port
    # Need to update ssh port for this case (don't use default port)
    dict(
        ap_ip=AP_IP,
        precfg=dict(ssh_enabled='disabled', ssh_port=22,
                    telnet_enabled='disabled', https_enabled='enabled',),
        cfg=dict(ssh_enabled='enabled', ssh_port=9996,),
        ap_cfg=dict(ip_addr=AP_IP, https=True,),
        apcli_cfg=dict(
            ip_addr=AP_IP, port=23, telnet=False, ssh_port = 9996,
        ),
        expected=dict(web=True, cli=True, cfg_match=True),
    ),
    # ssh: disabled
    dict(
        ap_ip=AP_IP,
        precfg=dict(ssh_enabled='enabled', ssh_port=22,
                    https_enabled='enabled',),
        cfg=dict(ssh_enabled='disabled',),
        ap_cfg=dict(ip_addr=AP_IP, https=True,),
        apcli_cfg=dict(ip_addr=AP_IP, port=23, telnet=False,ssh_port=22),
        expected=dict(web=True, cli=True, cfg_match=True),
    ),
]#[testcase]


class FMDV_Mgmt_WebCLI(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)

        self.ap.start()
        logging.info('Trying to set Mgmt to pre-config on AP')
        try:
            lib.ap.acc.set(self.ap, self.p['precfg'])
        except:
            logging.debug('It seems Mgmt is in pre-config state')
            log_trace()
        self.ap.stop()
        wait_for('AP to re-start services', 20)
        wait_for_sync(self.dv, self.p['precfg'], lib.fmdv.access.get, 15, 10)
        # TODO: reboot the AP here for avoiding the side effect
        # or increasing the time for FM recorgnize AP side changes?


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
        if self.dv and self._ap:
            if self.p['web_testcase']:
                logging.info('Reboot the AP before restoring default configs')
                reboot_ap(dict(ip_addr=self.p['ap_ip']))

            logging.info('Trying to set Mgmt to default config on AP web UI')
            self._ap.start()
            lib.ap.acc.reset(self._ap, self.p['cfg_ks'])
            self._ap.stop()
            wait_for('AP to re-start services', 20)

            default_cfg = to_str_dict_items(
                dict_by_keys(self.dv.access_mgmt, self.p['cfg_ks']))
            #log('Mgmt config - default:\n%s\n' % pformat(default_cfg))

            wait_for_sync(self.dv, default_cfg, lib.fmdv.access.get, 15, 10)
            self.fm.cleanup_device_view(self.dv)
        else:
            logging.debug('Not sure why we are here! Must be an exception')
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg
        #self.p = test_cfg[cfg['testcase']] # for debugging

        init_coms(
            self,
            dict(tb=self.testbed, ap_ip=self.p['ap_ip'],dv_ip=self.p['ap_ip'],)
        )
        # these for creating the AP web UI
        self.p['ap_cfg'].update(dict(
            model=self.ap.config['model'],
            sm=self.tb.selenium_mgr,
            browser_type='firefox',
        ))

        self.p.update(dict(
            cfg_ks=join_keys(self.p['precfg'], self.p['cfg']),
            ap_mgmt_cfg={}, # web == False or 'na'
            result=dict(web='na' ,cli='na', cfg_match='na',),
            web_testcase=False if 'apcli_cfg' in self.p else True, # for restarting ap
        ))
        self._ap = None # this for cross checking after-ward
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _cfg_access(self):
        '''
        it is expected that this config can not be set
        so an exception is expected here
        '''
        logging.info('Provisioning the mgmt config from device view')
        log('Config:\n%s' % pformat(self.p['cfg']))
        if not lib.fmdv.access.set(self.dv, self.p['cfg'])[0]:
            raise Exception('Failed to set Mgmt config from Device View')
        wait_for('AP to re-start services', 20)


    def _create_ap(self, cfg):
        logging.info('Creating AP WebUI (%s) for checking up' % cfg['ip_addr'])
        return create_com(cfg['model'], cfg, cfg['sm'], https=cfg['https'])


    def _create_apcli(self, cfg):
        '''
        TODO:
        . add a note to describe the telnet/force params, why they are there?
        '''
        p = dict(telnet=False, force_telnet=True,)
        p.update(cfg)
        logging.info('Creating AP WebUI (%s) for checking up' % cfg['ip_addr'])
        log('AP CLI Config: %s' % pformat(p))
        ap = None
        try:
            ap = RuckusAP(p)
        except socket.error:
            log_trace() # for debugging
        return ap


    def _get_apcfg(self, ks):
        ''' get the apcfg from web UI '''
        logging.info('Get the mgmt config from AP WebUI...')
        #log('Config keys: %s' % pformat(ks))
        apcfg = lib.ap.acc.get(self._ap, ks)
        log('AP mgmt configs:\n%s\n' % pformat(apcfg))
        return apcfg


    def _get_results(self):
        '''
        . go to AP WebUI to get the mgmt config
        . check up CLI for conectivity (if required)
        '''
        r = self.p['result']
        self._ap = self._create_ap(self.p['ap_cfg'])
        try:
            self._ap.start()
            r['web'] = True
        except:
            r['web'] = False
            self._ap.stop()

        if r['web'] == True: # force, to ignore 'na' case
            self.p['ap_mgmt_cfg'] = self._get_apcfg(self.p['cfg'].keys())
            self._ap.stop()

        if self.p['expected']['cli'] != 'na': # testing cli
            self._cli = self._create_apcli(self.p['apcli_cfg'])
            r['cli'] = True if self._cli else False
            del self._cli


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
        r, e = self.p['result'], self.p['expected']
        r['cfg_match'] = 'na' if e['cfg_match'] == 'na' \
            else self._is_match(self.p['cfg'], self.p['ap_mgmt_cfg'])
        log('\nExpected: %s\nResult:   %s\n' % (e, r))

        msg = ' '.join([msg_cfg[k][0] % msg_cfg[k][1][v]
                           for k, v in r.iteritems()
                           if k in msg_cfg and v in msg_cfg[k][1]])
        if r == e:
            self.passmsg = msg
            return
        self.errmsg = msg
        return
