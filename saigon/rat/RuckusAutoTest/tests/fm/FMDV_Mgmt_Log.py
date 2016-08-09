import logging
import re
import copy
from pprint import pformat

from RuckusAutoTest.common.utils import (
    wait_for, join_keys, log_trace, log,
    to_str_dict_items,
)
from RuckusAutoTest.tests.fm.lib_FM import init_coms
from RuckusAutoTest.components import Helpers as lib

from RuckusAutoTest.models import Test


'''
Typical logs
    May 21 14:26:11 RuckusAP syslog.info syslogd started: BusyBox v1.01 (2009.03.20-22:36+0000)
    May 21 14:26:21 RuckusAP user.info kernel: br0: port 3(wlan0) entering learning state
    May 21 14:26:22 RuckusAP user.warn kernel: ath_newstate: starting calibration interval=180000
    May 21 14:26:22 RuckusAP user.warn kernel: NF Ch0 -79[-79],-79[-50]
    May 21 14:26:22 RuckusAP user.warn kernel: NF Ch1 -79[-79],-79[-50]
    May 21 14:26:22 RuckusAP user.warn kernel: NF Ch2 -79[-79],-79[-50]
    May 21 14:26:22 RuckusAP user.warn kernel: wifi0: 9209276 : stuck beacon; resetting (bmiss count 157) nfcal_low=-76, scanning 0, syncbeacon 0, sc_beacons 1
    May 21 14:26:22 RuckusAP user.info kernel: ar5416AniInit: Reset ANI state opmode 6
    May 21 14:26:22 RuckusAP user.info kernel: br0: topology change detected, propagating
    May 21 14:26:22 RuckusAP user.info kernel: br0: port 3(wlan0) entering forwarding state
    May 21 14:26:22 RuckusAP user.info kernel: br0: port 3(wlan0) entering disabled state
    May 21 14:26:22 RuckusAP user.warn kernel: rks_ath_war_set_allow_upaggr: iwconfig allow upaggr wlan0 Wireless1 00:22:7f:18:1e:88
    May 21 14:26:22 RuckusAP user.info kernel: ar5416AniInit: Reset ANI state opmode 6
    May 21 14:26:22 RuckusAP user.info kernel: br0: port 3(wlan0) entering learning state
    May 21 14:26:22 RuckusAP user.info kernel: ar5416GetNf: Failed to Latch NF: agcctl 0x41d1a
    May 21 14:26:23 RuckusAP user.info kernel: br0: topology change detected, propagating
    May 21 14:26:23 RuckusAP user.info kernel: br0: port 3(wlan0) entering forwarding state
    May 21 14:26:24 RuckusAP user.warn kernel: ath_newstate: starting calibration interval=180000
    May 21 14:27:06 RuckusAP user.info kernel: br0: port 3(wlan0) entering disabled state

example of LOG_RE:
  May 21 14:26:11 RuckusAP syslog.info syslogd started: BusyBox v1.01 (2009.03.20-22', '36+0000)
returns:
  ('May 21 14:26:11',
   'syslogd started: BusyBox v1.01 (2009.03.20-22:36+0000)')
'''
LOG_RES = ['syslogd started: BusyBox',
           'entering learning state',
           'topology change detected',
           'entering forwarding state',
           'entering disabled state',
           ]
AP_LOG_RE =  '(.* \d+:\d+:\d+)[^:]*?: (.*)'
# Tu Bui: logs get from server is a list. I create a function to
# convert this list to format like log from AP
SRV_LOG_RE = '%s' % AP_LOG_RE # '\r', the only diff, is removed
#SRV_LOG_RE = '%s\r' % AP_LOG_RE # '\r', the only diff, is removed
MAX_SYSLOG_NETWORK_LEVEL = 7


msg_cfg = dict(
    local=('Log messages are %s on local.',
           { True: 'found', False: 'NOT found', }),
    server=('Log messages are %s on server.',
            { True: 'found', False: 'NOT found', }),
    cfg_match=('Log config on FM Device View and AP is %s.',
               { True: 'matched', False: 'NOT matched', }),
    log_match=('Log messages on local and server are %s.',
               { True: 'matched', False: 'NOT matched', }),
)


class FMDV_Mgmt_Log(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)

        logging.info('Restarting syslogd with remote reception on linux server')
        self.srv_cli.restart_syslog()

        logging.info('Setting AP\'s syslog network level to maximum (%s)' % \
                     MAX_SYSLOG_NETWORK_LEVEL)
        self.ap_cli.set_syslog_network_level(MAX_SYSLOG_NETWORK_LEVEL)

        logging.info('Trying to set Mgmt > Log to pre-config on device view')
        try:
            lib.fmdv.access.set(self.dv, self.p['log_precfg'])
            wait_for('Mgmt config to be pushed to AP', 10)
        except:
            logging.debug('It seems Mgmt > Log is in pre-config state')
            log_trace()
        lib.fmdv.access.nav_to(self.dv, force=True)


    def test(self):
        self._clear_syslog_msgs()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._cfg_access()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._gen_syslog_msgs()
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
        if self.srv_cli:
            logging.info('Restarting syslogd with default options')
            self.srv_cli.restart_syslog()
            del self.srv_cli
        if self.ap_cli:
            logging.info('Restoring syslogd network level')
            self.ap_cli.set_syslog_network_level(3)
            del self.ap_cli
        if self.dv:
            try:
                logging.info('Trying to set Mgmt > Log to default config on device view')
                lib.fmdv.access.reset(self.dv, self.p['restore_ks'])
            except:
                log_trace()
            self.fm.cleanup_device_view(self.dv)
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = copy.deepcopy(cfg) # test_cfg # remove on production
        #update_dict(self.p, cfg)

        init_coms(
            self,
            dict(tb=self.testbed, ap_ip=self.p['ap_ip'],dv_ip=self.p['ap_ip'],
                 apcli_cfg=dict(ip_addr=self.p['ap_ip']),
                 srv_cfg=self.p['srv_cfg']),
        )
        self.p['log_ks'] = join_keys(self.p['log_precfg'], self.p['log_cfg'])
        self.p['restore_ks'] = ['log_enabled']
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _clear_syslog_msgs(self):
        logging.info('Clear syslog messages on linux server')
        self.srv_cli.clear_syslog_messages()


    def _cfg_access(self):
        logging.info('Provisioning the log config from device view')
        logging.debug('Log config:\n%s' % pformat(self.p['log_cfg']))
        if not lib.fmdv.access.set(self.dv, self.p['log_cfg'])[0]:
            raise Exception('Failed to set Mgmt config from Device View')


    def _gen_syslog_msgs(self):
        '''
        enabling/disabling a wlan to generate syslog messages
        '''
        logging.info('Enable then disable a WLAN for generating syslog messages')
        try:
            lib.fmdv.wlan.cfgWLAN(self.dv, 1, dict(avail='enabled'))
            wait_for('WLAN to be enabled.', 6)
        except Exception:
            logging.info('The wlan is already enabled. Disable it.')
            # it is already enabled, disable and enable again
            lib.fmdv.wlan.cfgWLAN(self.dv, 1, dict(avail='disabled'))
            wait_for('WLAN to be disabled.', 6)

            lib.fmdv.wlan.cfgWLAN(self.dv, 1, dict(avail='enabled'))
            wait_for('WLAN to be enabled.', 6)

        lib.fmdv.wlan.cfgWLAN(self.dv, 1, dict(avail='disabled'))
        wait_for('WLAN to be disabled.', 2)


    def _get_results(self):
        '''
        go to AP WebUI/Linux server to get the log
        '''
        logging.info('Get the config/logs from AP WebUI.')
        ks = self.p['log_cfg'].keys() + ['logs']
        self.ap.start()
        self.p['ap_log_cfg'] = lib.ap.acc.get(self.ap, ks)
        self.p['ap_logs'] = self.p['ap_log_cfg'].pop('logs')
        self.ap.stop()
        wait_for('all AP\'s logs are sent to Syslog server', 5)
        logging.info('Get the config/logs from Syslog Server.')
        self.p['srv_logs'] = self.srv_cli.get_syslog_messages()

        log('AP Log config:\n%s\n' % pformat(self.p['ap_log_cfg']))
        log('AP logs:\n%s\n' % pformat(self.p['ap_logs']))
        log('Server logs:\n%s\n' % pformat(self.p['srv_logs']))


    def _is_match(self, logs):
        for p in LOG_RES:
            if not re.search(p, logs):
                return False
        return True


    def _clean_up_spaces(self, cfg):
        ''' removing duplicate spaces/tabs for better comparision '''
        _cfg = []
        for i in cfg:
            _cfg.append([re.sub('[ \t]+', ' ', j) for j in i])
        #log_cfg(cfg)
        return _cfg


    def _is_cfg_match(self, testcfg, apcfg):
        testcfg = to_str_dict_items(testcfg)
        apcfg = to_str_dict_items(apcfg)
        if apcfg != testcfg:
            logging.info('Log config on AP does NOT match test log config')
            logging.debug('Test log config:\n%s\nAP log config:\n%s\n' % \
                          (pformat(testcfg), pformat(apcfg)))
            return False
        return True


    def _is_log_match(self, aplogs, srvlogs):
        '''
        are all ap_logs in srv_logs?
        '''
        _aplogs = self._clean_up_spaces(re.findall(AP_LOG_RE, aplogs))
        _srvlogs = self._clean_up_spaces(re.findall(SRV_LOG_RE, srvlogs))

        log('AP logs:\n%s\n' % pformat(_aplogs))
        log('Server logs:\n%s\n' % pformat(_srvlogs))
        # if both are the same then it is too good, optimal case
        # otherwise, make sure all ap logs are on server
        if _aplogs == _srvlogs:
            return True
        for i in _aplogs:
            if i not in _srvlogs:
                return False
        return True


    def _test_results(self):
        '''
        based on the expected, deciding testing pass or fail
        . are all the expected logs in ap_logs/srv_logs?
        NOTE:
          right now, just check the syslog message restarted
          for the rest, will be consider to check in the future
        '''
        e = self.p['expected']
        logging.info('Comparing the result with expected..')
        # Tu Bui: logs get from server is a list. Change it to string
        #server_log_str = str(self.p['srv_logs']).strip('[,]')
        server_log_str = unicode("\n".join(self.p['srv_logs']))

        r = dict(
            local =self._is_match(self.p['ap_logs']),
            server=self._is_match(server_log_str),
            cfg_match='na' if e['cfg_match'] == 'na'
                else self._is_cfg_match(self.p['log_cfg'], self.p['ap_log_cfg']),
            log_match='na' if e['log_match'] == 'na'
                else self._is_log_match(self.p['ap_logs'], server_log_str),
        )
        logging.debug('\nExpected: %s\nResult:   %s\n' % (e, r))

        msg = ' '.join([msg_cfg[k][0] % msg_cfg[k][1][v]
                           for k, v in r.iteritems()
                           if k in msg_cfg and v in msg_cfg[k][1]])
        if r == e:
            self.passmsg = msg
            return
        self.errmsg = msg
        return
