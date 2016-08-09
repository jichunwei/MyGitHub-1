'''
This Report Foundation lib cover following pages and support almost necessary functions:
. Pages:
    1.    Manage Reports:
    . Saved Reports.
    2.    Report Categories:
    . Device View, Active Firmware, Historical, Connectivity, Association, Provision, Events and Speed Flex.

. Functions:
    1. Generate report from Manage Report and Report Categories page.
    2. Create/Save report from Manage Report and Report Categories page.
    3. Export report to xls from Manage Report and Report Categories page.
    4. Query/Edit/Delete saved reports in Mange Report page.
'''
import re
import logging
import copy
from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.common.utils import download_file
from RuckusAutoTest.components.lib.fm9 import _report_filter as rf
from RuckusAutoTest.components.lib import common_fns as fns
#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def generate_device_view_report(fm,
                                report_options = None,
                                filter_options = None,
                                get_result = True
    ):
    '''
    . generate report from Report Categories
    . None: get default option to query
    '''
    return _generate(
        fm, 'device_view', report_options, filter_options, get_result
    )

def generate_active_firmware_report(fm,
                                    report_options = None,
                                    filter_options = None,
                                    get_result = True
    ):
    '''
    . generate report from Report Categories
    '''
    return _generate(
        fm, 'active_firmware', report_options, filter_options, get_result
    )

def generate_connectivity_report(fm,
                                 report_options = None,
                                 filter_options = None,
                                 get_result = True
    ):
    '''
    . generate report from Report Categories
    '''
    return _generate(
        fm, 'connectivity', report_options, filter_options, get_result
    )

def generate_association_report(fm,
                                report_options = None,
                                filter_options = None,
                                get_result = True
    ):
    '''
    . generate report from Report Categories
    '''
    return _generate(
        fm, 'association', report_options, filter_options, get_result
    )

def generate_provision_report(fm,
                              report_options = None,
                              filter_options = None,
                              get_result = True
    ):
    '''
    . generate report from Report Categories
    '''
    return _generate(
        fm, 'provision', report_options, filter_options, get_result
    )

def generate_events_report(fm,
                           report_options = None,
                           filter_options = None,
                           get_result = True
    ):
    '''
    . generate report from Report Categories
    '''
    return _generate(
        fm, 'events', report_options, filter_options, get_result
    )

def generate_speed_flex_report(fm,
                               report_options = None,
                               filter_options = None,
                               get_result = True
    ):
    '''
    . generate report from Report Categories
    '''
    return _generate(
        fm, 'speed_flex', report_options, filter_options, get_result
    )

def create_device_view_report(fm,
                              report_name,
                              report_options = None,
                              filter_options = None,
                              save_cfg = dict(include_filter = False,
                                              include_header = False,
                                              schedule       = False),
                              get_result = False
    ):
    '''
    . generate and save report from Report Categories

    #save_cfg dict for daily
    save_cfg = dict(
        include_filter = True, # False
        include_header = True, # False
        schedule = True, # False
        frequency = 'Daily', # | 'Weekly' | 'Monthly',
        time_of_day = '1:00', # '2:00', '3:00', ...
        am_pm = 'AM', # 'PM'
        email_report = 'admin@ruckus.com',
    )
    # save_cfg dict for weekly
    save_cfg = dict(
        frequency = 'Weekly',
        day_week = 'Sunday', # 'Monday', 'Tuesday'
        time_of_day = '1:00', # '2:00', '3:00', ...
        am_pm = 'AM', # 'PM'
        email_report = 'admin@ruckus.com',
    )
    # save_cfg dict for monthly
    save_cfg = dict(
        frequency = 'Monthly',
        day_month = 1, #2, 3, ..., 31
        time_of_day = '1:00', # '2:00', '3:00', ...
        am_pm = 'AM', # 'PM'
        email_report = 'admin@ruckus.com',
    )
    '''
    _create_report(
        fm, report_name, 'device_view', report_options,
        filter_options, save_cfg, get_result
    )

def create_active_firmware_report(fm,
                                   report_name,
                                   report_options = None,
                                   filter_options = None,
                                   save_cfg = dict(include_filter = False,
                                                   include_header = False,
                                                   schedule       = False),
                                   get_result = False
    ):
    '''
    . generate and save report from Report Categories
    '''
    _create_report(
        fm, report_name, 'active_firmware',
        report_options, filter_options, save_cfg
    )

def create_connectivity_report(fm,
                               report_name,
                               report_options = None,
                               filter_options = None,
                               save_cfg = dict(include_filter = False,
                                               include_header = False,
                                               schedule       = False),
                               get_result = False
    ):
    '''
    . generate and save report from Report Categories
    '''
    _create_report(
        fm, report_name, 'connectivity', report_options,
        filter_options, save_cfg, get_result
    )

def create_association_report(fm,
                              report_name,
                              report_options = None,
                              filter_options = None,
                              save_cfg = dict(include_filter = False,
                                              include_header = False,
                                              schedule       = False),
                              get_result = False
    ):
    '''
    . generate and save report from Report Categories
    '''
    _create_report(
        fm, report_name, 'association', report_options,
        filter_options, save_cfg, get_result
    )

def create_provision_report(fm,
                            report_name,
                            report_options = None,
                            filter_options = None,
                            save_cfg = dict(include_filter = False,
                                            include_header = False,
                                            schedule       = False),
                            get_result = False
    ):
    '''
    . generate and save report from Report Categories
    '''
    return _create_report(
        fm, report_name, 'provision', report_options,
        filter_options, save_cfg, get_result
    )

def create_events_report(fm,
                        report_name,
                        report_options = None,
                        filter_options = None,
                        save_cfg = dict(include_filter = False,
                                        include_header = False,
                                        schedule       = False),
                        get_result = False
    ):
    '''
    . generate and save report from Report Categories
    '''
    _create_report(
        fm, report_name, 'events', report_options,
        filter_options, save_cfg, get_result
    )

def create_speed_flex_report(fm,
                             report_name,
                             report_options = None,
                             filter_options = None,
                             save_cfg = dict(include_filter = False,
                                             include_header = False,
                                             schedule       = False),
                             get_result = False
    ):
    '''
    . generate and save report from Report Categories
    '''
    _create_report(
        fm, report_name, 'speed_flex', report_options,
        filter_options, save_cfg, get_result
    )


def generate_report_from_manage(fm,
                                     report_options = None,
                                     filter_options = None,
                                     get_result     = True,
    ):
    return _generate_report_from_manage(
        fm, report_options, filter_options, get_result
    )


def create_report_from_manage_page(fm,
                                   report_name,
                                   report_options = None,
                                   filter_options = None,
                                   save_cfg = dict(include_filter = False,
                                                   include_header = False,
                                                   schedule       = False),
                                   get_result = False
    ):
    return _create_report_from_manage(
        fm, report_name, report_options,
        filter_options, save_cfg, get_result
    )


def export_device_view_report(fm,
                              report_options = None,
                              filter_options = None
    ):
    '''
    . to export Device View report report from Report Categories
    . None: get default option to query
    '''
    return _export(
        fm, 'device_view', report_options, filter_options
    )

def export_active_firmware_report(fm,
                                  report_options = None,
                                  filter_options = None,
    ):
    '''
    . to export active firmware report from Report Categories
    '''
    return _export(
        fm, 'active_firmware', report_options, filter_options
    )

def export_connectivity_report(fm,
                               report_options = None,
                               filter_options = None
    ):
    '''
    . to export connectivity report from Report Categories
    '''
    return _export(
        fm, 'connectivity', report_options, filter_options
    )

def export_association_report(fm,
                              report_options = None,
                              filter_options = None
    ):
    '''
    . to export report from Report Categories
    '''
    return _export(
        fm, 'association', report_options, filter_options
    )

def export_provision_report(fm,
                            report_options = None,
                            filter_options = None
    ):
    '''
    . to export report from Report Categories
    '''
    return _export(
        fm, 'provision', report_options, filter_options
    )

def export_events_report(fm,
                         report_options = None,
                         filter_options = None
    ):
    '''
    . to export report from Report Categories
    '''
    return _export(
        fm, 'events', report_options, filter_options
    )

def export_speed_flex_report(fm,
                             report_options = None,
                             filter_options = None
    ):
    '''
    . to export report from Report Categories
    '''
    return _export(
        fm, 'speed_flex', report_options, filter_options
    )

def export_report_from_manage(fm,
                              report_options = None,
                              filter_options = None
    ):
    '''
    . this function does export report in the Manage Report page:
        . fill report and filter options.
        . do query.
        . export report from Mangage Reports > Saved Reports page
    . return full path of xls file if success
    '''
    _generate_report_from_manage(
        fm, report_options, filter_options, False
    )
    fm.selenium.click_and_wait(locators['xls_file'])
    file_name = "".join(report_options) + '.xls'

    return download_file(file_name)

def edit_report_name(fm, old_name, new_name):
    '''
    . to rename a report
    . raise exception if fail
    '''
    return _edit_report(fm, old_name, new_name, None, None, {}, False)

def edit_criteria_query(fm,
                          report_name,
                          new_report_options = None,
                          new_filter_options = None,
                          get_result = True
    ):
    '''
    . to edit criteria query.
    . raise exception if fail
    '''
    return _edit_report(
        fm, report_name, report_name, new_report_options,
        new_filter_options, {}, get_result
    )

def edit_save_cfg(fm, report_name, new_save_cfg):
    '''
    . to modify save cfg of a report
    . raise exception if fail
    '''
    return _edit_report(
        fm, report_name, report_name, None, None, new_save_cfg, False
    )

def edit_all_report_attributes(fm,
                report_name,
                new_name,
                report_options = None,
                filter_options = None,
                save_cfg = {},
                get_result = True
    ):
    '''
    . to edit all report settings: report name, report options, filter options,
      save config,
    . raise exception if fail
    '''
    return _edit_report(
        fm, report_name, new_name, report_options,
        filter_options, save_cfg, get_result
    )

def delete_report(fm, report_name):
    s = fm.selenium
    r_info = find_report(fm, report_name)

    if not r_info:
        raise Exception('Not found report %s' % report_name)

    s.click_and_wait(r_info['links']['delete'])
    # Get OK, Cancel pop up. Otherwise, an exception will be raised and this selenium fails.
    if s.is_confirmation_present():
        logging.info('Got a pop up window "%s"' % s.get_confirmation())

    return

def query_report(fm, report_name, filter_txt = '', match = {}):
    '''
    . to get result from a saved report
    . filter_txt: text do do filter with search box
    '''
    _query_report(fm, report_name, filter_txt, match)
    cfg = _select_filter_txt('result_tbl', filter_txt, match, [])

    return _get_tbl(fm, 'result_tbl', cfg)

def export_report(fm, report_name):
    '''
    . to export a saved report
    . return full path of the file or raise exception if fail.
    '''
    _query_report(fm, report_name)
    fm.selenium.click_and_wait(locators['xls_file'])
    wild_char_pat = '[~!@#$%^&*()+\\\|{}:"<>?\[\];\',./= ]'
    revised_name = re.sub(wild_char_pat, '', report_name)

    return download_file(revised_name + '.xls')

#-----------------------------------------------------------------------------
# AFTER GENERARTING THE REPORT, THOSE FUNCTIONS CAN BE CALLED
#-----------------------------------------------------------------------------
def get_report_result(fm):
    '''
    . return the result of a report generation
    '''
    return _get_report_result(fm)

#-----------------------------------------------------------------------------
#  PROTECTED METHODS
#-----------------------------------------------------------------------------
result_parent_div = "//div[@dojoattachpoint='dataAreaFirstLayerContainer']"
report_list_parent_div = "//div[@dojoattachpoint='savedReportsContainer']"

locators = dict(
    report_name = Ctrl("//input[@dojoattachpoint='reportNameField']",'text'),
    query_btn = "//input[@dojoattachpoint='queryButton']",
    save_btn = Ctrl("//input[@value='Save Report']", 'button'),
    cancel_btn = Ctrl("//input[@value='Cancel']", 'button'),
    refresh_btn = Ctrl("//div[@id='refreshButtonArea']/img[contains(@src,'img_Refresh.gif')]", 'button'), # for FM9.0
    result_msg = "//a[@id='statusMessageLink']",
    xls_file = "//input[@value='XLS File']",
    # on 'Manage * Views' pages ---
    result_tbl = Ctrl(
        dict(tbl = result_parent_div + "//table[@dojoattachpoint='tableArea']",
             nav = result_parent_div + "//table[@class='pageSelector']",
             search_box = result_parent_div + "//input[@dojoattachpoint='searchBoxTextField']"),
        'ltable',
        cfg = dict(
            hdr_attr = 'class',
            #get = 'all',
        ),
    ),
    include_filter = Ctrl("//input[@dojoattachpoint='includeFilter']",'check'),
    include_header = Ctrl("//input[@dojoattachpoint='includeHeader']",'check'),

    schedule = Ctrl("//input[@dojoattachpoint='enableAutoReport']",'check'),
    email_report = Ctrl("//input[@dojoattachpoint='autoEmailField']",'text'),
    frequency = Ctrl("//td[contains(preceding-sibling::td, 'Frequency')]/span", 'dojo_select'),
    # schedule for daily report
    time_of_day = Ctrl("//td[contains(preceding-sibling::td, 'Time of Day')]/span[1]", 'dojo_select'),
    am_pm = Ctrl("//td[contains(preceding-sibling::td, 'Time of Day')]/span[2]", 'dojo_select'),
    #Schedule for weekly report
    day_of_week = Ctrl("//td[contains(preceding-sibling::td, 'Day of the Week')]/span", 'dojo_select'),
    day_of_month = Ctrl("//td[contains(preceding-sibling::td, 'Day of the Month')]/span", 'dojo_select'),

    # for items on Manage Reports > Saved Reports
    new_report = "//input[@dojoattachpoint='newReportButton']",
    report_list = Ctrl(
        dict(tbl = report_list_parent_div + "//table[@dojoattachpoint='tableArea']",
             nav = report_list_parent_div + "//table[@class='pageSelector']",),
        'ltable',
        cfg = dict(
            hdr_attr = 'class',
            links = dict(
                query = "//span[@class='sb'][.='Query']",
                edit = "//span[@class='sb'][.='Edit']",
                delete = "//span[@class='sb'][.='Delete']",
            ),
        ),
    ),
    delele_all_filter = "//a[@dojoattachpoint='deleteAllButton']",
)

SUCCESS_MSG = 'success'

ctrl_order = '''
'''

save_report_co = '''
[None report_name include_filter include_header schedule frequency
time_of_day am_pm day_of_week day_of_month email_report save_btn]
'''

def _get_loc(fm, page):
    return dict(
        saved_reports = fm.REPORTS_SAVE,

        device_view = fm.REPORTS_DEVICE_VIEW,
        active_firmware = fm.REPORTS_ACTIVE_FIRMWARE,
        connectivity = fm.REPORTS_HISTORICAL,
        association = fm.REPORTS_ASSOCIATION,
        provision = fm.REPORTS_PROVISION,
        events = fm.REPORTS_EVENT,
        speed_flex = fm.REPORTS_SPEED_FLEX,
        capacity = fm.REPORTS_CAPACITY,
        sla = fm.REPORTS_SLA,
        troubleshooting = fm.REPORTS_TROUBLESHOOT,
    )[page]


def nav_to(fm, page = 'save_reports', force = True):
    fm.navigate_to(fm.REPORTS, _get_loc(fm, page), force = force)

m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = None, # don't use now
)


def _set(fm, cfg, order = 'default'):
    return fns.set(m, fm, cfg, is_nav = False, order = order)

def _get(fm, cfg, order = 'default'):
    return fns.get(m, fm, cfg, is_nav = False, order = order)

def _get_result_status(fm):
    '''
    . return
        None if success
        raise exception if other.
    '''
    s, l = fm.selenium, locators
    msg = s.get_text(l['result_msg'])

    if re.search(SUCCESS_MSG, msg, re.I):
        return None

    raise Exception('Cannot save the report. Error: %s' % msg)

def _get_tbl(fm, tbl, cfg={}, order = None):
    return fns.get_tbl(m, fm, tbl, cfg, is_nav = False, order = order)

def _select_filter_txt(tbl,
                       filter_txt = '',
                       match= {},
                       ignore_fields = []
    ):
    '''
    NOTE: Not have a good idea to use this function yet.

    . some of fields can not be used as filter text (i.e. conn),
      this functions select a good field text to filter results
    input
    . filter_txt: text do do filter with search box
    . tbl_cfg will be updated accordingly
    '''
    tbl_cfg = {}
    tbl_cfg['search_box'] = filter_txt
    tbl_cfg['match'] = copy.deepcopy(match)
    for k in ignore_fields:
        try:
            del tbl_cfg['match'][k]
        except:
            pass

    return tbl_cfg


def _save_query_result(fm,
                       report_name,
                       cfg = {}
    ):
    '''
    . save the report
    . cfg = dict(
            include_filter = False,
            include_header = False,
            schedule       = False
      )
    '''
    p = dict(
        report_name = report_name,
    )

    if cfg:
        p.update(cfg)
    _set(fm, p, order = save_report_co)

    return _get_result_status(fm)


def _generate(fm,
              report_type    = 'device_view',
              report_options = None,
              filter_options = None,
              get_result     = False,
              filter_txt     = ''
    ):
    '''
    . to support generating a report from Report Categories
    '''
    nav_to(fm, report_type, True)
    return _fill_in_criteria(
        fm, report_options, filter_options, get_result, filter_txt
    )


def _generate_report_from_manage(fm,
                                 report_options = None,
                                 filter_options = None,
                                 get_result     = False,
                                 filter_txt = ''
    ):
    '''
    . to support generating a report from Manage Reports page
    '''
    nav_to(fm, 'saved_reports', True)
    fm.selenium.click_and_wait(locators['new_report'])

    return _fill_in_criteria(
        fm, report_options, filter_options, get_result, filter_txt
    )


def _create_report(fm,
                   report_name,
                   report_type    = 'device_view',
                   report_options = None,
                   filter_options = None,
                   save_cfg       = dict(include_filter = False,
                                         include_header = False,
                                         schedule       = False),
                   get_result = False
    ):
    '''
    '''
    res = _generate(
        fm, report_type, report_options, filter_options, get_result
    )
    msg = _save_query_result(fm, report_name, save_cfg)

    if get_result and res: return res

    return None

def _create_report_from_manage(fm,
                               report_name,
                               report_options = None,
                               filter_options = None,
                               save_cfg    = dict(include_filter = False,
                                                     include_header = False,
                                                     schedule       = False),
                               get_result     = False
    ):
    res = _generate_report_from_manage(fm, report_options, filter_options, get_result)
    msg = _save_query_result(fm, report_name, save_cfg)

    if msg:
        raise Exception('Fail to create report. Error: %s' % msg)

    if get_result and res: return res

def _export(fm,
            report_type    = 'device_view',
            report_options = None,
            filter_options = None
    ):
    '''
    . to generate and export the result to xls file from Report Categories page
    . return full path of the file
    '''
    _generate(
        fm, report_type, report_options, filter_options, False
    )
    fm.selenium.click_and_wait(locators['xls_file'])

    # get prefix for export file name
    prefix = dict(
        device_view     = 'Device View',
        connectivity    = 'Historical Connectivity',
        active_firmware = 'Active Firmware',
        association     = 'Association',
        provision       = 'Provision',
        events          = 'Events',
        speed_flex      = 'Speed Flex',
    )[report_type]

    # Speed Flex doesn't have report_options
    file_name = prefix + '.xls' \
                if report_type == 'speed_flex' else \
                prefix + "".join(report_options) + '.xls'
    file_name = file_name.replace(' ', '') # replace space

    return download_file(file_name)

def _export_report_from_manage(fm,
                               report_options = None,
                               filter_options = None
    ):
    '''
    . to generate and export the result to xls file from Report Categories page
    . return full path of the file
    '''
    _generate_report_from_manage(
        fm, report_options, filter_options, False
    )

    file_name = "".join(report_options) + '.xls'

    return download_file(file_name)

def find_report(fm, report_name):
    '''
    . to find a report with report name
    '''
    l = locators
    nav_to(fm, 'saved_reports', True)

    return _get_tbl(
        fm, 'report_list',
        dict(
             match=dict(reportname=report_name),
             op = 'equal',
             get = '1st'
        )
    )

def _edit_report(fm,
                report_name,
                new_name,
                report_options = None,
                filter_options = None,
                save_cfg = {},
                get_result = False
    ):
    '''
    . to query a report from a saved report
    . save_cfg: provide it if want to modify as below example
            #save_cfg dict for daily
            save_cfg = dict(
                include_filter = True, # False
                include_header = True, # False
                schedule = True, # False
                frequency = 'Daily', # | 'Weekly' | 'Monthly',
                time_of_day = '1:00', # '2:00', '3:00', ...
                am_pm = 'AM', # 'PM'
                email_report = 'admin@ruckus.com',
            )
            # save_cfg dict for weekly
            save_cfg = dict(
                frequency = 'Weekly',
                day_week = 'Sunday', # 'Monday', 'Tuesday'
                time_of_day = '1:00', # '2:00', '3:00', ...
                am_pm = 'AM', # 'PM'
                email_report = 'admin@ruckus.com',
            )
            # save_cfg dict for monthly
            save_cfg = dict(
                frequency = 'Monthly',
                day_month = 1, #2, 3, ..., 31
                time_of_day = '1:00', # '2:00', '3:00', ...
                am_pm = 'AM', # 'PM'
                email_report = 'admin@ruckus.com',
            )
    . return all result.

    Note: Bug 15336: FM cannot save new filter criteria if modify them from
          a saved report
    '''
    s, l = fm.selenium, locators
    r_info = find_report(fm, report_name)

    if not r_info:
        raise Exception('Not found report %s' % report_name)

    s.click_and_wait(r_info['links']['edit'])

    # only delete the current filter if new filter is provided
    if filter_options:
        s.click_and_wait(l['delele_all_filter'])

    res = _fill_in_criteria(fm, report_options, filter_options, get_result)

    # If new save_cfg is provided, use the new save config to save the report
    # Else, just click "save" button to keep original save cfg.
    new_save_cfg = {}
    if save_cfg:
        # set default = False to make _save_query_result remove all old settings
        new_save_cfg = dict(
            include_filter = False,
            include_header = False, # False
            schedule = False, # False
        )
        new_save_cfg.update(save_cfg)

    msg = _save_query_result(fm, new_name, new_save_cfg)

    if msg:
        raise Exception('Cannot save report. Error: %s' % msg)

    return res if get_result else None


#-------------------------------------------------------------------------------
#  PRIVATE METHODS
#-------------------------------------------------------------------------------
def _fill_in_criteria(fm,
                      report_options = None,
                      filter_options = None,
                      get_result     = False,
                      filter_text    = ''
    ):
    '''
    NOTE: Currently, support to get result report of pages of Report
    Categories only.
    . fill in report and filter options.
    . get_result if True
    . filter_text: text to use search box filter
    report_options = [
            'Device View', # Report Category element
            'All ZoneDirectors', # Device View element
            'ZoneDirectors', # Report Type element
    ]
    filter_options = [
            ['Device Name', 'Contains', 'al'],
            ['Serial Number', 'Starts with', '1008'],
            ['IP Address', 'Ends with', '140'],
    ]
    '''
    rf.fill_in(fm, report_options, filter_options)

    fm.selenium.click_and_wait(locators['query_btn'])
    if get_result:
        cfg = {}
        # update value for searchbox
        if filter_text:
            cfg['search_box'] = filter_text
        return _get_tbl(fm, 'result_tbl', cfg)


    return None


def _get_report_result(fm, filter_text = ''):
    '''
    . return the result of a report generation
    '''
    cfg = {}
    if filter_text:
        cfg['search_box'] = filter_text
        
    return _get_tbl(fm, 'result_tbl', cfg)


def _query_report(fm, report_name, filter_txt = '', match = {}):
    '''
    . to get result from a saved report
    . filter_txt: text do do filter with search box
    '''
    s = fm.selenium

    r_info = find_report(fm, report_name)
    if not r_info:
        raise Exception('Not found report %s' % report_name)

    s.click_and_wait(r_info['links']['query'])

#---------------------------------------------------------------------------------
if __name__ == '__main__':
    #from ratenv import *
    from pprint import pprint
    from RuckusAutoTest.common.SeleniumControl import SeleniumManager
    from RuckusAutoTest.components.FlexMaster import FlexMaster

    sm = SeleniumManager()
    print "type of sm: ", type(sm)
    config = {
        'username': 'admin@ruckus.com',
        'password': 'admin'
    }

    fm = FlexMaster(sm, 'firefox', '192.168.0.124', config)
    fm.start()
    fm.login()

    fm.stop()
