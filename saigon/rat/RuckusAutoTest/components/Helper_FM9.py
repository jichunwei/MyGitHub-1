#from RuckusAutoTest.components.lib import fm_firmware_manager as fm_fw
from RuckusAutoTest.components.lib.fm import (
        common_config_fm_old as cfg, # common config

        inv_reports_fm as ireports, # reports
        inv_reports2 as reports, # new version of ireports
        reg_status_mgmt_fm as dreg, # device reg
        auto_cfg_rule_fm as auto_cfg, # dev reg > auto cfg

        # provisioning
        fw_upgrade_fm as fwup,
        factory_reset_fm as fr, # factory reset
        ap_reboot_fm as ap_reboot,
        cfg_template_fm as cfg_tmpl,
        cfg_upgrade_fm as cfg_upgr,
        zd_cfg_mgmt_fm as zd_cfg,
        zd_cloning_fm as zd_cloning,
        cfg_fw_status_fm as fw_status,

        # admin
        admin_users_fm as user,
        admin_view_mgmt_fm as view,
        admin_assign_devices_fm as da, # device assignment
        admin_assign_groups_fm as ga, # group assignment

        # old modules: don't use these for new development
        fw_upgrade_fm_old as fwUpgrade,
        factory_reset_fm_old as factoryReset,
        ap_reboot_fm_old as apReboot,
        user_manager_fm_old as userMgmt,
        fw_manager_fm_old as fw,
)

# put override stuffs here
from RuckusAutoTest.components.lib.fm9 import (
        inv_device_mgmt as idev, # device management
        report_mgmt as rp,
        dashboard,
        zd_cfg_tmpl as zd_tmpl,
        zd_cfg_tasks as zd_cu, # ZD config upgrade
        speedflex,
        zd_event_cfg as zd_ec, #ZD Event Config
)
