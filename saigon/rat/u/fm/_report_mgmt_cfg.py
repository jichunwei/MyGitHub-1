'''
This tea to work with Reports page.

1. Reports foundation development
  + to cover those pages: Device View, Active Firmware, Historical
     Connectivity, Association, Provision, Events, Speed Flex
  + to provide basic report activities:
    + fill in report options (inc. filters)
    + generate the report
    + get the report results
  + unsupported features: save reports, export reports

Examples to generate report:
tea.py u.fm.report_mgmt fm_ip=192.168.20.252 action=generate report_param=dv_report_zd_params
tea.py u.fm.report_mgmt fm_ip=192.168.20.252 action=generate report_param=dv_report_ap_params
tea.py u.fm.report_mgmt fm_ip=192.168.20.252 action=generate report_param=connectivity_report_zd_params
tea.py u.fm.report_mgmt fm_ip=192.168.20.252 action=generate report_param=connectivity_report_ap_params
tea.py u.fm.report_mgmt fm_ip=192.168.20.252 action=generate report_param=provision_report_params
tea.py u.fm.report_mgmt fm_ip=192.168.20.252 action=generate report_param=events_report_params
tea.py u.fm.report_mgmt fm_ip=192.168.20.252 action=generate report_param=speed_flex_report_params

Examples to create report:


Example for report option and filter options

save_cfg = dict(include_filter = True, # False
        include_header = True, # False
        schedule = True, # False
        frequency = 'Weekly', # | 'Weekly' | 'Monthly',
        day_of_week = 'Monday',
        time_of_day = '3:00', # '2:00', '3:00', ...
        am_pm = 'PM', # 'PM'
        email_report = 'admin@ruckus.com',
)

advance_cfg = dict(include_filter = True, # False
        include_header = True, # False
        schedule = True, # False
        frequency = 'Monthly', # | 'Weekly' | 'Monthly',
        day_of_month = 1,
        time_of_day = '3:00', # '2:00', '3:00', ...
        am_pm = 'AM', # 'PM'
        email_report = 'admin@ruckus.com',
)
'''

import copy
#-------------------------------------------------------------------------------
# It is too long to write these params and their values on command line.
# So define them here for  generating/creating reports.

general_save_cfg = dict(
    include_filter = True,
    include_header = True,
    time_of_day = '6:00', # '2:00', '3:00', ...
    am_pm = 'AM', # 'PM'
    email_report = 'admin@ruckus.com',
)

save_cfg_daily_type = dict(
    schedule = True,
    frequency = 'Daily', # | 'Weekly' | 'Monthly',
)
save_cfg_daily_type.update(general_save_cfg)

save_cfg_weekly_type = dict(
    schedule = True, # False
    frequency = 'Weekly', # | 'Weekly' | 'Monthly',
    day_of_week = 'Monday',
)
save_cfg_weekly_type.update(general_save_cfg)

save_cfg_monthly_type = dict(
    schedule = True, # False
    frequency = 'Monthly', # | 'Weekly' | 'Monthly',
    day_of_month = 1,
)
save_cfg_monthly_type.update(general_save_cfg)

################################################################################
# NOTE: Currently cannot generate/create report with filters "Model Name" and
# "Connection". Bug: 15203
################################################################################

#1. params to generate a report and get it result from Report Categories
dv_report_zd_params = dict(
    #action = 'generate',
    report_type = 'device_view',
    get_result = True,
    report_options = [
        'All ZoneDirectors', 'ZoneDirectors',
    ],
    filter_options = [
        ['ZoneDirector Name', 'Contains', 'Ruckus'],
        ['Version', 'Contains', '9.0']
    ],
    save_cfg = save_cfg_daily_type,
)
# params to create/generate zd Device View report from Saved Reports
manage_dv_report_zd_params = copy.deepcopy(dv_report_zd_params)
manage_dv_report_zd_params.update(
    report_options = [
        'Device View', 'All ZoneDirectors', 'ZoneDirectors',
    ],
)

dv_report_ap_params = dict(
    #action = 'generate',
    report_type = 'device_view',
    get_result = True,
    report_options = [
        'All Standalone APs', 'Currently Connected',
    ],
    filter_options = [
        ['Device Name', 'Contains', 'Ruckus'],
        ['Uptime', 'Greater than', '1', 'Hours']
    ],
    save_cfg = save_cfg_weekly_type,
)
# params to create/generate ap Device View report from Saved Reports
manage_dv_report_ap_params = copy.deepcopy(dv_report_ap_params)
manage_dv_report_ap_params.update(
    report_options = [
        'Device View', 'All Standalone APs', 'Currently Connected',
    ],
)

connectivity_report_zd_params = dict(
    #action = 'generate',
    report_type = 'connectivity',
    get_result = True,
    report_options = [
        'All ZoneDirectors', 'Disconnected ZoneDirectors', # 'Connected ZoneDirectors',
    ],
    filter_options = [
        ['Device Last Seen', 'Earlier than', '2010-07-26', '06:00:00 AM'],
    ],
    save_cfg = save_cfg_monthly_type,
)

manage_connectivity_report_zd_params = copy.deepcopy(connectivity_report_zd_params)
manage_connectivity_report_zd_params.update(
    report_options = [
        'Historical Connectivity', 'All ZoneDirectors', 'Disconnected ZoneDirectors',
    ],
)

connectivity_report_ap_params = dict(
    #action = 'generate',
    report_type = 'connectivity',
    get_result = True,
    report_options = [
        'All Standalone APs', 'Connected',
    ],
    filter_options = [
        ['Uptime', 'Greater than', 5, 'Hours'],
        ['Software', 'Contains', '9.0']
    ],
    save_cfg = save_cfg_daily_type,
)
manage_connectivity_report_ap_params = copy.deepcopy(connectivity_report_ap_params)
manage_connectivity_report_ap_params.update(
    report_options = [
        'Historical Connectivity', 'All Standalone APs', 'Connected',
    ],
)

# report params for Provision report
provision_report_params = dict(
    #action = 'generate',
    report_type = 'provision',
    get_result = True,
    report_options = [
        'Configuration Upgrade',
    ],
    filter_options = [
        ['Created by', 'Starts with', 'admin'],
    ],
    save_cfg = save_cfg_weekly_type,
)

manage_provision_report_params = copy.deepcopy(provision_report_params)
manage_provision_report_params.update(
    report_options = [
        'Provision', 'Configuration Upgrade',
    ],
)

# report params for Events report
events_report_params = dict(
    #action = 'generate',
    report_type = 'events',
    get_result = True,
    report_options = [
        'Events', 'Standalone APs',
        'Value changed due to configuration request'
    ],
    filter_options = [
        ['IP Address', 'Starts with', '192.168']
    ],
    save_cfg = save_cfg_monthly_type,
)

manage_events_report_params = copy.deepcopy(events_report_params)
manage_events_report_params.update(
    report_options = [
        'Events', 'Events', 'Standalone APs',
        'Value changed due to configuration request'
    ],
)

# report params for Speed Flex report
speed_flex_report_params = dict(
    #action = 'generate',
    report_type = 'speed_flex',
    get_result = True,
    report_options = None,
    filter_options = [
        ['Executor', 'Starts with', 'admin']
    ],
    save_cfg = save_cfg_daily_type,
)

manage_speed_flex_report_params = copy.deepcopy(speed_flex_report_params)
manage_speed_flex_report_params.update(
    report_options = [
        'Speed Flex',
    ],
)

