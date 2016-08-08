# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to test spectralink phone with different encryption
Author: Jason Lin
Email: jlin@ruckuswireless.com
Test Parameters: {'filename': file name for save capturing packets,
                              default is tb.name+'_'+phone_ssid+'.pkt',
                  'duration': capture stop after NUM seconds,
                  'inf': use this interface to capture, '1' }
example:{'duration': 500, 'inf': '1'}
Result type:PASS/FAIL
Results:PASS:launch tshark on station
        FAIL:

Test Procedure:
1. config:
   -
2. test:
   - launch tshark on station
3. cleanup:
   -
"""
import logging
from RuckusAutoTest.models import Test

class CB_ZD_Start_Sniffer_On_Station(Test):

    def config(self, conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self._restartAdapterOnStation()
        self._reconfigChannelOnAirPcap()
        self._startCapturePktsOnStation()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag['sniffer_enable']=True
        msg = 'Start Tshark to Sniffer Packets on Station [%s] Successfully' % self.target_station.sta_ip_addr
        return self.returnResult('PASS', msg)

    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = conf.copy()
        self.tb_name = self.testbed.testbed_info.name
        self.zd = self.testbed.components['ZoneDirector']
        self.zd_version = self.zd._get_version()['version']
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.ap_model = self.carrierbag[self.conf['ap_tag']]['ap_ins'].get_ap_model()
        self.filename = self.conf['filename'] if self.conf.has_key('filename') else \
                        self.tb_name + '_' + self.ap_model + '_' + self.conf['dut_phone'] + '.pkt'
        self.skl_file = self.conf['skl_file']

    def _restartAdapterOnStation(self):
        logging.info('Restart CACE Adapter on Station')
        return self.target_station.restart_adapter()

    def _reconfigChannelOnAirPcap(self):
        logging.info('Reconfigure channel on airpcap dongle')
        param_dict = dict(skl_file=self.skl_file)
        param_str = str(param_dict)
        return self.target_station.do_cmd('airpcap_channel_config_by_sikuli', param_str)

    def _startCapturePktsOnStation(self):
        logging.info('Launch Tshark to sniffer packets on station [%s]' % self.target_station.sta_ip_addr)
        fcfg=dict(infname='airpcap_any', filename=self.filename, duration='400', pkts_folder=self.zd_version)
        fcfg.update(self.conf)
        param_dict = dict(infname=fcfg['infname'], filename=fcfg['filename'], duration=fcfg['duration'], ether_host=fcfg['phone_mac'], pkts_folder=fcfg['pkts_folder'])
        param_str = str(param_dict)
        return self.target_station.do_cmd('TA.captureTrafficOTA', param_str)
