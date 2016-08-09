'''
to walk FM managed components of specified views
    [list of view]:
    1. create components relationship with dict [tree] structure with
       neccessary attributes
        1.1 provide a get method for all devices in FM > Inventory
        1.2 check connections on FM > Inventory to see if the device
            is connected or not
        1.3 go to FM > report and check the device statuses
    2. write components' dict structure to data file
        2.1 using RAT_FM_WALK_REPORT_FILE environment variable to point to
            dictionary/files if presented
        2.2 using default filename "walk_status_report.log" if nothing is given
    3. executed with different time or different build to verify device
       status after event
        3.1 used by status monitor program to idetify the diff of components

Examples:
tea.py u.fm.walk_managed_devices fm_ip_addr=97.74.124.173 action=create_view view_name=ruckus_view device_category="Standalone APs" options="[['Device Name', 'Contains', 'att'], 'or', ['Serial Number', 'Ends with', '2210']]"
tea.py u.fm.walk_managed_devices fm_ip_addr=97.74.124.173 action=monitor view_name=ruckus_view interval=1 repeat=3 report_options="['Historical Connectivity', 'luan_view', 'Disconnected']"
tea.py u.fm.walk_managed_devices action=dump_report
tea.py u.fm.walk_managed_devices action=report_currently_disconn
'''


import os
import logging
import time
from pprint import pformat

from RuckusAutoTest.common.utils import get_cfg_items
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.components import Helpers as lib

REPORT_FILE_ENV_KEY = 'RAT_FM_WALK_REPORT_FILE'


def write_to_file(filename, text):
    '''
    . write components' dict structure to data file
    '''
    fh = open(filename, 'a+')
    fh.write(text + '\n')
    fh.close()


def read_from_file(filename):
    '''
    . read all the content from file and parse, return as list of dict
    '''
    fh = open(filename, 'r+')
    res = [eval(l) for l in fh]
    fh.close()
    return res


def create_view(cfg):
    '''
        view_name=luan_view device_category='Standalone APs'
        options="[['Device Name', 'Contains', 'att'], 'or',
                  ['Serial Number', 'Ends with', '2210']]"
    '''
    # just select required items for calling create_view function
    p = get_cfg_items(cfg, ['fm', 'view_name', 'device_category', 'options'])

    logging.info('Create a view [%s]' % p['view_name'])
    logging.debug('\n%s' % pformat(p))
    lib.fm.idev.create_view(**p)
    return dict(result='PASS', message='View [%s] is created' % p['view_name'])


def _get_disconnected_devices(devices):
    return [d for d in devices if d['conn'] == 'disconnect']


def _loop(repeat, interval):
    '''
    . iterately return the point for execution
    input
    . interval: mins
    '''
    if repeat <= 0:
        raise Exception('repeat param must be greater than zero')
    c = 0
    yield c

    c += 1
    while c < repeat:
        c += 1
        time.sleep(interval * 60)
        logging.info('Wait for %s mins before next getting...' % interval)
        yield c


def _get_report_details(fm, report_options):
    '''
    . go to reports page and get info
    '''
    return lib.fm.reports.generate_report(fm, report_options,
                                          get_results = True)


def _monitor(cfg):
    '''
    . get the disconnected devices
    . write to file
    '''
    logging.info('Monitoring devices of view [%s]' % cfg['view_name'])
    for c in _loop(cfg['repeat'], cfg['interval']):
        cfg['fm'].start()
        devs = lib.fm.idev.get_all_devices_by_view_name(cfg['fm'],
                                                        cfg['view_name'])
        #logging.debug('\n%s' % pformat(devs))
        report = dict(
            timestamp = time.strftime('%m/%d/%Y %H:%M:%S'),
            disconn_devs = _get_disconnected_devices(devs),
            report_details = _get_report_details(cfg['fm'],
                                                 cfg['report_options']),
        )
        cfg['fm'].stop()
        logging.info('Save results to file %s...' % cfg['report_file'])
        write_to_file(cfg['report_file'], str(report))

    return dict(result='PASS',
                message='Report is filled in file [%s]' % cfg['report_file'])


def _dump_report(cfg):
    logging.info('Get all the written down info for report')
    r = read_from_file(cfg['report_file'])
    if not len(r):
        return dict(result='ERROR',
                    message='Nothing is in the report to be dump')

    logging.info(pformat(r))
    return dict(result='PASS', message='The whole report is dump')


def _report_currently_disconn(cfg):
    '''
    . dump out the last item on written down reports
    '''
    logging.info('Get all the written down info for report')
    reports = read_from_file(cfg['report_file'])
    if len(reports):
        logging.info(pformat(reports[-1]))
    else:
        return dict(result='ERROR',
                    message='There is nothing on the report file')

    return dict(result='PASS',
                message='The currently disconnected devices are listed')


def _report_by_device(cfg):
    logging.info('Get all the written down info for report')
    reports = read_from_file(cfg['report_file'])
    if len(reports):
        dev_reports = []
        for r in reports:
            #print r['timestamp']
            for dev in r['disconn_devs']:
                #print dev['serial']
                if str(cfg['serial']) == dev['serial']:
                    dev_reports.append(r['timestamp'])
                    break
        if len(dev_reports):
            logging.info('Disconnected times of device [%s]:' % cfg['serial'])
            for i in dev_reports:
                logging.info(i)
            logging.info('')
        else:
            logging.info('The device [%s] is not disconnected anytime'
                         % cfg['serial'])
    else:
        logging.info('ERROR: There is nothing on the report file')


def do_config(cfg):
    p = dict(
        fm_ip_addr = '192.168.20.252',
        report_file = 'walk_status_report.log', # default name
    )
    p.update(cfg)

    if REPORT_FILE_ENV_KEY in os.environ:
        cfg['report_file'] = os.environ[REPORT_FILE_ENV_KEY]

    # in report case, we don't need FM
    if not 'report' in p['action'].lower():
        p['fm'] = create_fm_by_ip_addr(cfg.pop('fm_ip_addr'))

    return p


def do_test(cfg):
    if cfg['action'] == 'dump_report':
        res = _dump_report(cfg)
    if cfg['action'] == 'report_currently_disconn':
        res = _report_currently_disconn(cfg)

    if cfg['action'] == 'create_view':
        res = create_view(cfg)
    if cfg['action'] == 'monitor':
        res = _monitor(cfg)

    return res


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
