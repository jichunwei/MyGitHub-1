import time
import logging
import tempfile
import pdb
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.utils import try_interval
from pprint import pformat
import libIPTV_TestConfig as tconfig
import libIPTV_TestMethods as tmethod

class Reboot_BootRom(Test):
    required_components = ['RuckusAPSerial']

    def config(self, conf):
        self._defineTestParams(conf)
        self._getActiveAP(conf)

        if self.bootup_time:
            self._getStations(conf)
            self._get_ip_addrs(conf)
            self._getADConfig(conf)

        if self.isAP5GHz: self.dfs_info = self.active_ap.get_dfs_info(self.wlan_if)

    def test(self):
        interval = time.strftime("%Y/%m/%d %H:%M:%s", time.localtime())
        if self.reboot_from_cli:
            msg = "[%s]: Reboot AP from CLI continuously for %s hours" % (interval, self.period)
            return self._reboot24Hours(msg, self.active_ap.reboot)

        if self.power_cycle:
            logging.info("AP is connecting to port %s on the Power MGMT" % self.port)
            msg = "[%s]: Power cycle AP continuously for %s hours" % (interval, self.period)
            return self._reboot24Hours(msg, self.active_ap.power_cycle,True)

        if self.bootrom:
            msg = "[%s]: Reboot AP from bootrom continuously for %s hours" % (interval, self.period)
            return self._reboot24Hours(msg, self.active_ap.reboot_boot_rom)

        if self.manual_boot_bkup: return self._load_image(False, 2, 1)
        if self.manual_boot_main: return self._load_image(True, 1, 2)

        if self.boot_script: return self._bootScript()
        if self.boot_from_network: return self._bootViaNetwork()

        if self.antenna: return self._verifyAntennaInfo()
        if self.boardtype: return self._verifyBoardType()

        if self.dfs_scan:
            if not self.isAP5GHz:
                msg = "Can not check DFS scanning because AP does not support radio 5GHz. "
                msg += "Skip this test"
                return ["", msg]
            return self._checkDFSScanTime()
        if self.bootup_time: return self._bootWithTraffic()

    def cleanup(self):
        if self.boot_from_network:
            self.active_ap.reboot()

        if self.remote_sta and self.local_sta:
            logging.info("Kill iperf server process on the remote station %s" % self.remote_ip_addr)
            self.remote_sta.stop_iperf()

            logging.info("Down svcp interface on the active Adapter")
            self.remote_sta.set_ruckus_ad_state(self.ad_conf, 'down', 'wlan0')

        if self.active_ap:
            if self.wlan_if:
                logging.info("Down interface %s on the active AP" % self.wlan_if)
                self.active_ap.set_state(self.wlan_if, 'down')
        logging.info("---------- FINISH ----------")

    def _defineTestParams(self, conf):
        if conf.has_key('power_cycle'):
            self.power_cycle = conf['power_cycle']
            self.period = conf['period']
            self.port = conf['port']
            self.pwr_mgmt = self.testbed.pwr_mgmt
            self.pwr_mgmt['port'] = self.port

        else: self.power_cycle = False

        if conf.has_key('reboot_from_cli'):
            self.reboot_from_cli = conf['reboot_from_cli']
            self.period = conf['period']
        else: self.reboot_from_cli = False

        if conf.has_key('manual_boot_main'):
            self.manual_boot_main = conf['manual_boot_main']
        else: self.manual_boot_main = False

        if conf.has_key('manual_boot_bkup'):
            self.manual_boot_bkup = conf['manual_boot_bkup']
        else: self.manual_boot_bkup = False

        if conf.has_key('boot_from_network'):
            self.boot_from_network = conf['boot_from_network']
        else: self.boot_from_network = False

        if conf.has_key('bootrom'):
            self.bootrom = conf['bootrom']
            self.period = conf['period']
        else: self.bootrom = False

        if conf.has_key('boot_script'):
            self.boot_script = conf['boot_script']
        else: self.boot_script = False

        if conf.has_key('boardtype'):
            self.boardtype = conf['boardtype']
        else: self.boardtype = ""

        if conf.has_key('antenna'):
            self.antenna = conf['antenna']
        else: self.antenna = ""

        if conf.has_key('dfs_scan'):
            self.dfs_scan = conf['dfs_scan']
        else: self.dfs_scan = False

        if conf.has_key('bootup_time'):
            self.bootup_time = conf['bootup_time']
        else: self.bootup_time = False

        if conf.has_key('wlan_if'): self.wlan_if = conf['wlan_if']
        else: self.wlan_if = ''

        if conf.has_key('isAP5GHz'):
            self.isAP5GHz = conf['isAP5GHz']
        else: self.isAP5GHz = False

        self.remote_sta = None
        self.local_sta = None
        self.active_ap = None
        self.ad_conf = {}
        self.ap_ethinterface = ""

        self.timeout = 300
        self.bw = '4m'

    def _load_image(self, main, new_bootid, forced_bootid):
        if main: txt = "main"
        else: txt = 'back up'
        logging.info("Verify the %s image with manual boot" % txt)

        # Make sure AP's running image
        self.active_ap.goto_red_boot()
        bootid = self.active_ap.get_main_image_id()

        txt_now = ""
        if bootid == new_bootid:
            self.active_ap.set_main_image_id(forced_bootid)
            self.active_ap.exit_red_boot()

            time.sleep(1)
            fw_setting = self.active_ap.get_fw_upgrade_setting()
            if main: txt_now = 'back up'
            else: txt_now = 'main'
            t = 'image%s' % forced_bootid
            if fw_setting['running_image'].lower() != t.lower():
                return ["FAIL", "Can not force AP to run %s image" % txt_now]
            self.active_ap.goto_red_boot()
        else:
            if main: txt_now = "bkup"
            else: txt_now = "main"

        logging.info("AP is running on %s image now" % txt_now)
        logging.info("Boot up the AP manually with %s image" % txt)
        if main: self.active_ap.load_image(True, new_bootid)
        else: self.active_ap.load_image(False, new_bootid)

        time.sleep(2)
        fw_setting = self.active_ap.get_fw_upgrade_setting()
        logging.debug("AP's image after manually boot: %s" % fw_setting['running_image'])
        t = 'image%s' % new_bootid
        if fw_setting['running_image'].lower() != t.lower():
            return ["FAIL", "Can not load AP with %s image" % txt]
        logging.info("%s image is loaded and run correctly" % txt)

        return ["PASS", ""]

    def _reboot24Hours(self, msg, f, powercycle=False):

        self.period = self.period * 3600
        logging.info(msg)
        start_time = time.time()
        cur_time = start_time
        count = 0
        while time.time() - start_time < self.period:
            try:
                if powercycle: f(self.testbed.pwr_mgmt)
                else: f()
                if f.func_name == 'reboot':
                    self.active_ap.login()
            except Exception, e:
                return ["FAIL", e.message]
            if time.time() - cur_time >= 3600:
                count += 1
                logging.info("AP have been rebooting for %d hour(s)" % count)
                cur_time = time.time()
            time.sleep(60)

        interval = time.strftime("%Y/%m/%d %H:%M:%s", time.localtime())
        logging.info("[%s]: Complete %s" % (interval, msg))
        return ["PASS", ""]

    def _bootScript(self):

        logging.info("Create and verify boot script on the AP")
        verify_ok = True
        self.active_ap.goto_red_boot()
        try:
            self.active_ap.set_boot_script(True)
        except Exception, e:
            return ["FAIL", e.message]

        res, msg = self.active_ap.run_boot_script()
        if not res:
            verify_ok = False

        time.sleep(1)
        try:
            self.active_ap.set_boot_script(False)
            self.active_ap.exit_red_boot()
        except Exception, e:
            return ["FAIL", e.message]

        if not verify_ok: return ["FAIL", msg]
        return ["PASS", msg]

    def _bootViaNetwork(self):

        logging.info("Verify the image when booting via network")

        res, msg = self.active_ap.set_boot_net_info(self.ap_ip_addr, self.testbed.ftpserv['ip_addr'])
        logging.info('set_boot_net_info return msg: %s' % msg)
        if not res: return ["FAIL", msg]
        logging.info(msg)

        res, msg = self.active_ap.boot_from_network()
        logging.info('boot_from_network return msg: %s' % msg)
        if not res: return ["FAIL", msg]
        logging.info(msg)

        return ["PASS", ""]

    def _verifyAntennaInfo(self):
        model = self.active_ap.get_model()
        logging.info("Verify antenna info for AP %s" % model)

        atinfo = self.active_ap.get_antenna_info()
        if atinfo != self.antenna:
            return ["FAIL", "Antenna info of AP %s is not correct" % model]

        logging.info("Antenna Info of AP %s is correct" % model)
        return ["PASS", ""]

    def _verifyBoardType(self):
        model = self.active_ap.get_model()
        logging.info("Verify Board Type for AP %s" % model)

        tmp = self.active_ap.get_board_type()
        if tmp != self.boardtype:
            return ["FAIL", "Board Type of AP %s is not correct" % model]

        logging.info("Board Type of AP %s is correct" % model)
        return ["PASS", ""]

    def _checkDFSScanTime(self):

        logging.info("Factory AP before checking DFS scan time")
        self.active_ap.set_factory()

        logging.info("Turn on interface %s" % self.wlan_if)
        self.active_ap.set_state(self.wlan_if, 'up')

        logging.info("Reboot AP to start measuring DFS scan time")
        self.active_ap.reboot()

        up = self._checkBSSID()
        if not up:
            return ["FAIL", "BISSD of interface %s is still not up after DFS scan time [%s seconds]" %
                    (self.wlan_if, self.dfs_info['cactime'])]
        logging.info("%s is up after DFS scan time. Correct behavior" % self.wlan_if)
        return ["PASS", ""]

    def _bootWithTraffic(self):

        logging.info("Factory AP before checking DFS scan time")
        self.active_ap.set_factory()

        logging.info("Config wlan settings for AP and AD")
        self._cfg_wlan(self.wlan_if)
        self._cfg_wlan(self.wlan_if, False, self.ad_ip_addr, self.remote_sta, self.ad_conf)

        logging.info("Turn on wlan interface so that AD can associate to the AP successfully")
        self.active_ap.set_state(self.wlan_if, 'up')
        tmethod.setADWlanState(self.remote_sta,
                               self.ad_conf, "up",
                               self.ad_model, self.ad_ip_addr)

        if self.isAP5GHz:
            if not self._checkBSSID():
                return ["FAIL", "BSSID of wlan %s is still zero after DFS scanning" % self.wlan_if]
        time.sleep(2)

        logging.info("Start iperf to stream traffic between 2 stations to create traffic online")
        self.remote_sta.start_iperf(test_udp = True)
        self.local_sta.start_iperf(serv_addr = self.remote_ip_addr,
                                  test_udp = True,
                                  timeout = self.timeout, bw = self.bw)
        time.sleep(10)
        logging.info("Reboot the AP to check boot up time while having traffic online")
        self.active_ap.reboot()

        if self.isAP5GHz:
            if not self._checkBSSID():
                return ["FAIL", "BSSID of wlan %s is still zero after AP boots up and DFS scans" % self.wlan_if]
        else:
            bssid = tmethod.getBSSID(self.active_ap, self.wlan_if)
            if bssid == "00:00:00:00:00:00":
                return ["FAIL", "BSSID of wlan %s is still zero after AP boots up" % self.wlan_if]
        logging.info("Interface %s is up immediately after AP reboot" % self.wlan_if)

        # Verify station list. Need to wait a mement for AD associate to AP
        # The wait time depends on each AP model but as manual guy's experience,
        # it should not longer than 2 mins
        stalist, wait_interval = [], 120
        for i in try_interval(wait_interval, 10):
            stalist = self.active_ap.get_station_list(self.wlan_if)
            print '%s. stalist: %s' % (i, stalist)
            if stalist: break
            
        assoc = False
        for sta in stalist:
            if self.ad__mac in sta:
                assoc = True
                break
        if not assoc: return ["FAIL", "Information of station does not appear in station list after %s(s)" % wait_interval]

        # Start tcpdump on linux station
        fo, tcpdump_info = tempfile.mkstemp(".txt")
        self.remote_sta.start_tcp_dump(ip_addr = self.remote_ip_addr,
                                     proto = 'udp',
                                     count = '100',
                                     file_path = tcpdump_info)
        time.sleep(10)
        capture_res = tmethod.findCapturedPacket(self.remote_sta,
                                                 tcpdump_info,
                                                 self.local_ip_addr,
                                                 self.remote_ip_addr)
        if not capture_res: return ["FAIL", "[Station %s]: does not receive traffic after AP boots up" % self.remote_ip_addr]

        logging.info("[STA %s]: receive traffic immediately after AP reboots" % self.remote_ip_addr)
        return ["PASS", ""]

    def _cfg_wlan(self, wlan_if = "", on_ap = True, ad_ip_addr = "", sta_obj = None, ad_config = {}):
        wlan_cfg = dict(auth="open",
                        encryption="none",
                        ssid='DFS_SCAN_TIME',
                        wlan_if='%s' % wlan_if)
        if on_ap:
            logging.info("Configure a WLAN with SSID %s on the active AP" % wlan_cfg['ssid'])
            self.active_ap.cfg_wlan(wlan_cfg)
        else:
            ad_wlan_cfg = wlan_cfg.copy()
            ad_wlan_cfg['wlan_if'] = 'wlan0'
            logging.info("Configure a WLAN with SSID %s on Adapter %s" % (wlan_cfg['ssid'], ad_ip_addr))
            sta_obj.cfg_wlan(ad_config, ad_wlan_cfg)

    def _getStations(self, conf):
        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.remote_sta = tconfig.getStation(conf['remote_sta'], station_list)
        self.local_sta = tconfig.getStation(conf['local_sta'], station_list)

    def _get_ip_addrs(self, conf):

        error_msg = "Can not find any ip addresses belong to subnet %s" % self.testbed.sta_wifi_subnet['network']

        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['ad_linux'])

        # Find the ip address of interface that connected to the adapter on the local station and remote station
        self.local_ip_addr, self.local_ifname = tconfig.getLinuxIpAddr(self.local_sta,
                                                                      self.testbed.sta_wifi_subnet, True)
        self.remote_ip_addr, self.remote_ifname = tconfig.getLinuxIpAddr(self.remote_sta,
                                                                        self.testbed.sta_wifi_subnet, True)
        if not self.local_ip_addr or not self.remote_ip_addr:
            raise Exception("[Linux STAs]: %s" % error_msg)

    def _getADConfig(self, conf):

        # Get adapter configuration information
        self.ad_conf = tconfig.getADConfig(self.testbed,
                                           conf['ad_linux'],
                                           self.testbed.ad_list,
                                           "AD behind Linux")
        self.ad__mac = self.remote_sta.get_ad_wireless_mac(self.ad_conf)
        self.ad_model = self.remote_sta.get_ad_device_type(self.ad_conf)

    def _getActiveAP(self, conf):
        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        logging.info("Find the active AP object")
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, conf['active_ap'],
                                                    self.testbed.components['AP'], "", "")
        if self.bootup_time:
            ethlist = self.active_ap.get_all_eth_interface()
            for interface in ethlist:
                if interface['status'] == 'up':
                    self.ap_ethinterface = interface['interface']

    def _checkBSSID(self):
        start_time = time.time()
        up = False
        while time.time() - start_time < self.dfs_info['cactime']:
            bssid = tmethod.getBSSID(self.active_ap, self.wlan_if)
            if bssid != "00:00:00:00:00:00":
                up = True
                break
            if up: break
            time.sleep(0.3)

        return up
