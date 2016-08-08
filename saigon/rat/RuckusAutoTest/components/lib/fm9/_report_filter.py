from RuckusAutoTest.common import se_dojo_ui as dj

#-----------------------------------------------------------------------------
#  CONSTANTS FOR THIS LIB
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def fill_in(fm, rpt_opts=None, flt_opts=None):
    '''
    . rpt_opt: a list of elements
    +  Required elements if create report from Saved Report page.
        rpt_opts = [
            'Device View', # Report Category element
            'All ZoneDirectors', # Device View element
            'ZoneDirectors', # Report Type element
        ]
        OR
        rpt_opts = [
            'Association', # Report Category element
            'All ZoneDirectors', # Device View element
            'ZoneDirectors', # Report Type element
        ]
    +  Required elements if create report from pages of Report Categories.
        rpt_opts = [
            'All ZoneDirectors', # Device View element
            'ZoneDirectors', # Report Type element
        ]
        OR
        rpt_opts = [
            'All Standalone APs', # Device View element
            'Currently Connected', # Report Type element
        ]
    . a list of criteria, something likes
        flt_opts = [
            ['Device Name', 'Contains', 'al'],
            ['Serial Number', 'Starts with', '1008'],
            ['IP Address', 'Ends with', '140'],
        ]
    '''
    if rpt_opts:
        idx = _find_first_visible_report_option_index(fm)
        top_rpt = REPORT_TOP_TMPL
        for opt in rpt_opts:
            _fill_in_an_report_option(fm, top_rpt % idx, opt)
            idx +=1

    if flt_opts:
        top_flt = FILTER_TOP_TMPL
        for idx, opt in enumerate(flt_opts):
            _fill_in_an_filter_option(fm, top_flt % (idx+1), opt)
            if (idx+1) < len(flt_opts):
                fm.s.click_and_wait(top_flt % (idx+1) + filter_tmpl['add_cond_btn'], 1)

    #fm.s.click_and_wait(filter_tmpl['query_btn'], 2)


#-----------------------------------------------------------------------------
#  PRIVATE METHODS
#-----------------------------------------------------------------------------
REPORT_TOP_TMPL = "//div[@class='RuckusReportOptionRow'][%s]"
FILTER_TOP_TMPL = "//tr[contains(@class, 'RuckusFilterRow')][%s]"


filter_tmpl = dict(
    attr = "/td[2]/span",
    op = "/td[3]/span",
    value_txt = "/td[4]/input[@type='text']",
    value_cb = "/td[4]//span[contains(@class,'dojoComboBoxOuter')]",
    value_date = "/td[4]/span[2]/span[2]//input[@type='text']",
    value_time = "/td[4]/span[2]/span[4]//input[@type='text']",

    value_time_txt = "//input[@dojoattachpoint='upTimeTextField']",
    # value_time_txt = "/td[4]/div/input[@type='text']",
    value_time_unit = "//span[@dojoattachpoint='upTimeField']/span",

    add_cond_btn = "//img[@dojoattachpoint='addImg']",
    query_btn = "//input[@dojoattachpoint='queryButton']",
    # for Configuration Upgrade > Created
    select_date="//span[@dojoattachpoint='dateAndTimeField']/span[2]//input[2]",
    select_time="//span[@dojoattachpoint='dateAndTimeField']/span[4]//input[2]",
)


report_tmpl = dict(
    option_cb = "//span[contains(@class,'dojoComboBoxOuter')]",
)


def _find_first_visible_report_option_index(fm):
    '''
    To identify the first visible report element.
    . Page of Save Reports has the first report option (span element) with index=1
    . Pages Device View, Active Firmware, ... of Report Categories has the first
      report option (span element) with index=2
    '''
    s, rpt_loc, idx = fm.selenium, REPORT_TOP_TMPL, 1
    while not s.is_element_displayed(rpt_loc % idx, 1.5): idx +=1
    return idx


def _fill_in_an_report_option(fm, top, option):
    '''
    constraints on input
    . option: Report option name
    . Eg: All ZoneDirectors, Connected ZoneDirectors, ..
    '''
    dj.select_cb_option(fm.s, top + report_tmpl['option_cb'], option)


def _fill_in_an_filter_option(fm, top, option):
    '''
    constraints on input
    . last seen > value_date, value_time
    . uptime > value_txt, value_cb
    . connection, model > value_cb
    '''
    attr = option[0]
    dj.select_cb_option(fm.s, top + filter_tmpl['attr'], attr)
    dj.select_cb_option(fm.s, top + filter_tmpl['op'], option[1])

    if attr in ['Last Seen']:
        dj.select_cb_option(fm.s, top + filter_tmpl['value_date'], option[2])
        dj.select_cb_option(fm.s, top + filter_tmpl['value_time'], option[3])
    elif attr in ['Uptime']:
        fm.s.type_text(top + filter_tmpl['value_time_txt'], option[2])
        dj.select_cb_option(fm.s, top + filter_tmpl['value_time_unit'],
                            option[3])
    elif attr in ['Connection', 'Model Name']:
        dj.select_cb_option(fm.s, top + filter_tmpl['value_cb'], option[2])
    elif attr in ['Device Last Seen', 'Created']:
        fm.s.type_text(top + filter_tmpl['select_date'], option[2])
        fm.s.type_text(top + filter_tmpl['select_time'], option[3])
    else:
        fm.s.type_text(top + filter_tmpl['value_txt'], option[2])


