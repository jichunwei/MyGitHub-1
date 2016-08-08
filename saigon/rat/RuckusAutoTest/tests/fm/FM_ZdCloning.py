'''
NOTES:
This script is to obtain/edit a ZD config.

Hence, this test script is currently to test below test cases:
    1.1.9.7     ZoneDirector Clone
    1.1.9.7.1    Create new ZoneDirector Clone task  select by group , cloning type is "Restore clone"
    1.1.9.7.2    Create new ZoneDirector Clone task  select by group , cloning type is "Failover clone"
    1.1.9.7.3    Create new ZoneDirector Clone task  select by group , cloning type is "Policy clone"
    1.1.9.7.5.1    By schedule and repeat test case 1.1.9.7.1
    1.1.9.7.5.2    By schedule and repeat test case 1.1.9.7.2
    1.1.9.7.5.3    By schedule and repeat test case 1.1.9.7.3
    1.1.9.7.6    Cancel ZoneDirector clone  task
    1.1.9.7.7    Update result
    1.1.9.7.6    Cancel ZoneDirector clone  task
    1.1.9.7.7    Update result

Test Procedure for 1.1.9.7.1, 1.1.9.7.2, 1.1.9.7.3, 1.1.9.7.5.1, 1.1.9.7.5.2, 1.1.9.7.5.3:
    1. Log in FM as admin account
    2. Navigate to Configure > Manage ZD Configurations
    3. Click "Obtain New ZoneDirector Configuration" link and select a ZD to obtain
       a new cfg.
    4. Enter a description and save it
    5. Go to Configure > ZoneDirector Cloning, create a new zd cloning task:
        + Enter a task name.
        + Select the zd cfg file.
        + Select a target zd/a group of ZD to do cloning
        + Select a cloning mode.
        + Schedule this task if needed.
        + Save this task.
    6. Wait for the task completed successfully
    7. Go to target zds and make sure the cfg exported correctly according to each
       cloning mode as below:

Full Restore Mode: Restore all settings:
    o    IP
    o    System name
    o    User name
    o    Password.


Failover Restore Mode:
    Restore below items:
    o    System
    o    WLANs
    o    Access Control
    o    Roles
    o    User setting: Roles, Users, Guest Access, Hotspot Services, Mesh, AAA Servers,
                       Alarm Settings, Services, and Access Point.
    Except:
    o    IP
    o    System name from System page
    o    User name
    o    Password.

Policy Restore Mode:
    Restore below items:
    o    WLANs
    o    Access Control
    o    Roles
    o    User settings: Roles, Users, Hotspot Services, Mesh, AAA Servers, Alarm Settings,
                       Services and Access Point.
    Except:
    o    Dynamic pre-shared key (PSK) (NOTE: Not support to verify this yet)
    o    Guest Access

Test procedure for "1.1.9.7.6 Cancel ZoneDirector clone  task":
    1. Log in FM as admin account
    2. Navigate to Configure > Manage ZD Configurations
    3. Click "Obtain New ZoneDirector Configuration" link and select a ZD to obtain
       a new cfg.
    4. Enter a description and save it
    5. Go to Configure > ZoneDirector Cloning, create a new zd cloning task:
        + Enter a task name.
        + Select "Restore" for configuration type
        + Select the zd cfg file.
        + Select a target zd/a group of ZD to do cloning
        + Select a cloning mode.
        + Schedule this task.
        + Save this task.
    6. Click "Cancel" to cancle this task.
    7. Make sure the task can be "canceled".

Test procedure for "1.1.9.7.7 Update result":
    1. Log in FM as admin account
    2. Navigate to Configure > Manage ZD Configurations
    3. Click "Obtain New ZoneDirector Configuration" link and select a ZD to obtain
       a new cfg.
    4. Enter a description and save it
    5. Test two cases: "Success" and "failed/expired"
        5.1 Success case:
            + Make sure ZD connected to FM correctly.
            + Create a ZD cfg cloning as above.
            + Make sure the task executed and its status updated as "success"

        5.2 "Failed/Expired" case:
            + Make sure ZD disconnected to FM by plug out network cable or
              disable port on the switch correctly.
            + Create a ZD cfg cloning as above.
            + Make sure the task executed and its status updated as "expired"
    # NOTE FOR UPDATE RESULT TEST CASE: This test case need to do two things:
    # 1. Verify updating result for "success" case: a clone task executed successfully.
    # 2. Verify updating result for "failed/expired" cases: Currently cannot not
    # verify this case due to no L3 switch in testbed to disable zds/aps ports on the
    # switch.

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *

class FM_ZdCloning(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)

    def test(self):
        self._execute_test()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_result()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        self._cleanup_test()
        self.fm.logout()

    def _cfg_test_params(self, **kwa):
        ''''''
        cfg_fn = {
            'create': self._cfg_test_params_for_test_type_create,
            'cancel': self._cfg_test_params_for_test_type_cancel,
            'update': self._cfg_test_params_for_test_type_update,
        }[kwa['test_type']]
        if cfg_fn: cfg_fn(**kwa)

    def _cfg_test_params_for_test_type_create(self, **kwa):
        self.p = dict(
            test_type = 'create',
            schedule = 0,
            zd_model = 'zd1k',
            source_zd_ip = 'specify the source zd',
            target_zd_ip = '', # specify "target zd ip" if you want do cloning for one zd
            group_name = '', # specify "group name" if you want do cloning for a group of ZD
            zd_set_cfg = 'specify the set cfg', # this key is for "create" test only
            test_name = 'Create a "Full Restore" ZD cloning task',
            cloning_mode = 'full_restore', # dhcp, static
            keys_for_set = [], # this key is for "create" test only
            expected_inconsistent_keys = [], # this key is for "create" test only
            expected_consistent_keys = [], # this key is for "create" test only
        )
        self.p.update(kwa)

        init_coms(self, dict(tb=self.testbed))
        # Some places of zd 9 doesn't accept dot symbol ".". Replace it first.
        time_stamp = get_timestamp().replace(".", "_")
        # NOTE: Almost cloning test bases on system_name of System page to check
        # whether the cloning function works correctly or not. Hence, we have to
        # make the system_name unique by appending a timestamp to its name. This
        # makes the system_name of Source ZD always different from the target ZD.
        if self.p['zd_set_cfg'].has_key('system') and \
            self.p['zd_set_cfg']['system'].has_key('system_name'):
            self.p['zd_set_cfg']['system']['system_name'] += '_%s' % time_stamp
        # Get source and target ZD to set/get cfg from web ui
        self.source_zd = self.testbed.get_zd_by_ip(self.p['source_zd_ip'])
        self.target_zd = self.testbed.get_zd_by_ip(self.p['target_zd_ip'])

        self.source_zd.start()
        # get zd serial: temporary comment out it
        self.p['source_zd_serial'] = self.source_zd.get_serial_number()
        #self.p['source_zd_serial'] = 'SN1235'
        self.target_zd.start()
        # Temporarily comment out it
        self.p['target_zd_serial'] = self.target_zd.get_serial_number()
        #self.p['target_zd_serial'] = 'SN1234'


        # Add basic param to do test cfg upgrade for
        # Basic param 1: create a config param for cfg template
        self.p['settings_to_get_new_cfg_from_source_zd']= dict(
            cfg = dict(
                cfg_desc = 'cloning_cfg_%s' % (time_stamp),
            ),
            match_expr = dict(
                internal_ip = self.p['source_zd_ip'],
                serial = self.p['source_zd_serial']
            )
        )
        self.p['settings_to_get_ori_cfg_from_source_zd']= dict(
            cfg = dict(
                cfg_desc = 'original_cfg_%s' % (time_stamp),
            ),
            match_expr = dict(
                internal_ip = self.p['source_zd_ip'],
                serial = self.p['source_zd_serial']
            )
        )
        self.p['settings_to_get_ori_cfg_from_target_zd']= dict(
            cfg = dict(
                cfg_desc = 'original_cfg_%s' % (time_stamp),
            ),
            match_expr = dict(
                internal_ip = self.p['target_zd_ip'],
                serial = self.p['target_zd_serial']
            )
        )
        # Deinfe settings to do zd cfg cloning task test
        self.p['settings_to_create_cloning_task'] = dict(
            task_name     = '%s_%s' % (self.p['cloning_mode'], time_stamp),
            cfg_type      = 'restore',
            cfg_file_name = '%s\(%s_backup.tgz' %
                            (self.p['settings_to_get_new_cfg_from_source_zd']['cfg']['cfg_desc'],
                             self.p['source_zd_serial']),
            clone_type    = self.p['cloning_mode'],
            schedule      = self.p['schedule'],
        )
        # Whether do cloning for a zd or a group of zd
        if self.p['target_zd_ip']:
            self.p['settings_to_create_cloning_task']['device'] = self.p['target_zd_ip']
        else:
            self.p['settings_to_create_cloning_task']['group_name'] = self.p['group_name']

        # Define settings to restore cfg for the source ZD
        self.p['settings_to_restore_source_zd'] = dict(
            task_name     = '%s_%s' % ('full_restore', time_stamp),
            cfg_type      = 'restore',
            cfg_file_name = '%s\(%s_backup.tgz' %\
                            (self.p['settings_to_get_ori_cfg_from_source_zd']['cfg']['cfg_desc'],
                             self.p['source_zd_serial']),
            clone_type    = 'full_restore',
            schedule      = 0,
            device        = self.p['source_zd_ip']
        )

        # Define settings to restore cfg for the target ZD(s)
        self.p['settings_to_restore_target_zd'] = dict(
            task_name     = '%s_%s' % ('full_restore', time_stamp),
            cfg_type      = 'restore',
            cfg_file_name = '%s\(%s_backup.tgz' %\
                            (self.p['settings_to_get_ori_cfg_from_target_zd']['cfg']['cfg_desc'],
                             self.p['target_zd_serial']),
            clone_type    = 'full_restore',
            schedule      = 0,
        )
        # Whether do restore for only one target zd or a group of zd
        if self.p['target_zd_ip']:
            self.p['settings_to_restore_target_zd']['device'] = self.p['target_zd_ip']
        else:
            self.p['settings_to_restore_target_zd']['group_name'] = self.p['group_name']

        logging.info('Test configs:\n%s' % pformat(self.p))

    def _cfg_test_params_for_test_type_cancel(self, **kwa):
        '''
        This function is to do settings for "cancel" and "update" test cases.
        '''
        self.p = dict(
            test_type = 'cancel',
            schedule = 10,
            zd_model = 'zd1k',
            source_zd_ip = 'specify the source zd',
            test_name = 'Test cancel case',
            cloning_mode = 'full_restore', # dhcp, static
        )
        self.p.update(kwa)

        init_coms(self, dict(tb=self.testbed))
        time_stamp = get_timestamp()
        # Get source and target ZD to set/get cfg from web ui
        self.source_zd = self.testbed.get_zd_by_ip(self.p['source_zd_ip'])

        self.source_zd.start()
        # get zd serial
        self.p['source_zd_serial'] = self.source_zd.get_serial_number()


        # Add basic param to do test "Cancel" or "Update" result
        self.p['settings_to_get_cfg_from_source_zd']= dict(
            cfg = dict(
                cfg_desc = 'source_zd_cfg_%s' % (time_stamp),
            ),
            match_expr = dict(
                internal_ip = self.p['source_zd_ip'],
                serial = self.p['source_zd_serial']
            )
        )
        # Deinfe settings to do zd cfg cloning task test
        self.p['settings_to_create_cloning_task'] = dict(
            task_name     = '%s_%s' % ('test_cancel', time_stamp),
            cfg_type      = 'restore',
            cfg_file_name = '%s\(%s_backup.tgz' %
                            (self.p['settings_to_get_cfg_from_source_zd']['cfg']['cfg_desc'],
                             self.p['source_zd_serial']),
            clone_type    = self.p['cloning_mode'],
            schedule      = self.p['schedule'],
            device        = self.p['source_zd_ip']
        )

        logging.info('Test configs:\n%s' % pformat(self.p))

    def _cfg_test_params_for_test_type_update(self, **kwa):
        '''
        This function is to do settings for "cancel" and "update" test cases.
        NOTE FOR "update" case:
        - For the "update" case, we have to test two cases:
            1. "Success" case:
                - Obtain cfg from the source zd.
                - Do cloning cfg to itself "source zd"
            2. "Failed/Expired" case:
                - Obtain cfg from the source zd.
                - Make the source zd disconnected to FM by disable FM management.
                - Do cloning cfg to itself "source zd".
        '''
        self.p = dict(
            test_type = 'update',
            schedule = 0,
            zd_model = 'zd1k',
            source_zd_ip = 'specify the source zd',
            test_name = 'Test update result',
            cloning_mode = 'full_restore', # dhcp, static
        )
        self.p.update(kwa)

        init_coms(self, dict(tb=self.testbed))
        time_stamp = get_timestamp()
        # Get source and target ZD to set/get cfg from web ui
        self.source_zd = self.testbed.get_zd_by_ip(self.p['source_zd_ip'])

        self.source_zd.start()
        # get zd serial
        self.p['source_zd_serial'] = self.source_zd.get_serial_number()

        # Add basic param to do test "Cancel" or "Update" result
        self.p['settings_to_get_cfg_from_source_zd']= dict(
            cfg = dict(
                cfg_desc = 'source_zd_cfg_%s' % (time_stamp),
            ),
            match_expr = dict(
                internal_ip = self.p['source_zd_ip'],
                serial = self.p['source_zd_serial']
            )
        )
        # Deinfe settings to do zd cfg cloning task test
        self.p['task_settings_to_test_success_case'] = dict(
            task_name     = '%s_%s' % ('test_success', time_stamp),
            cfg_type      = 'restore',
            cfg_file_name = '%s\(%s_backup.tgz' %
                            (self.p['settings_to_get_cfg_from_source_zd']['cfg']['cfg_desc'],
                             self.p['source_zd_serial']),
            clone_type    = self.p['cloning_mode'],
            schedule      = self.p['schedule'],
            device        = self.p['source_zd_ip']
        )
        self.p['task_settings_to_test_failed_case'] = dict(
            task_name     = '%s_%s' % ('test_failed_expired', time_stamp),
            cfg_type      = 'restore',
            cfg_file_name = '%s\(%s_backup.tgz\)' %
                            (self.p['settings_to_get_cfg_from_source_zd']['cfg']['cfg_desc'],
                             self.p['source_zd_serial']),
            clone_type    = self.p['cloning_mode'],
            schedule      = self.p['schedule'],
            device        = self.p['source_zd_ip']
        )
        self.p['settings_to_disable_fm_mgmt'] = dict(
            enable_fm_mgmt = False,
        )
        self.p['settings_to_enable_fm_mgmt'] = dict(
            enable_fm_mgmt = True,
            fm_url         = self.fm.get_cfg()['ip_addr'],
            fm_interval    = 5
        )

        logging.info('Test configs:\n%s' % pformat(self.p))

    def _change_zd_cfg(self):
        '''
        This function is to change ZD cfg according to input zd cfg from input
        cfg.
        '''
        keys_for_set = self.p['keys_for_set']
        for k in self.p['keys_for_set']:
            cfg_fn = {
               'system': lib.zd.sys2.set,
               'wlan': lib.zd.wlan2.set,
               'access_point': lib.zd.ap2.set,
               'access_control': lib.zd.ac2.set,
               'map': lib.zd.zd_map.set,
               'role': lib.zd.zd_role.set,
               'user': lib.zd.zd_user.set,
               'guest_access': lib.zd.ga2.set,
               'hotspot_service': lib.zd.wispr2.set,
               'mesh': lib.zd.zd_mesh.set,
               'aaa_server': lib.zd.aaa2.set,
               'alarm_setting': lib.zd.zd_alarm.set,
               'service': lib.zd.zd_service.set,
            }[k]
            logging.info('Configure page %s with setting %s' % (k, pformat(self.p['zd_set_cfg'][k])))
            cfg_fn(self.source_zd, self.p['zd_set_cfg'][k], 'create')

    def _obtain_zd_cfg(self, match_expr, cfg, msg=''):
        try:
            lib.fm.zd_cfg.obtain_zd_cfg(self.fm, match_expr, cfg)
            logging.info('Obtained a ZD cfg with setting "%s" and match expr %s successfully' %
                         (pformat(cfg), pformat(match_expr)))
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _do_zd_cloning_cfg(self, cfg):
        ''''''
        ts, detail = None, None
        logging.info('Do cloning cfg with setting %s' % (pformat(cfg)))
        timeout = lib.fm.zd_cloning.create_zd_cloning_task(self.fm, cfg)

        logging.info('Monitor the cloning task %s. Timeout: %s' %
                     (cfg['task_name'], timeout))
        ts, detail = lib.fm.zd_cloning.monitor_task(
            self.fm, {'task_name': cfg['task_name']}, timeout
        )

        return ts, detail

    def _execute_test(self):
        ''''''
        cfg_test_fn = {
            'create': self._execute_test_for_test_type_create,
            'cancel': self._execute_test_for_test_type_cancel,
            'update': self._execute_test_for_test_type_update,
        }[self.p['test_type']]

        if cfg_test_fn: cfg_test_fn()

    def _execute_test_for_test_type_create(self):
        '''
        This function is to do create a zd cfg cloning task for "create" test type.
        '''
        try:
            # Remove all zd cfg to avoid duplicating config. Especially is for wlan item.
            # ZD doesn't allow creating duplication of wlan.
            logging.info('Remove all config of the source ZD %s' % self.p['source_zd_ip'])
            self.source_zd.remove_all_cfg()
            logging.info('Remove all config of the target ZD %s' % self.p['target_zd_ip'])
            self.target_zd.remove_all_cfg()

            logging.info('Get original cfg of the source ZD %s' % self.p['source_zd_ip'])
            self._obtain_zd_cfg(
                self.p['settings_to_get_ori_cfg_from_source_zd']['match_expr'],
                self.p['settings_to_get_ori_cfg_from_source_zd']['cfg']
            )
            if self.errmsg: return

            logging.info('Get original cfg of the target ZD %s' % self.p['target_zd_ip'])
            self._obtain_zd_cfg(
                self.p['settings_to_get_ori_cfg_from_target_zd']['match_expr'],
                self.p['settings_to_get_ori_cfg_from_target_zd']['cfg']
            )
            if self.errmsg: return

            logging.info('Change cfg of the source ZD %s' % self.p['source_zd_ip'])
            self._change_zd_cfg()
            if self.errmsg: return

            logging.info('Obtain the new cfg of the source zd %s' % self.p['source_zd_ip'])
            self._obtain_zd_cfg(
                self.p['settings_to_get_new_cfg_from_source_zd']['match_expr'],
                self.p['settings_to_get_new_cfg_from_source_zd']['cfg']
            )
            if self.errmsg: return

            # do a trick here: after finish cloning task, WebUI of target zd will
            # be expired. Log out it first to avoid this situation
            self.target_zd.logout()

            ts, detail = self._do_zd_cloning_cfg(self.p['settings_to_create_cloning_task'])
            if ts and lib.fm.zd_cloning.is_success_status(ts):
                logging.info('Did cloning cfg task for target zd(s) successfully. '
                             'Task status: %s. Detail: %s' % (ts, detail))
            else:
                self._fill_error_msg(
                    'Warning: Cannot do cloning cfg task for the target ZD(s). '
                    'Task status: %s. Detail: %s' % (ts, detail)
                )
                return
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _execute_test_for_test_type_cancel(self):
        '''
        This function is to do execute test type "cancle".
        '''
        try:
            # 1. Obtain ZD config
            logging.info('Get cfg of the source ZD %s' % self.p['source_zd_ip'])
            self._obtain_zd_cfg(
                self.p['settings_to_get_cfg_from_source_zd']['match_expr'],
                self.p['settings_to_get_cfg_from_source_zd']['cfg']
            )
            if self.errmsg: return

            # 2. Create cloning task cfg
            logging.info('Create zd cloning cfg task with setting %s' %
                         (pformat(self.p['settings_to_create_cloning_task'])))
            timeout = lib.fm.zd_cloning.create_zd_cloning_task(
                self.fm, self.p['settings_to_create_cloning_task']
            )
            # 3. Cancel the task
            ts, detail = lib.fm.zd_cloning.cancel_task(
                self.fm,
                {'task_name': self.p['settings_to_create_cloning_task']['task_name']},
                timeout
            )
            # 4. Check its status to make sure that it is canceled
            if ts and lib.fm.zd_cloning.is_canceled_status(ts):
                logging.info('Cancel zd cloning cfg task successfully. '\
                             'Task status: %s. Detail: %s' % (ts, detail))
            else:
                self._fill_error_msg(
                    'Warning: Cannot cancel zd cloning cfg task. '\
                    'Task status: %s. Detail: %s' % (ts, detail)
                )
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _test_success_case_for_test_type_update(self):
        '''
        This function is to test success case for the test type "update".
        '''
        try:
            logging.info(
                'Test "success" case for the zd cloning config test type "%s"' %
                self.p['test_type']
            )
            # Create cloning task cfg and monitor it
            ts, detail = self._do_zd_cloning_cfg(self.p['task_settings_to_test_success_case'])
            # Check its status to make sure that it is update as "success"
            if ts and lib.fm.zd_cloning.is_success_status(ts):
                logging.info('CORRECTLY: The zd cloning cfg task is updated as "success"'\
                             'Task status: %s. Detail: %s' % (ts, detail))
            else:
                self._fill_error_msg(
                    'ERROR: Expect the zd cloning cfg task "success" but its status: '\
                    'Task status: %s. Detail: %s' % (ts, detail)
                )
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _test_negative_case_for_test_type_update(self):
        '''
        This function is to test "failed/expired" case for the test type "update".
        NOTE: Currently we can only verify "expired" case. Don't know how to verify
              "failed" case.

        # @TODO: Currently cannot not verify this case due to no L3 switch in testbed
        # to disable zds/aps ports on the switch.
        '''
        try:
            logging.info(
                'Test "failed/expired" case for the zd cloning config test type "%s"' %
                self.p['test_type']
            )
            logging.info('Disable FM management of the source ZD %s' % self.p['source_zd_ip'])
            lib.zd.sys2.set(self.source_zd, self.p['settings_to_disable_fm_mgmt'])
            # Create cloning task cfg and monitor it
            ts, detail = self._do_zd_cloning_cfg(self.p['task_settings_to_test_failed_case'])
            # Check its status to make sure that it is update as "success"
            if ts and \
                (lib.fm.zd_cloning.is_expired_status(ts) or \
                 lib.fm.zd_cloning.is_failed_status(ts)):
                logging.info('CORRECTLY: The zd cloning cfg task is updated as "expired/failed"'\
                             'Task status: %s. Detail: %s' % (ts, detail))
            else:
                self._fill_error_msg(
                    'ERROR: Expect the zd cloning cfg task "failed/expired" but its status: '\
                    'Task status: %s. Detail: %s' % (ts, detail)
                )
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _execute_test_for_test_type_update(self):
        '''
        This function is to do execute test type "update".
        '''
        try:
            # 1. Obtain ZD config
            logging.info('Get cfg of the source ZD %s' % self.p['source_zd_ip'])
            self._obtain_zd_cfg(
                self.p['settings_to_get_cfg_from_source_zd']['match_expr'],
                self.p['settings_to_get_cfg_from_source_zd']['cfg']
            )
            if self.errmsg: return

            # do a trick here: after finish cloning task, WebUI of source zd will
            # be expired. Log out it first to avoid this situation
            self.source_zd.logout()

            # 2. Test "success" case
            self._test_success_case_for_test_type_update()
            if self.errmsg: return

            # 3. Test "expired/failed" case
            # @TODO: Verify updating result for "failed/expired" cases: Currently cannot not
            # verify this case due to no L3 switch in testbed to disable zds/aps ports on the
            # switch.
            # self._test_negative_case_for_test_type_update()
            # if self.errmsg: return
        except Exception, e:
            log_trace()
            self._fill_error_msg(e.__str__())

    def _test_result(self):
        '''
        Test to make sure the ZD config added/edited successfully
        '''
        logging.info('Checking the result for the test "%s" ZD cfg' % self.p['test_type'])

        test_result_fn = {
            'create': self._verify_result_for_test_type_create,
            'cancel': None, # self._verify_result_for_test_type_cancel,
            'update': None, # self._verify_result_for_test_type_update,
        }[self.p['test_type']]

        if test_result_fn: test_result_fn()

        if self.errmsg is None: self._fill_pass_msg()

    def _get_get_fn(self, k):
        return {
           'system': lib.zd.sys2.get,
           'wlan': lib.zd.wlan2.get,
           'access_point': lib.zd.ap2.get,
           'access_control': lib.zd.ac2.get,
           'map': lib.zd.zd_map.get,
           'role': lib.zd.zd_role.get,
           'user': lib.zd.zd_user.get,
           'guest_access': lib.zd.ga2.get,
           'hotspot_service': lib.zd.wispr2.get,
           'mesh': lib.zd.zd_mesh.get,
           'aaa_server': lib.zd.aaa2.get,
           'alarm_setting': lib.zd.zd_alarm.get,
           'service': lib.zd.zd_service.get,
        }[k]

    def _verify_result_for_test_type_create(self):
        '''
        This function is to verify keys which we expect they are different/the same
        '''
        self.source_zd.logout()
        self.source_zd.login()
        self.target_zd.login()
        # Verify items of expected_consistent_keys
        for k in self.p['expected_consistent_keys']:
            source_zd_vals, target_zd_vals = None, None
            item, keys_to_get = '', []
            # if k is a dict, this dict has only one key.
            # if keys_to_get is empty, get all for this item
            item, keys_to_get = (k.keys()[0], k.values()[0])\
                                    if isinstance(k, dict) else\
                                (k, [])

            get_fn = self._get_get_fn(item)
            source_zd_vals = get_fn(self.source_zd, keys_to_get)
            target_zd_vals = get_fn(self.target_zd, keys_to_get)
            logging.info('Got info from source ZD %s, (key, values): (%s, %s)' %
                         (self.p['source_zd_ip'], item, pformat(source_zd_vals)))
            logging.info('Got info from target ZD %s, (key, values): (%s, %s)' %
                         (self.p['target_zd_ip'], item, pformat(target_zd_vals)))
            if source_zd_vals != target_zd_vals:
                if keys_to_get:
                    self._fill_error_msg(
                        'ERROR: Expect keys "%s" of item "%s" of source and target '
                        'ZD are the same but they are different' % (pformat(keys_to_get), item)
                    )
                else:
                    self._fill_error_msg('ERROR: Expect all items of page "%s" of source '
                        'and target ZD are the same but they are different' % (item)
                    )
                return

            logging.info("CORRECT: Item %s is consistent between source and target ZD" % item)

        # Verify items of expected_inconsistent_keys
        for k in self.p['expected_inconsistent_keys']:
            source_zd_vals, target_zd_vals = None, None
            item, keys_to_get = '', []
            # if k is a dict, this dict has only one key.
            # if keys_to_get is empty, get all for this item
            item, keys_to_get = (k.keys()[0], k.values()[0])\
                                    if isinstance(k, dict) else\
                                (k, [])

            get_fn = self._get_get_fn(item)
            source_zd_vals = get_fn(self.source_zd, keys_to_get)
            target_zd_vals = get_fn(self.target_zd, keys_to_get)
            logging.info('Got info from source ZD %s, (key, values): (%s, %s)' %
                         (self.p['source_zd_ip'], item, pformat(source_zd_vals)))
            logging.info('Got info from target ZD %s, (key, values): (%s, %s)' %
                         (self.p['target_zd_ip'], item, pformat(target_zd_vals)))

            if source_zd_vals == target_zd_vals:
                if keys_to_get:
                    self._fill_error_msg('ERROR: Expect keys "%s" of item "%s" of source '
                        'and target ZD are different but they are the same' % (pformat(keys_to_get), item)
                    )
                else:
                    self._fill_error_msg('ERROR: Expect all items of page "%s" of source '
                        'and target ZD are different but they are the same' % (item)
                    )
                return

            logging.info("CORRECT: Items of page %s of source and target ZD are different" % item)

    def _verify_result_for_test_type_cancel(self):
        '''
        This function is to verify test result for "cancel" case
        Note: No need to verify any else for cancel test
        '''
        pass

    def _verify_result_for_test_type_update(self):
        '''
        This function is to verify test result for "update" case
        Note: No need to verify any else for update test
        '''
        pass

    def _fill_error_msg(self, errmsg):
        self.errmsg = 'The test "%s" has error:" %s' % (self.p['test_name'], errmsg)
        logging.info(self.errmsg)

    def _fill_pass_msg(self):
        self.passmsg = 'The test "%s" works correctly' % self.p['test_name']
        logging.info(self.passmsg)

    def _cleanup_test(self):
        cleanup_fn = {
            'create': self._cleanup_for_test_type_create,
            'cancel': self._cleanup_for_test_type_cancel,
            'update': self._cleanup_for_test_type_update,
        }[self.p['test_type']]

        if cleanup_fn: cleanup_fn()

    def _restore_ori_cfg_for_source_target_zd(self):
        ''''''
        try:
            # 1. Restore original cfg for the source ZD
            ts, detail = self._do_zd_cloning_cfg(self.p['settings_to_restore_source_zd'])
            if ts and lib.fm.zd_cloning.is_success_status(ts):
                logging.info('Restored original cfg for the source ZD %s successfully' %
                             self.p['source_zd_ip'])
            else:
                logging.info('Warning: Cannot restore original cfg for the source ZD %s. '\
                         'Task status: %s. Detail: %s' % (self.p['source_zd_ip'], ts, detail))
        except Exception, e:
            logging.info(
                'Warning: Error "%s" happens while restoring orginal cfg for the '\
                'source ZD %s' %(e.__str__(), self.p['source_zd_ip'])
            )
        try:
            # 2. Restore original cfg for the target ZD
            ts, detail = self._do_zd_cloning_cfg(self.p['settings_to_restore_target_zd'])
            if ts and lib.fm.zd_cloning.is_success_status(ts):
                logging.info('Restored original cfg for the target ZD %s successfully' %
                             self.p['target_zd_ip'])
            else:
                logging.info('Warning: Cannot restore original cfg for the target ZD %s. '\
                             'Task status: %s. Detail: %s' % (self.p['target_zd_ip'], ts, detail))
        except Exception, e:
            logging.info(
                'Warning: Error "%s" happens while restoring orginal cfg for the '\
                'target ZD %s' %(e.__str__(), self.p['target_zd_ip'])
            )

    def _delete_zd_cfg(self, match_expr):
        '''
        This function is to delete a zd cfg matches "match_expr"
        '''
        try:
            lib.fm.zd_cfg.delete_zd_cfg(self.fm, match_expr)
            logging.info('Delete the cfg file with match expression "%s"' % match_expr)
        except Exception, e:
            log_trace()
            logging.info('Warning: Cannot find out any zd cfg matches the expression "%s"' %
                         match_expr)

    def _cleanup_for_test_type_create(self):
        ''''''
        # 1.
        self._restore_ori_cfg_for_source_target_zd()

        # 2. Delete the new cfg obtained from source ZD
        self._delete_zd_cfg(
            dict(cfg_desc=self.p['settings_to_get_new_cfg_from_source_zd']['cfg']['cfg_desc'])
        )

        # 3. Delete the original cfg obtained from source ZD
        self._delete_zd_cfg(
            dict(cfg_desc=self.p['settings_to_get_ori_cfg_from_source_zd']['cfg']['cfg_desc'])
        )

        # 4. Delete the original cfg obtained from target ZD
        self._delete_zd_cfg(
            dict(cfg_desc=self.p['settings_to_get_ori_cfg_from_target_zd']['cfg']['cfg_desc'])
        )

        self.source_zd.stop()
        self.target_zd.stop()

    def _cleanup_for_test_type_cancel(self):
        ''''''
        try:
            # 1. Delete the cfg obtained from source ZD
            self._delete_zd_cfg(
                dict(cfg_desc=self.p['settings_to_get_cfg_from_source_zd']['cfg']['cfg_desc'])
            )
        except Exception, e:
            logging.info('Warning: Error "%s" happens while delete the original cfg')

        # 2. Stop ZD
        self.source_zd.stop()

    def _cleanup_for_test_type_update(self):
        ''''''
        # let is raise exception to stop the test if cannot enable fm mgmt
        # 1. Enable fm management
        lib.zd.sys2.set(self.source_zd, self.p['settings_to_enable_fm_mgmt'])

        try:
            # 2. Delete the cfg obtained from source ZD
            self._delete_zd_cfg(
                dict(cfg_desc=self.p['settings_to_get_cfg_from_source_zd']['cfg']['cfg_desc'])
            )
        except Exception, e:
            logging.info('Warning: Error "%s" happens while delete the original cfg')
        # 2. Delete the task in case cannot cancel it, need this step???
        self.source_zd.stop()


