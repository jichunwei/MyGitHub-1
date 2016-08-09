'''
This test script is to verify following authentication types:
4.4.1.1    Upgrade image via AP WebUI
4.4.1.2    Upgrade image via AP CLI mode

Test Procedure:
I. Upgrade via Web UI
1.    Login the AP WebUI by admin account.
2.    Go to Management > Upgrade page
3.    Select tftp/ftp protocol to do upgrade
4.    Fill fullly information for tftp/ftp
5.    Click Perform Upgrade button
6.    Wait for a moment, make sure it shows a dialog to inform upgrading successfully

II. Upgrade via Web UI
1.    Login the CLI by admin account.
2.    Enter into shell mode
3.    Use command "fw set proto", "fw set ip", "fw set port", "fw set user", "fw set pass"
      to set necessary setting for tftp/ftp
5.    Execute "fw update main" to upgrade the main image
6.    Wait for a moment, make sure it shows the upgrade progress completed successfully

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

'''
import os, time, logging, re, random, traceback, shutil
from datetime import *
from pprint import pprint, pformat

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *
from RuckusAutoTest.components.RuckusAP import RuckusAP


class AP_FwUpgrade(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfgTestParams(**conf)

    def test(self):
        if 'cli' == self.p['test_type'].lower():
            self._doUpgradeFwViaCLI()
        else:
            self._doUpgradeFwViaWebUI()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testAPFwVersion(is_test_upgrade=True)
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        if 'cli' == self.p['test_type'].lower():
            self._doRestoreFwViaCLI()
        else:
            self._doRestoreFwViaWebUI()
        self._testAPFwVersion(is_test_upgrade=False)

        self.aliases.fm.logout()
        self._removeImgCtrlFile()

    def _cfgTestParams(self, **kwa):
        self.p = {
            'model': 'zf2925',
            'ap_ip': '',
            'fw_upgrade_path': '', #fw which is used to test, it is a full path likes "D:/temp/fw/2942_8.1.0.0.72.Bl7"
            'fw_restore_path': '', # fw which is used to restore when finish the test, it is a full path like "D:/temp/fw/2942_8.1.0.0.72.Bl7"
            'test_type': 'cli',
            'test_name': 'Verify firmware upgrade via Web UI by using protocol tftp',
            'ftp_cfg': dict(
                protocol = 'tftp', # ftp, tftp
                ip_addr = '192.168.200.252', # tftp, ftp
                port = '69', # tftp, ftp
                rootpath = '', # tftp, ftp
                #username = '%s', # use for ftp only
                #password = '%s', # use for ftp only
            ),
        }
        self.p.update(kwa)
        self.aliases = init_aliases(testbed=self.testbed)

        self.ap_cli_cfg = get_ap_default_cli_cfg()
        self.ap_cli_cfg['ip_addr'] = self.p['ap_ip']
        self.ap_cli_cfg['ftpsvr'] = self.p['ftp_cfg']

        self.ap_webui = self.aliases.tb.getApByIp(self.p['ap_ip'])
        self.ap_cli   = RuckusAP(self.ap_cli_cfg)

        # pattern to get version from firmware image name
        version_pat = '(?<=_)\S+(?=.bl7)'
        # get firmware name
        self.upgrade_fw_name = os.path.split(self.p['fw_upgrade_path'])[1]
        self.restore_fw_name  = os.path.split(self.p['fw_restore_path'])[1]
        # get firmware version
        self.fw_upgrade_version = re.search(version_pat, self.upgrade_fw_name , re.I).group(0)
        self.fw_restore_version = re.search(version_pat, self.restore_fw_name , re.I).group(0)

        # Only have to create ctrl file and copy image/ctrl files to FTP Root dir
        # if test upgrade AP fw via webUI. If upgrade via cli, the upgrade_sw of
        # RuckusAP already do create ctrl file and copy image/ctrl files to the
        # FTP root dir.
        #if 'webui' == self.p['test_type'].lower():
        self._createUpgradeAndRestoreCtrlFile()
        # get ctrl file name
        self.upgrade_ctrl_file_name = os.path.split(self.upgrade_ctrl_file_path)[1]
        self.restore_ctrl_file_name = os.path.split(self.restore_ctrl_file_path)[1]

        self._copyUpgradeRestoreImgAndCtrlFileToFTPRootDir()

        logging.info('Test configs:\n%s' % pformat(self.p))

    def _wait4_ap_stable(self):
        '''
        This function is to check CPU usage of AP and wait for each ready to test.
        Note: if provide username password, this function will use that username/password
        instead of username/password from ap instance to connect to AP and monitor its CPU usage.
        '''
        # monitor AP CPU usage to wait for its load < 40% after rebooting or provisioning
        MONITOR_CPU_USAGE = 0

        monitor_cpu_cfg= {
            #'config': config,
            'monitor': MONITOR_CPU_USAGE,
            'threshold': 40, # default % CPU Usage
            'timeout': 20, # in minute
            'interval': 2,
            'times_to_check': 3,
        }

        monitor_cpu_cfg.update({'config': self.ap_cli_cfg})
        msg = 'CPU of AP %s looks free for the test' % self.ap_cli_cfg['ip_addr']\
                if wait4_ap_stable(**monitor_cpu_cfg) else \
                ('WARNING: The CPU usage of AP %s is still too high' % self.ap_cli_cfg['ip_addr'])
        logging.info(msg)

    def _doUpgradeFwViaCLI(self):
        '''
        If upgrade via cli, the function upgrade_sw of RuckusAP also call the function
        CreateCtrlFile so we don't to do this step first
        '''
        try:
            self.ap_cli.upgrade_sw(self.p['fw_upgrade_path'], timeout=240, is_img_file_extracted=True)
        except Exception, e:
            # TODO: Whether we treat a situation "Unecessary to do upgrade" as failed case?
            # We may see this problem if the upgrade fw is the same with current fw on AP
            if 'no update' in e.__str__().lower():
                logging.info('No need to do upgrade')
            else:
                self.errmsg = ('Fail to upgrade to firmware version: %s. Error: %s' %
                               (self.fw_upgrade_version, e.__str__()))
                logging.info(self.errmsg)

    def _doRestoreFwViaCLI(self):
        '''
        If upgrade via cli, the function upgrade_sw of RuckusAP also call the function
        CreateCtrlFile so we don't to do this step first
        '''
        try:
            self.ap_cli.upgrade_sw(self.p['fw_restore_path'], timeout=240, is_img_file_extracted=True)
        except Exception, e:
            logging.info('Warning: Fail to restore to firmware version: %s. Error: %s' %
                         (self.fw_restore_version, e.__str__()))

    def _createUpgradeAndRestoreCtrlFile(self):
        '''
        This function is to use RuckusAP instance to create a ctrl file to do
        upgrade and restore firmware.
        '''
        ap_cli = RuckusAP(self.ap_cli_cfg)
        #fw_file = self.p['fw_upgrade_patch'] if is_upgrade else self.p['fw_restore_patch']
        self.upgrade_ctrl_file_path = ap_cli.create_ctrl_file(self.p['fw_upgrade_path'])
        self.restore_ctrl_file_path = ap_cli.create_ctrl_file(self.p['fw_restore_path'])

    def _copyUpgradeRestoreImgAndCtrlFileToFTPRootDir(self):
        '''
        This function is to copy image, ctrl files for upgrading/restoringi to tftp/ftp
        server
        '''
        root_path = self.p['ftp_cfg']['rootpath']
        shutil.copyfile(self.upgrade_ctrl_file_path, root_path + '\\' + self.upgrade_ctrl_file_name)
        shutil.copyfile(self.restore_ctrl_file_path, root_path + '\\' + self.restore_ctrl_file_name)
        shutil.copyfile(self.p['fw_upgrade_path'], root_path + '\\' + self.upgrade_fw_name)
        shutil.copyfile(self.p['fw_restore_path'], root_path + '\\' + self.restore_fw_name)

    def _doUpgradeFwViaWebUI(self):
        '''
        - Set config to provide it for set_cfg function of ap_fw_upgrade_fm_mgmt_hlp
          library
        '''
        # keys of ftp_cfg are the same as keys config of ap_fw_upgrade_fm_mgmt_hlp.set_cfg
        ui_cfg = copy.deepcopy(self.p['ftp_cfg'])
        remove_keys = ['rootpath']
        for k in remove_keys: del ui_cfg[k]
        # get ctrl file name only
        ui_cfg['ctrl_file_name'] = self.upgrade_ctrl_file_name
        self.ap_webui.start(15)
        try:
            ts, msg = lib.ap.fwup.set_cfg(self.ap_webui, ui_cfg)
            logging.info(msg)
            # TODO: Whether we treat a situation "Unecessary to do upgrade" as failed case?
            # We may see this problem if the upgrade fw is the same with current fw on AP
            if lib.ap.fwup.UPGRADE_STATUS_FAILED == ts or lib.ap.fwup.UPGRADE_STATUS_TIMEOUT == ts:
                self.errmsg = msg
        except Exception, e:
            # TODO: Use log_trace enhancement from Luan for this
            self.errmsg = ('Fail to upgrade to firmware version: %s. Error: %s' %
                         (self.fw_upgrade_version, e.__str__()))

            logging.info(self.errmsg)

        self.ap_webui.stop()

    def _doRestoreFwViaWebUI(self):
        '''
        - Set config to provide it for set_cfg function of ap_fw_upgrade_fm_mgmt_hlp
          library
        '''
        # keys of ftp_cfg are the same as keys config of ap_fw_upgrade_fm_mgmt_hlp.set_cfg
        ui_cfg = copy.deepcopy(self.p['ftp_cfg'])
        remove_keys = ['rootpath']
        for k in remove_keys: del ui_cfg[k]
        # get ctrl file name only
        ui_cfg['ctrl_file_name'] = self.restore_ctrl_file_name
        self.ap_webui.start(15)
        try:
            ts, msg = lib.ap.fwup.set_cfg(self.ap_webui, ui_cfg)
            # TODO: Whether we treat a situation "Unecessary to do upgrade" as failed case?
            # We may see this problem if the upgrade fw is the same with current fw on AP
            if lib.ap.fwup.UPGRADE_STATUS_FAILED == ts or lib.ap.fwup.UPGRADE_STATUS_TIMEOUT == ts:
                logging.info('Warning: Fail to restore to firmware version to %s. Error: %s' %
                         (self.fw_restore_version, msg))
        except Exception, e:
            logging.info('Warning: Fail to restore to firmware version to %s. Error: %s' %
                         (self.fw_restore_version, e.__str__()))

        self.ap_webui.stop()

    def _testAPFwVersion(self, is_test_upgrade=True):
        '''
        This version is to make sure AP fw version is the expected one after
        upgrading/restoring
        '''
        self._wait4_ap_stable()

        cur_version = self.ap_cli.get_version().strip()
        expected_version = self.fw_upgrade_version if is_test_upgrade else self.fw_restore_version
        logging.info('Current version: %s. Expected version: %s' % (cur_version, expected_version))
        if  expected_version == cur_version:
            logging.info('The AP was ' + ('upgraded' if is_test_upgrade else 'restored') +
                         ' to version ' + cur_version + ' via ' + self.p['test_type'] + ' successfully!!!')
            self.passmsg = self.p['test_name']
        else:
            self.errmsg = ('Cannot ' + 'upgrade' if is_test_upgrade else 'restore' +
                         ' AP to version ' + cur_version + ' !!!')
            logging.info(self.errmsg)

    def _removeImgCtrlFile(self):
        '''
        This function is to remove img, ctrl files on the FTP root dir.
        We only need to call this function if do upgrade via webUI. It is because
        if do upgrade fw via cli the upgrade_sw of RuckusAP already do delete these
        files.
        '''
        root_path = self.p['ftp_cfg']['rootpath']
        try:
            # remove ctrl files
            remove_file(root_path + '\\' + self.upgrade_ctrl_file_name)
            remove_file(root_path + '\\' + self.restore_ctrl_file_name)
            # remove imge files
            remove_file(root_path + '\\' + self.upgrade_fw_name )
            remove_file(root_path + '\\' + self.restore_fw_name )
        except Exception, e:
            # ignore error if cannot delete the file in the root_path
            logging.info('Warning: Cannot remove the ctrl and image files in the'
                         ' root directory %s. Error: %s' % (root_path, e.__str__()))
