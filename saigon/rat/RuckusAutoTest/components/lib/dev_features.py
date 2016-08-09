class FM:
    ''' put table headers here for cross checkup, one place change '''
    # on Cfg > ... for selecting view/devices
    cfg_view_ths = ['name', 'serial', 'ip', 'ex_ip', 'model', 'status', 'uptime', 'tag']
    cfg_device_ths = ['select', 'name', 'serial', 'ip', 'ex_ip', 'model',
                    'status', 'uptime', 'tag']
    task_ths = ['id', 'task_name', 'schedule', 'created', 'by', 'cfg_file', 'actions', 'status']
    task_detail_ths = ['name', 'serial', 'model', 'ip', 'from', 'to', 'status', 'failure']
    reboot_task_detail_ths = ['name', 'serial', 'model', 'ip', 'version', 'status', 'failure']

    # on Inv > Reports (normal cases)
    # NOTE: same key with report_cates
    report_ths = dict(
        aps = ['name', 'serial', 'mac', 'ip', 'model', 'last_seen',
                'uptime', 'tag', 'firmware', 'conn'],
        assoc = ['name', 'serial', 'mac', 'ip', 'model', 'last_seen',
               'uptime', 'tag', 'firmware', 'conn', 'assoc'],
        prov = ['task_name', 'schedule', 'created', 'by', 'devices', 'details', 'status'],
        zds = ['name', 'ip', 'mac', 'last_seen', 'model', 'serial', 'version',
             'uptime', 'aps', 'clients', 'rogue', 'conn'],
        zd_ap = ['name', 'desc', 'zd_name', 'mac', 'model', 'status', 'ip', 'channel',
               'radiotype', 'max_clients', 'min_clients', 'uptime', 'disconn_clients',
               'type', 'upstream', 'clients', 'impacted_aps', 'uplink_rssi', 'downlink_rssi',
               'details'],
        zd_client = ['mac', 'zd_name', 'ip', 'ap_name', 'wlan', 'channel', 'radio', 'signal', 'status'],
    )
    ar_ths = ['name', 'freq', 'email', 'attr', 'action']
    # on Admin > Users
    user_ths = ['username', 'last_login', 'role', 'action']
    # on Admin > View Mgmt
    view_mgmt_ths = ['view', 'desc', 'context', 'action']
    inv_status_ths = ['status', 'action']

    # on Admin > Managed Device Assignment
    device_assignment_ths = ['groupname', 'action']

    # on Dashboard: conn, disconn are context based fields
    zd_device_view_ths = ['view', 'conn', 'disconn', 'conn_ap', 'disconn_ap', 'client', 'event']
    ap_device_view_ths = ['view', 'conn', 'seen_1d', 'seen_2d', 'disconn', 'client', 'event']

    license_ths = ['key', 'part_num', 'ap_count', 'created']

    # on Configure > Fw Status
    fw_status_ths = ['model', 'firmware', 'date', 'total_devices', 'action']

    # those below attrs from Inventory > Manage Devices/Reports
    attrs = dict(
        device_name = 'Device Name',
        serial = 'Serial Number',
        ip = 'IP Address',
        ex_ip = 'External IP Address',
        model = 'Model Name',
        last_seen = 'Device Last Seen',
        uptime = 'Uptime',
        tag = 'Tag',
        auto_cfg = 'Auto Configured',
        firmware = 'Firmware Version',
    )
    ops = dict(
        equals = 'Exactly equals',
        contains = 'Contains',
        starts_with = 'Starts with',
        ends_with = 'Ends with'
    )

    device_cate = dict(
        aps = 'Standalone APs',
        zds = 'ZoneDirectors',
    )

    predef_views = dict(
        aps = 'All Standalone APs',
        #zf_aps='ZoneFlex Standalone APs', # removed on 8.2.x
        #vf_aps='MediaFlex Standalone APs',
        zds = 'All ZoneDirectors',
    )
    # those below attrs are from Inventory > Reports
    report_cates = dict(
        device_view = 'Device View',
        active_fw = 'Active Firmware',
        conn = 'Historical Connectivity',
        assoc = 'Association',
        prov = 'Provision',
        event = 'Events',
        timeline = 'Event Timeline',
        event_details = 'Detailed Events',
    )
    # report_types is drived by predef_views
    report_types = dict(
        aps = 'APs',
        cur_conn = 'Currently Connected',
        cur_disconn = 'Currently Disconnected',
        conn_clients = 'Connected Clients',
        last_seen_24 = 'Seen in Last 24 hours',
        last_seen_48 = 'Seen in Last 48 hours',
        # ZD case
        zds = 'ZoneDirectors',
        zd_ap = 'All Access Points',
        zd_client = 'Connected Clients',
    )

    # Admin > Users
    roles = dict(
        network_admin = 'Network Administrator',
        group_admin = 'Group Administrator',
        group_op = 'Group Operator',
        device_op = 'Device Operator',
    )

