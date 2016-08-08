import time
import logging
import tempfile
import pdb
import re
from pprint import pformat

from RuckusAutoTest.models import Test
import libIPTV_TestConfig as tconfig
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common.utils import log_trace

class Cablevision(Test):
    required_components = ['RuckusAPSerial']
    parameter_description = {'active_ap':'ip address of the tested AP',
                             'local_sta':'ip address of local station',
                             'config_psk':'Decides if psk is configured and verified or not',
                             'psk':'the decryption password',
                             'wrong_psk':'the wrong decryption password',
                             'auto_upgrade':'decides if upgrade starts automatically or manually',
                             'build':'decides if build is upgraded or not',
                             'factory':'decides if control file has "set factory" command or not',
                             'encrypted':'decides if control file is encrypted or not'
    }

    def config(self, conf):
        # Define test parameters
        self._defineTestParams(conf)

        # Get active AP
        self._getActiveAP(conf)

        # Get Local station information
        if not self.config_psk: self._getStaInfo(conf)

    def test(self):
        if self.config_psk:
            return self._configPSK()
        else:
            logging.info("Remove the all current custom files out of the AP")
            self.active_ap.remove_all_custom_file()

            if self.auto_upgrade: return self._autoUpgrade()
            else: return self._manualUpgrade()

    def cleanup(self):
        if self.active_ap and not self.config_psk:
            if not self.wrong_psk:
                logging.info("Remove custom file out of the AP")
                self.active_ap.remove_all_custom_file()

        if not self.config_psk:
            os.remove("%s" % self.ctrl_file)
            os.remove("%s/%s" % (self.ftpserv['rootpath'], self.ipfname))
            os.remove("%s/%s" % (self.ftpserv['rootpath'], self.opfname_woencrypt))
            if self.encrypted:
                os.remove("%s/%s" % (self.ftpserv['rootpath'], self.opfname_wencrypt))
            if self.tcpdump_info: os.remove(self.tcpdump_info)
            if self.build: os.remove("%s/%s" % (self.ftpserv['rootpath'],self.build))

    def _manualUpgrade(self):
        self._prepareFiles()

        self.fw_conf['control'] = self.ctrl_file
        logging.info("Configure fw upgrade settings")
        self.active_ap.change_fw_setting(self.fw_conf)

        if not self.wrong_psk:
            self._startTcpdump()
            time.sleep(2)

        if self.encrypted:
            if self.wrong_psk: msg = "Try to update encrypted custom file with wrong psk manually"
            else: msg = "Update encrypted custom file manually"
        else: msg = "Update non-encrypted custom file manually"
        logging.info(msg)

        success = False
        try:
            self.active_ap.upgrade_sw(100, True, False)
        except Exception, e:
            log_trace()
            if self.wrong_psk:success = True
            else: raise e

        if self.wrong_psk:
            if not success: return ["FAIL", "Encrypted custom file with wrong PSK is still upgraded. Incorrect Behavior"]
            else:
                logging.info("Could not upgrade encrypted custom file because of wrong PSK. Correct Behavior")
                return ["PASS", ""]

        # Stop tcpdump
        time.sleep(10)
        self.local_sta.stop_tcp_dump()

        logging.info("Verify that custom file is upgraded successfully")
        if not self.active_ap.verify_custom_file_shell():
            return ["FAIL", "Expected custom file is not appeared in directory /writable/custom after upgrading"]
        logging.info("Upgrade custom file successfully")

        logging.info("Verify that custom file is not activated after upgrading manually")
        if not self._verifyCustomFile():
            return ["FAIL", "[Manual Upgrade]: Custom file is activated while AP has not rebooted yet"]
        logging.info("[Manual Upgrade]: Until now custom file is not activated. Correct behavior")

        res, msg = self._analyzeData()
        if res == "FAIL": return [res, msg]

        logging.info("Activate Custom file and verify its configuration applied to AP")
        self.active_ap.set_factory()
        return self._logCheckCustomFile()

    def _autoUpgrade(self):
        msg = "[Auto Upgrade]"
        # Save fw setting before upgrade custom file with command 'set factory'
        if self.factory:
            old_fw = self.active_ap.get_fw_upgrade_setting()

        self.fw_conf.update(dict(firstcheck=self.firstcheck))
        logging.info("Configure fw upgrade settings")
        self.active_ap.change_fw_setting(self.fw_conf)

        if self.build:
            self.build = self.local_sta.create_copy_image(self.build, name="cablevision%s" % int(time.time()))
            self.active_ap.change_fw_setting({'auto':True})

        logging.info("Reboot AP before auto upgrading")
        self.active_ap.reboot()
        time.sleep(3)

        self._prepareFiles()
        self.active_ap.change_fw_setting({'control':'%s' % self.ctrl_file})

        if not self.build and not self.factory:
            if not self.wrong_psk:
                self._startTcpdump()
                logging.info("%s: with encrypted custom file" % msg)
            else: logging.info("%s: With encrypted custom file and wrong PSK" % msg)

        # check auto upgrade interval
        tres = self.active_ap.is_auto_upgrade(int(self.firstcheck)*60*2)

        if self.build:
            logging.info("%s: Verify that AP will upgrade firmware first then continue upgrading custom file" % msg)
            if not tres:
                fmsg = "Auto upgrade [both firmware and custom file] does not start "
                fmsg += "after %s minute(s) [firstcheck time]" % self.firstcheck
                return ["FAIL", fmsg]

            if tres['upgrade_custom']:
                fmsg = "AP automatically upgrades custom file before upgrading firmware. Incorrect behavior"
                return ["FAIL", fmsg]

            # Verify if Ap automatically reboot after upgrade
            res, rmsg = self._logAutoReboot("Firmware")
            if res == "FAIL": return [res, rmsg]
            logging.info("%s: AP upgraded firmware first. Correct behavior" % msg)

            atup_custom = self.active_ap.is_auto_upgrade(int(self.firstcheck)*60)
            if not atup_custom or not atup_custom['upgrade_custom']:
                fmsg = "AP does not automatically upgrade custom file after upgrade firmware"
                return ["FAIL", fmsg]
            res, rmsg = self._logAutoReboot("Custom File")
            if res == "FAIL": return [res, rmsg]
            logging.info("%s: Then AP continues to upgrade custom file successfully" % msg)

            logging.info("%s: AP upgrades firmware and custom file orderly correctly" % msg)
            return ["PASS", ""]

        if self.factory:
            logging.info("Verify auto upgrade the custom file with command 'set factory'")
            res, rmsg = self._logAutoReboot()
            if res == "FAIL": return [res, rmsg]

            # Get current fw settings
            current_fw = self.active_ap.get_fw_upgrade_setting()
            for key in current_fw.keys():
                if current_fw[key] != old_fw[key]:
                    fmsg = "%s: Although AP already applied factory reset " % msg
                    fmsg += "but old configuration has been still existed"
                    return ["FAIL", fmsg]

            fmsg = self._verifyCustomFile()
            if fmsg:
                return ["FAIL", "%s. Custom file is activated but its configuration is not applied to AP correctly" % fmsg]

            pmsg = "AP automatically factory resets and apply the configuration from new custom file. Correct behavior"
            logging.info(pmsg)
            return ["PASS", ""]

        if self.wrong_psk:
            if tres:
                return ["FAIL", "AP still performs auto upgrade custom file although PSK is wrong. Incorrect behavior"]
            logging.info("%s: Because of wrong PSK, the auto upgrade does not complete. Correct Behavior" % msg)
            return ["PASS", ""]

        else:
            if not tres:
                return ["FAIL", "Auto upgrade does not start after %s minute(s) [firstcheck time]" %
                        self.firstcheck]
            logging.info("AP starts auto upgrade after %s minute(s) [firstcheck time]. Correct behavior" %
                         self.firstcheck)

            # Verify automatically reboot
            res, rmsg = self._logAutoReboot()
            if res == "FAIL": return [res, rmsg]

            # Stop tcpdump
            self.local_sta.stop_tcp_dump()

            res, rmsg = self._analyzeData()
            if res == "FAIL": return [res, rmsg]

            logging.info("%s: Verify configuration in custom file is applied to AP correctly" % msg)
            return self._logCheckCustomFile()

    def _defineTestParams(self, conf):
        if conf.has_key('config_psk'):
            self.config_psk = conf['config_psk']
        else: self.config_psk = False

        if conf.has_key('psk'): self.psk = conf['psk']
        else: self.psk = ""

        if conf.has_key('wrong_psk'): self.wrong_psk = conf['wrong_psk']
        else: self.wrong_psk = ""

        if conf.has_key('build'): self.build = conf['build']
        else: self.build = ''

        if conf.has_key('factory'): self.factory = conf['factory']
        else: self.factory = False

        if conf.has_key('encrypted'): self.encrypted = conf['encrypted']
        else: self.encrypted = None

        self.auto_upgrade = conf['auto_upgrade']
        self.ftpserv = self.testbed.ftpserv

        self.ipfname = "CustomSrcFile"
        self.opfname_woencrypt = "CustomNonEncrypt"
        self.opfname_wencrypt = "CustomEncrypt"
        self.firstcheck = '2'
        self.wlan_if = 'wlan0'
        self.commands = ["set ssid %s CABLEVISION" % self.wlan_if,
                         "set state %s up" % self.wlan_if,
                         "set channel %s 6" % self.wlan_if,
                         "set snmp community ro snmpreadonly",
                         "set snmp community rw snmpreadwrite"]
        if self.factory: self.commands.append('set factory')

        self.getcmds = {'get ssid %s' % self.wlan_if:'CABLEVISION',
                        'get state %s' % self.wlan_if:'up',
                        'get channel %s' % self.wlan_if:'([0-9]+)',
                        'get snmp':'snmpreadonly',
                        'get snmp':'snmpreadwrite'}

        self.active_ap = None
        self.local_sta = None
        self.sta_ip_addr = None
        self.tcpdump_info = None
        self.ctrl_file = None

        self.fw_conf = dict(auto=self.auto_upgrade,
                            control='',
                            host=self.ftpserv['ip_addr'],
                            proto='ftp',
                            user=self.ftpserv['username'],
                            password=self.ftpserv['password'],
                            psk=self.psk)

    def _getActiveAP(self, conf):
        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])

        logging.info("Find the active AP object")
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, conf['active_ap'],
                                                    self.testbed.components['AP'], "", "")

        self.ap_profile = self.active_ap.get_profile()

    def _getStaInfo(self, conf):
        self.local_sta = tconfig.getStation(conf['local_sta'], self.testbed.components['Station'])

        subnet = get_network_address(self.ap_ip_addr)
        self.sta_ip_addr = tconfig.getLinuxIpAddr(self.local_sta, subnet)
        if not self.sta_ip_addr:
            raise Exception("[Linux STAs]: Can not find any ip addresses belong to subnet %s" % subnet)

    def _prepareFiles(self):
        """
        Create custom file and control file
        """
        # Create custom source file
        self._createCustomSrcFile()

        if self.encrypted:
            ftmp = self.opfname_wencrypt
            if self.wrong_psk: tpsk = self.wrong_psk
            else: tpsk = self.psk
            tbool = True
        else:
            ftmp = self.opfname_woencrypt
            tpsk = ""
            tbool = False

        # create custom file
        ftin = "%s/%s" % (self.ftpserv['rootpath'], self.ipfname)
        ftout = "%s/%s" % (self.ftpserv['rootpath'], ftmp)

        if self.encrypted:
            customtmp = "%s/%s" % (self.ftpserv['rootpath'], self.opfname_woencrypt)
            create_custom_file(ftin, self.ap_profile, customtmp, False)
            ftin = customtmp
        create_custom_file(ftin, self.ap_profile, ftout, tbool, tpsk)

        if self.build:
            self.ctrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], self.build)
        self.ctrl_file = self.active_ap.create_ctrl_file(self.ftpserv['rootpath'], ftmp, custom=True)

    def _startTcpdump(self):
        logging.info("Use tool tcpdump to capture traffic while upgrading custom file to the AP")
        fo, self.tcpdump_info = tempfile.mkstemp(".pcap")
        self.local_sta.start_tcp_dump(ip_addr=self.sta_ip_addr,
                                    proto='tcp',
                                    file_path=self.tcpdump_info,
                                    snaplen=65535,write=True,
                                    not_use_verbose=True)

    def _analyzeData(self):

        if self.encrypted:
            logging.info("[Encrypted Custom File]: Verify its data is unreadable")
        else: logging.info("[NonEncrypted Custom File]: Verify its data is readable")

        ftpdata = self.local_sta.get_ftp_data(self.tcpdump_info, self.sta_ip_addr, self.ap_ip_addr)
        tmp = self.commands
        tmp = [line.replace(" ", "") for line in tmp]

        readable = False
        for data in ftpdata:
            for line in tmp:
                if line in data:
                    readable = True
                    break
            if readable: break

        if self.encrypted:
            if readable: return ["FAIL",
                                 "[Encrypted Custom File]: FTP data is still readable while it's encrypted"]
            else: logging.info("[Encrypted Custom File]: FTP data is not readable. Correct behavior")
        else:
            if not readable: return ["FAIL",
                                     "[NonEncrypted Custom File]: FTP data is not readable while it is not encrypted"]
            else: logging.info("[NonEncrypted Custom File]: FTP data is readable. Correct behavior")

        return ["PASS", ""]

    def _configPSK(self):

        logging.info("Configure Decryption Password at AP CLI")
        self.active_ap.change_fw_setting({'psk': self.psk,'auto':self.auto_upgrade})

        logging.info("Verify decryption password after setting")
        fw_setting = self.active_ap.get_fw_upgrade_setting()

        if fw_setting['psk'] != self.psk:
            return ["FAIL", "Can not set decryption password for FW setting"]

        logging.info("Decrytpion password is configured successfully")
        return ["PASS", ""]

    def _createCustomSrcFile(self):
        try:
            fi = open("%s/%s" % (self.ftpserv['rootpath'], self.ipfname), 'w')
            for line in self.commands: fi.write(line+'\n')
            fi.write('\n')
            fi.close()
        except:
            try:
                fi.close()
            finally:
                raise Exception('[Cablevision]: Can not create the custom source file')

    def _verifyCustomFile(self):

        failed_msg = ""
        order = 0
        for key, value in self.getcmds.iteritems():
            res = self.active_ap.cmd(key)
            time.sleep(0.1)

            found = False
            for line in res:
                mobj = re.search(value, line)
                if mobj:
                    found = True
                    break
            if not found: failed_msg += "** Command [%s]: is not applied correctly " % self.commands[order]
            order += 1

        return failed_msg

    def _logCheckCustomFile(self):

        failed_msg = self._verifyCustomFile()
        if failed_msg:
            return ["FAIL",
                    "%s. Custom file is activated but its configuration is not applied to AP correctly" % failed_msg]

        logging.info("Custom file is activated and its configuration is applied to AP successfully")
        return ["PASS", ""]

    def _logAutoReboot(self, msg = ""):
        # Verify automatically reboot
        try:
            if self.factory: self.active_ap.check_log_auto_up(log_factory=True)
            else: self.active_ap.check_log_auto_up()
        except Exception, e:
            if str(e.message).find('can not login') != -1:
                raise Exception(e.message)

            if self.factory:
                if str(e.message).find('set factory') != -1:
                    return ["FAIL", e.message]
            return ["FAIL", "[Auto Upgrade %s]: AP does not automatically reboot because of the error: %s" %
                    (msg, e.message)]

        return ["PASS", ""]
