import time
import logging
import string

from RuckusAutoTest.common.utils import (
        try_interval, try_times, is_matched, log, log_trace,
)
from selenium import selenium

'''
The below snippet is used for testing iter_table_rows():

from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components import FlexMaster as FM
sm = SeleniumManager()
fm = FM.FlexMaster(sm, 'firefox', '192.168.30.252',
                   dict(username='admin@luannt.com', password='123456'))
fm.start()
s = fm.selenium
for i in s.iter_table_rows("//table[@id='auditlogtableList']",
        ['type', 'sev', 'time', 'user', 'msg']):
    print i

for i in s.iter_table_rows("//table[@id='auditlogtableList']",
        ['type', 'sev', 'time', 'user', 'msg'], verbose=True):
    print i

for i in s.iter_table_rows("//table[@id='auditlogtableList']",
        ['atype', 'sev', 'time', 'user', 'msg'],
        matches=dict(atype='logged')):
    print i

for r, i, rtmpl in s.iter_table_rows("//table[@id='UserList']",
        ['name', 'lastlog', 'role', 'action'],
        matches=dict(action='delete'), is_advance=False, verbose=True):
    print r
    s.safe_click((rtmpl + "/td/a[.='Delete']") % i)
'''

DEFAULT_WAIT = 1.5 # secs
DEFAULT_TRY_WAIT = .5 # secs
TBL_HDR_CHANGING_TXTS = [' ', '-', '/']
TBL_HDR_REMOVING_TXTS = ['_id', 'col_dataIndex_c_', 'col_dataIndex_',]


class SeleniumClient(selenium):
    """
    This class is an extension of selenium, providing some safe/retrying methods.

    NOTE:
    All public methods of this class have an element present checking inside.
    Therefore, no need to check for that before calling these methods.
    """

    def __init__(self, host, port, browser_type, browser_url):
        # url/browser_type are redundant! but they are good for runtime references
        self.url = browser_url
        self.browser_type = browser_type

        bt = dict(
            ie = '*iehta',
            #firefox = '*chrome',
            # Change to use 'firefox' profile instead of '*chrome'
            # An Nguyen - an.nguyen@ruckuswireless.com - Nov 2010
            firefox = "*firefox"
        )[browser_type]

        selenium.__init__(self, host, port, bt, browser_url)

        self.BY_VALUE = 0
        self.BY_LABEL = 1
        self.BY_LABEL_REG = 2

        self.timeout = 17 # secs
        self.page_load_timeout = 30 # secs


    def get_timeout(self, timeout = None):
        if timeout is None:
            return self.timeout
        else:
            return timeout


    def set_timeout(self, timeout):
        self.timeout = timeout


    def get_page_load_timeout(self, timeout = None):
        if timeout is None:
            return self.page_load_timeout
        else:
            return timeout


    def set_page_load_timeout(self, timeout):
        self.page_load_timeout = timeout


    def is_element_present(self, locator, timeout = None):
        """
        Check whether an element is present or not. Retrying a couple of times before timeout.

        NOTE:
        In case, you use this function for bound checking, likes checking if reaching the end of a table,
        you should set the timeout as small as possible (likes 0.4)

        Input:
        - locator: element locator to be checked
        - timeout: the maximum time to find the locator (in secs)

        Output: Boolean
        """
        for z in try_interval(self.get_timeout(timeout), DEFAULT_TRY_WAIT):
            if selenium.is_element_present(self, locator):
                return True

        return False


    def check_element_present(self, locator, timeout = None):
        '''
        this function raise exception if element not found
        while is_element_present() returns boolean
        '''
        if not self.is_element_present(locator, self.get_timeout(timeout)):
            raise Exception('Element not found: "%s"' % locator)


    def is_alert_present(self, timeout = None):
        for z in try_interval(self.get_timeout(timeout), DEFAULT_TRY_WAIT):
            if selenium.is_alert_present(self):
                return True

        return False


    def is_element_displayed(self, locator, timeout = None):
        '''
        This function is to check whether an element is displayed or not
        '''
        self.check_element_present(locator, self.get_timeout(timeout))
        # Added step to verify if the element is visible or not.
        # @since: Nov 2011
        # @author: an.nguyen@ruckuswireless.com        
        self.check_element_visible(locator, self.get_timeout(timeout))
        
        not_display_dict = {'@style':['display: none'],
                            '@class':['not-implemented']}

        for k, v in not_display_dict.iteritems():
            try:
                attr = self.get_attribute(locator + k, self.get_timeout(timeout))
                for item in v:
                    if  item.lower() in attr.lower().strip():
                        return False
            except Exception:
                pass

        return True


    def is_element_disabled(self, locator, timeout = None,
                            disabled_xpath = "[contains(@class,'disabled')]"):
        '''
        This function is to check whether an element is disabled or not.
        A disabled element is normally grey-out and is not click-able.

        NOTES: duplicated with lib.zd.widgets_zd's is_enabled_to_click

        Below is the example.
        --  <span class="sb" id="new-gprint">Create New</span>
            -> The 'Create New' button is enabled (click-able)

        --  <span class="sb disabled" id="new-gprint">Create New</span>
            -> The 'Create New' is now disabled (unable to click)

        The above are controlled by CSS
        .sb {
            color: darkblue;
            cursor: pointer;
        }

        .disabled {
            color: #cccccc;
            cursor: default;
        }

        With the HTML above, we have:
            locator = "//span[@id='new-gprint']"
            disabled_xpath = [contains(@class,'disabled')]

        and then we can form an element to check:
            //span[@id='new-gprint'][contains(@class,'disabled')]"]
        by using:
            disabled_element = string.join([locator, disabled_xpath], '')
        '''

        disabled_element = string.join([locator, disabled_xpath], '')
        disabled_xpath2 = "[@disabled]"
        disabled_element2 = string.join([locator, disabled_xpath2], '')
        

        res1 = self.is_element_present(disabled_element, timeout)
        res2 = self.is_element_present(disabled_element2, timeout)
        
        return (res1 or res2)


    def wait_for_element_disappered(self, locator, timeout = None):
        '''
        NOTE: consider to raise exception here
        '''
        for z in try_interval(self.get_timeout(timeout), DEFAULT_WAIT):
            if not self.is_element_displayed(locator, .3):
                return True

        return False


    def _safe_type(self, locator, value, timeout = None):
        """
        Make sure that value is set to the locator
        Internal function, use type_text instead.

        Input:
        - locator: the textbox to type text to
        - value:   the text to set to locator
        - timeout: the maximum time to set the value to the locator
        """
        self.check_element_present(locator, self.get_timeout(timeout))
        # Added step to verify if the element is visible or not.
        # @since: Nov 2011
        # @author: an.nguyen@ruckuswireless.com        
        self.check_element_visible(locator, self.get_timeout(timeout))
        # NOTE: read/write on Textbox should be string type
        value = str(value)
        end_time = time.time() + self.get_timeout(timeout)

        while time.time() <= end_time:
            try:
                #print 'value="%s", get_value="%s"' % (value, self.get_value(locator))
                self.type(locator, value)

                time.sleep(0.25) # at least wait for 0.25 sec
                # NOTE:
                #   since selenium.get_value() will strip the result
                #   so the value must be stripped before comparing
                if self.get_value(locator).strip() == value.strip():
                    return True

            except: # Some unexpected error happens
                pass

            time.sleep(0.2)

        return False


    def type_text(self, locator, value, timeout = None):
        if not self._safe_type(locator, value, self.get_timeout(timeout)):
            raise Exception('Can not set value "%s" to the element "%s"' % (value, locator))


    def _safe_do(self, locator, func, errmsg, timeout = None):
        '''
        Try to do the action defined on 'func' in a definite interval.
        Raise an 'errmsg' exception if the action could not be done.
        '''
        self.check_element_present(locator, self.get_timeout(timeout))
        # Added step to verify if the element is visible or not.
        # @since: Nov 2011
        # @author: an.nguyen@ruckuswireless.com
        #delete the check by west.li at 2012.01.06,
        #because in some case,after the input,the element will become unvisible,
        #and this check make the input failed 
        #self.check_element_visible(locator, self.get_timeout(timeout))
        for z in try_interval(self.get_timeout(timeout), DEFAULT_TRY_WAIT):
            try:
                return func(locator)
            except:
                pass

        raise Exception(errmsg % (self.get_timeout(timeout), locator))


    def get_text(self, locator, timeout = None, check_empty = False):
        '''
        TODO: do an analysis on the src, this can be set to True by default
              for all goods.
              one exception case found so far is the table getting funcs which
              can be fix easily
        - check_empty: if true, do check to make sure returned string is not empty,
                       and re-try in the timeout if the returned string is empty
        Get the text of an html tag.
        For getting value from input tags, refer to get_value()
        '''
        errmsg = 'Timed-out (%s secs) occurs while trying to get text from locator "%s"'
        text = self._safe_do(locator, self._get_text, errmsg, self.get_timeout(timeout))

        if check_empty:
            # re-try if the retruned string is empty
            end_time = time.time() + self.get_timeout(timeout)
            while not text and time.time() < end_time:
                text = self._safe_do(locator, self._get_text, errmsg, 2)

        return text


    def _get_text(self, locator):
        return selenium.get_text(self, locator)


    def get_value(self, locator, timeout = None):
        '''
        Get the value of an input field
        '''
        errmsg = 'Timed-out (%s secs) occurs while trying to get value from locator "%s"'
        return self._safe_do(locator, self._get_value, errmsg, self.get_timeout(timeout))


    def _get_value(self, locator):
        return selenium.get_value(self, locator)


    def get_attribute(self, locator, timeout = None):
        '''
        get the attribute
        return the attribute or raise an exception (if the attribute is not exist)

        NOTE:
        this function is not checking for element present since the locator containing
        the @attribute.

        WARNING:
        Wrapping this function in a try... except is recommended.
        Sometime an Firebug visible attribute can not be get. This is due to the attribute
        may be deleted by scripts while Firebug keep the old info.

        WARNING: Obsoleted! using get_attr() instead
        '''
        errmsg = 'Timed-out (%s secs) occurs while trying to get an attribute "%s"'
        func = selenium.get_attribute

        # the below code is copied from self._safe_do()
        # because the locator contains @attribute
        for z in try_interval(self.get_timeout(timeout), DEFAULT_TRY_WAIT):
            try:
                return func(self, locator)
            except:
                pass

        raise Exception(errmsg % (self.get_timeout(timeout), locator))


    def get_attr(self, locator, attribute, timeout = None):
        '''
        this function provides check element present and concanate
        locator and attribute so no preprocessing is needed
        '''
        self.check_element_present(locator, self.get_timeout(timeout))
        return self.get_attribute('%s@%s' % (locator, attribute), self.get_timeout(timeout))


    def get_selected_option(self, locator, timeout = None):
        """
        Get the selected label of a combo box
        """
        errmsg = 'Timed-out (%s secs) occurs while trying to get value from locator "%s"'
        return self._safe_do(locator, self.get_selected_label, errmsg,
                             self.get_timeout(timeout))


    def get_selected_value(self, locator, timeout = None):
        """
        Get the selected value of a combo box
        """
        errmsg = 'Timed-out (%s secs) occurs while trying to get value from locator "%s"'
        return self._safe_do(locator, self._get_selected_value, errmsg,
                             self.get_timeout(timeout))


    def _get_selected_value(self, locator):
        return selenium.get_selected_value(self, locator)


    def get_all_options(self, locator, timeout = None):
        """
        Get all labels of a combo box
        """
        errmsg = 'Timed-out (%s secs) occurs while trying to get all options from locator "%s"'
        return self._safe_do(locator, self.get_select_options, errmsg,
                             self.get_timeout(timeout))


    def get_xpath_count(self, locator, timeout = None):
        errmsg = 'Timed-out (%s secs) occurs while trying to get xpath count from locator "%s"'
        count = int(self._safe_do(locator, self._get_xpath_count, errmsg,
                                 self.get_timeout(timeout)))
        # if count = 0, retry with get_xpaht_count_2
        return count if count > 0 else self.get_xpath_count_2(locator)

    def get_xpath_count_2(self, locator):
        '''
        Another way to get x-path count. Get by check element present.
        '''
        l, i = locator + '[%s]', 1
        while self.is_element_present(l % i, 0.2): i +=1

        return i-1


    def _get_xpath_count(self, locator):
        return selenium.get_xpath_count(self, locator)


    def safe_click(self, locator, timeout = None):
        errmsg = 'Timed-out (%s secs) occurs while trying to click on "%s"'
        return self._safe_do(locator, self.click, errmsg,
                             self.get_timeout(timeout))


    def wait_for_pop_up(self, window_id, timeout = None):
        return selenium.wait_for_pop_up(self, window_id,
                                        self.get_timeout(timeout))


    def drag_and_drop(self, object, dest, wait = DEFAULT_WAIT, timeout = None):
        '''
        Drag and drop and object to destinated object
        Wait some secs for the page to be stabled
        '''
        errmsg = '%s %s %s'
        self.check_element_present(object)
        # Added step to verify if the element is visible or not.
        # @since: Nov 2011
        # @author: an.nguyen@ruckuswireless.com        
        self.check_element_visible(object, self.get_timeout(timeout))
        
        self.check_element_present(dest)

        for z in try_interval(self.get_timeout(timeout), DEFAULT_TRY_WAIT):
            try:
                self.drag_and_drop_to_object(object, dest)
                time.sleep(DEFAULT_WAIT)
                return

            except:
                pass

        raise Exception(errmsg % (self.get_timeout(timeout), object, dest))


    def key_up(self, locator, value, timeout = None):
        self.check_element_present(locator)

        for z in try_interval(self.get_timeout(timeout), 0.2):
            try:
                #print 'value="%s", get_value="%s"' % (value, self.get_value(locator))
                selenium.key_up(self, locator, value)

                time.sleep(0.25) # at least wait for 0.25 sec
                # NOTE:
                #   since selenium.get_value() will strip the result
                #   so the value must be stripped before comparing
                #if self.get_value(locator).strip() == value.strip():
                return True
            except:
                pass

        return False


    def click_and_wait(self, locator, wait = DEFAULT_WAIT, timeout = None):
        '''
        Click on a button/refresh button and wait for some secs before returning
        This function is helpful in case clicking on Refresh, Submit buttons...
        '''
        self.safe_click(locator, self.get_timeout(timeout))
        time.sleep(wait)


    def is_checked(self, locator, timeout = None):
        """
        Gets whether a toggle-button (checkbox/radio) is checked.  Fails if the specified element doesn't exist or isn't a toggle-button.

        'locator' is an element locator pointing to a checkbox or radio button
        """
        errmsg = 'Timed-out (%s secs) occurs while trying to get checked status of "%s"'
        return self._safe_do(locator, self._is_checked, errmsg,
                             self.get_timeout(timeout))

    def get_radio_group_value(self, loc_dict, timeout = None):
        '''
        to get value from group of radios.
        . loc_dict:
            Ex: dict(
                v1 = loc1,
                v2 = loc2,
                ....
            )
        return
            return the key according to its locator
            none if
        '''
        for k, l in loc_dict.iteritems():
            if self.is_checked(l):
                return k

        raise Exception("Cannot get value of any radio")

    def _is_checked(self, locator):
        return selenium.is_checked(self, locator)


    def click_if_not_checked(self, locator, timeout = None):
        """
        only click if the item is not checked. This is usually used for check box items
        """
        if not self.is_checked(locator, self.get_timeout(timeout)):
            self.safe_click(locator, self.get_timeout(timeout))


    def click_if_checked(self, locator, timeout = None):
        """
        only click if the item is checked to uncheck. This is usually used for check box items
        """
        if self.is_checked(locator, self.get_timeout(timeout)):
            self.safe_click(locator, self.get_timeout(timeout))


    def _safe_select(self, locator, value, get_by = 0, timeout = None):
        """
        Try to select an option from a combo box
        0: get by value
        1: get by label
        2: get by label regular expression
        """
        self.check_element_present(locator)
        # Added step to verify if the element is visible or not.
        # @since: Nov 2011
        # @author: an.nguyen@ruckuswireless.com        
        self.check_element_visible(locator, self.get_timeout(timeout))
        

        #log(value)
        #log(str(value))
        value = str(value)
        for z in try_interval(self.get_timeout(timeout), 0.5):
            try:
                map_key = {
                    self.BY_LABEL_REG: ["label=regexp:^.*" + value + ".*$", self.get_selected_label],
                    self.BY_LABEL: ["label=" + value, self.get_selected_label],
                    self.BY_VALUE: ["value=%s" % value, self.get_selected_value]
                }
                self.select(locator, map_key[get_by][0])
                time.sleep(0.25)
                # selecting by RE, we don't know how to compare the result, ignore it
                #log("Got value: %s" % map_key[get_by][1](locator))
                v = map_key[get_by][1](locator)
                #if get_by == self.BY_VALUE:
                #    v = v[0]
                if get_by == self.BY_LABEL_REG or v.strip() == value.strip():
                    return True
            except:
                pass

        return False


    def select_value(self, locator, value, timeout = None):
        """
        Select an option from a drop-down using an option locator.
        """
        if not self._safe_select(locator, value, self.BY_VALUE, self.get_timeout(timeout)):
            raise Exception('Cannot select the value "%s" from the element "%s"' % (value, locator))


    def select_option(self, locator, option, timeout = None, sel_by_reg = True):
        """
        Select an option from a drop-down using an option locator.
        Note: This function doesn't work with label having special characters like "2.4GHZ 54Mbps(802.11g only)".
        """
        get_by = self.BY_LABEL_REG if sel_by_reg else self.BY_LABEL
        if not self._safe_select(locator, option, get_by, self.get_timeout(timeout)):
            raise Exception('Cannot select the option "%s" from the element "%s"' % (option, locator))


    def get_htable_content(self, locator, row_locator = '/tbody/tr',
                           split_by = ':', ignore_case = False):
        """
        WARNING: OBSOLETE! Please use get_htable_rows2

        WARNING: This function returns wrong table in case the meta data is not unique.
        Please use iter_htable_rows() instead.

        This function gets contents of a horizontal-style table, returning as a hash.
        This fn will ignore all the <td colspan='2'>

        Horizonal-style tables appear on AP WebUI and FM WebUI. Below is an example
        which is got from FM Device View > Summary page:
            Model Type:     ZF7942
            Customer ID:    4bss
            Device Name:    RuckusAP
            MAC Address:    00:1D:2E:00:0D:B0
            ...

        Input:
        - locator: xpath for locating a table
        Output:
        - A hash containing row contents

        Ex:
        The below is the result from splitting the content get from get_htable_content example
            {u'Device Name': u'RuckusAP',
             u'MAC Address': u'00:1D:2E:00:0D:B0',
             ...
             u'Ruckus ZoneDirector IP Address': u'192.168.0.100'}
        """
        tbl = {}
        for k, v in self.iter_htable_rows(locator, row_locator, split_by, ignore_case):
            tbl[k] = v

        return tbl


    def get_htable_rows(self, locator, title, no_rows, row_locator = '/tbody/tr',
                        split_by = ':', ignore_case = False):
        """
        WARNING: OBSOLETE! Please use get_htable_rows2

        This function gets contents of a "no_rows" of FIRST rows from a row has the "title".
        It returns a hash with a title as key and value as its content.
        This fn will ignore all the <td colspan='2'>

        Horizonal-style tables appear on AP WebUI and FM WebUI. Below is an example
        which is got from FM Device View > Summary page:
            Telnet access: Disabled
                     Port:  23
               SSH access: Enabled
                     Port:  22
            ...

        Input:
        - locator: xpath for locating a table
        - row_title: title of a beginning row
        - num: number of rows to get their content

        Output:
        - A hash table contains row contents

        Note: The result table may be in following special cases:
            1. It is empty if the function doesn't find any row with "title"
            2. It doesn't have enough expected rows if no_rows from the row with "title"
            exceeds the last row of table
        Ex:
        Call get_htable_rows(locator, "Telnet access", 2)
        Will return a hash like below:
            {u'Telnet access': u'Disabled',
            u'Port': u'23'}

        """

        found = False
        count = 0
        rows = {}

        for t, v in self.iter_htable_rows(locator, ignore_case = ignore_case):
            if not found and title.upper() == t.upper():
                found = True

            if found:
                rows[t] = v
                count += 1
                # the last expected row
                if count >= no_rows:
                    break

        return rows


    def iter_htable_rows(self, locator, row_locator = '/tbody/tr',
                         split_by = ':', ignore_case = False):
        """
        WARNING: OBSOLETE! Please use get_htable_rows2

        Returning each row as a tuple of (meta-data, data)
        Please read the comments on get_htable_content() for details
        """
        # Some time the page loaded very slow so temporarily increase this timeout
        self.check_element_present(locator, 20)

        row_tmpl = locator + row_locator + '[%s]'
        i = 1
        while True:
            row_loc = row_tmpl % i
            #print row_loc # 4 debugging

            # now read the content of each row
            if self.is_element_present(row_loc, 0.5): # optimized for bound checking
                row_txt = self.get_text(row_loc)
                row_content = row_txt.split(split_by, 1)

                # sometime we will meet
                #   <td colspan="2"> </td>
                # so ignore that case
                if len(row_content) >= 2:
                    if ignore_case:
                        yield row_content[0].strip().lower().replace(' ', ''), row_content[1].strip()
                    else:
                        yield row_content[0].strip(), row_content[1].strip()
            else:
                break

            i += 1


    def get_htable_value(self, locator, title, ignore_case = False):
        """
        WARNING: OBSOLETE! Please use get_htable_rows2

        Iterate through the HTable until the given title is found.
        Returning the value of that title or None (if it's not available)
        """
        value = None

        for k, v in self.iter_htable_rows(locator, ignore_case = ignore_case):
            if k.upper() == title.upper():
                value = v
                break

        return value


    def _get_vtable_header(self, locator, header_locator = '/thead/tr/th'):
        """
        WARNING: OBSOLETED! iter_table_rows() provides simpler interface

        Returning a list of header based on its index
        An example of vertical style table is the inventory table on FM > Inventory.

        NOTE:
        No need to check for element present here because this function is an internal function,
        called by iter_vtable_rows() and the checking is already in iter_vtable_rows().

        Input:
        - locator: table locator
        """
        # NOTE: Quick fix for different kinds of header_locator
        if not self.is_element_present(locator + header_locator, .4):
            header_locator = '/thead/tr/td'

        header_loc_tmpl = locator + header_locator + '[%s]'
        headers = []
        i = 1

        while True:
            header_loc = header_loc_tmpl % i

            if self.is_element_present(header_loc, 0.5):
                headers.append(self.get_text(header_loc).strip())
            else:
                break

            i += 1

        return headers


    def iter_vtable_rows(self, locator, check_blank = True, verbose = False,
                         compare_method = None, ignore_case = False):
        """
        WARNING: OBSOLETED! iter_table_rows() provides simpler interface

        Iterate all the rows of a VTable
        This help us get as much row data as needed while maintaining the simple
        calling structure.

        The calling code can be written in a simple manner, such as:
            for r in iter_vtable_rows('/...', True):
                print r
            -- or --
            for r, i, r_tmpl in iter_vtable_rows('/...', verbose=True):
                print r, i, r_tmpl
        """
        self.check_element_present(locator)
        
        row_locator = '/tbody/tr' # will change to a parameter when needed
        row_tmpl = locator + row_locator + '[%s]'
        cell_tmpl = row_tmpl + '/td[%s]'

        th = self._get_vtable_header(locator)
        if ignore_case:
            th = [h.lower().replace(' ', '') for h in th]

        # try a couple of times, in case, the first row is blank
        # this can be moved to parameter list later
        tries = 5
        isAdvance = True # advance to the next item or not?
        isReturn = True # return the row to iteratee?

        r = 1 # row index
        while True:
            c = 1 # cell index
            row = {}

            # forming a row by reading all cells
            while True:
                cell = cell_tmpl % (r, c)
                if self.is_element_present(cell, .5) and \
                   len(th) >= c:
                    row[th[c - 1]] = self.get_text(cell).strip()
                else:
                    break
                c += 1

            # this is the last row, stop it
            if check_blank and self.is_blank_row(row):
                # NOTE:
                #   should get 1st row a couple of times, in case, it is blank
                #   because the table is not finishing initialization
                if r == 1:
                    time.sleep(0.1)
                    tries -= 1
                    if tries <= 0:
                        break
                    continue # retry here
                else:
                    break

            if compare_method != None:
                (isAdvance, isReturn) = compare_method(row)

            if isReturn:
                if verbose:
                    # row, row index, row template are returned as a tuple
                    yield row, r, row_tmpl
                else:
                    yield row

            if isAdvance: r += 1
        # nothing to return here!


    def get_vtable(self, locator, check_blank = True,
                   compare_method = None, ignore_case = True):
        '''
        WARNING: OBSOLETED! iter_table_rows() provides simpler interface

        . return VTable as a list of rows
        '''
        return [r for r in self.iter_vtable_rows(locator, check_blank, False,
                                                 compare_method, ignore_case)]


    def _get_row(self, hdrs, cell_tmpl):
        '''
        UPDATE:
        . ignore header with title is blank (refer to get_tbl_hdrs_by_attr)

        helper function of iter_vtable_rows2
        '''
        return dict(
            [(hdrs[i], self.get_text(cell_tmpl % (i + 1)).strip())
              for i in range(len(hdrs))
              if hdrs[i]
            ]
        )


    def iter_table_rows(self, loc, hdrs, match = {}, op = 'in',
                        is_advance = True, fns = []):
        '''
        Iterate all the rows of a Table. Refer to iterTableRow() for more
        How? by using get_xpath_count and given headers to get row by row
        . faster: since the number of rows/columns are predefined
        . independent with table headers: less rework
        . headers must be updated if table columns change

        . removing 2 unused options: check_blank=True, case_sens=False
        input:
        . match, op, is_advance come together
        '''
        self.check_element_present(loc)
        
        row_loc = loc + '/tbody/tr'
        row_tmpl = row_loc + '[%s]'

        # skip if there is no row in the tbody table
        count = 2
        for i in range(count):
            if not self.is_element_present(row_loc, 0.2):
#                print "row_loc %s not present" % row_loc
                time.sleep(1)
            else:
                break
            if i == count-1:
                return 

        r = 1
        while r <= self.get_xpath_count(row_loc):
            cell_tmpl = row_tmpl % r + '/td[%s]'
            row = self._get_row(hdrs, cell_tmpl)

            if self.is_blank_row(row):
                if r > 1:
                    return
                # is this the first row and it is blank? retry some times
                # after trying, if it is still blank then exit
                log('First row is blank, try to get again...')
                for i in try_times(5, 2):
                    row = self._get_row(hdrs, cell_tmpl)
                    if not self.is_blank_row(row):
                        break
                if self.is_blank_row(row):
                    return
            # if not matches to the spec, move to next row
            if match and not is_matched(row = row, criteria = match, op = op):
                r += 1
                continue

            res = dict(row = row, idx = r, tmpl = row_tmpl)
            for fn in fns: # post-processing
                fn(self, res)
            yield res
            if is_advance:
                r += 1


    def _get_htable_row(self, loc, hdrs, idx):
        '''
        WARNING: use this on 2 columns table only but can be extended
        '''
        row = loc + '/tbody/tr[%s]' % (idx + 1)
        self.check_element_present(row, .5)

        cell = row + '/td[2]' # 2 cases: (td[1] td[2]), (th[1] td[1])
        if not self.is_element_present(cell, .5):
            cell = row + '/td[1]'

        return self.get_text(cell)


    '''
    def getHTableRow(self, loc, hdrs, idx, as_value=True):
        self.check_element_present(loc)
        v = self._get_htable_row(loc, hdrs, idx)
        if as_value:
            return v
        return {hdrs[idx]: v}
    '''

    def get_htable_rows2(self, loc, hdrs, ks):
        '''
        get HTable on selected ks, if ks = hdrs then get all the table

        Advantages:
        . faster: since the number of rows is predefined (by hdrs)
                  accessing the row instantly
        . independent with table headers: less rework, no mapping required
        . headers must be updated if changes
        Example:
        . From FM Device View > Summary page:
            Model Type:     ZF7942
            Customer ID:    4bss
            Device Name:    RuckusAP
            MAC Address:    00:1D:2E:00:0D:B0

        . hdrs = [model, cus_id, name, mac]
        if you want to get 'name':
          se.getHTableRow(tbl_loc, hdrs, hdrs.index('name'))
        '''
        if not hdrs:
            raise Exception('No headers given')

        self.check_element_present(loc)
        
        return dict(
            [(hdrs[i], self._get_htable_row(loc, hdrs, i))
                for i in range(len(hdrs))
                if hdrs[i] in ks]
        )
 
    def get_htable_rows3(self, loc, hdrs):
        '''
        WARNING: use this on 2 columns table only but can be extended
        Use the id of location instead of index 
        '''
        info = []
        for hdid in hdrs:
            row = loc + '/tbody/tr/td[@id="%s"]/..' % hdid
            if self.is_element_present(row, .5) and self.is_visible(row):
                if self.is_element_present(row + '/th', .5):
                    info.append((self._get_text(row + '/th'), self._get_text(row + '/td')))
                else:
                    info.append((self._get_text(row + '/td[1]'), self._get_text(row + '/td[2]')))

        return dict(info)

    def wait_for_page_to_load(self, timeout = None):
        try:
            selenium.wait_for_page_to_load(
                self, self.get_page_load_timeout(timeout) * 1000
            )
        except:
            self.refresh()

    def is_blank_row(self, row):
        '''
        On the FM WebUI, there is a lot of table with blank rows. For ex: panes on Dashboard
        This function returns True in case all the cell contents are blanks.

        Input:
        - row: a dictionary

        Output:
        - Boolean: True if all the cells are blanks. Otherwise, False.
        '''
        for v in row.itervalues():
            if v != '':
                return False

        return True


    def is_confirmation_present(self, timeout = None):
        for z in try_interval(self.get_timeout(timeout), DEFAULT_TRY_WAIT):
            if selenium.is_confirmation_present(self):
                return True

        return False


    def close_confirmation_dlg(self, timeout = 10):
        '''
        This function is to close confirmation "Ok, Cancel" dialog
        '''
        if self.is_confirmation_present(timeout):
            logging.info('Got a pop up window "%s"' % self.get_confirmation())


    def get_alert(self, cancel_button = None):
        '''
        '''
        msg_alert = None

        if (self.is_alert_present(5)):
            msg_alert = selenium.get_alert(self)

            if cancel_button:
                self.click_and_wait(cancel_button)
                raise Exception("[ALERT] %s" % msg_alert)

        return msg_alert


    def _convert_hdr_key_to_internal(self, key):
        for i in TBL_HDR_CHANGING_TXTS:
            key = key.replace(i, '_')
        for i in TBL_HDR_REMOVING_TXTS:
            key = key.replace(i, '')
        return key.lower().strip()


    def get_tbl_hdrs_by_attr(self, loc, attr='attr'):
        '''
        . get the list of table headers based on attribute or title
        HOW TO:
        . get the table header special identified-able attributes which
          are use as keys of returning dict of iter_table_rows()
        . if the attributes are not there then use the titles (texts)
        . converting those attributes to conforming with our naming convention
          . lower case
          . stripped
          . ' ', '-',.. are converted to '_' (refer to TBL_HDR_CHANGING_TXTS)
          . some other special texts (likes '_id', 'col_dataIndex_') which are
            meaningless are also removed (refer to TBL_HDR_REMOVING_TXTS list)
        input
        . loc: table locator
        . attr: interest attribute
        return
        . a list of headers
        '''
        hdr_loc = loc + '/thead/tr/th'
        hdr_tmpl = hdr_loc + '[%s]'
        hdrs = []

        for i in range(0, self.get_xpath_count(hdr_loc)):
            loc, txt = hdr_tmpl % (i + 1), ''
            # ignore if the column is invisible
            # if not self.is_element_displayed(loc, 0.2): continue
            try:
                txt = self.get_attr(loc, attr, .2)

            except: # fail to get the attr then use the name as id
                txt = self.get_text(loc)

            hdrs.append(self._convert_hdr_key_to_internal(txt))

        return hdrs
    
    def get_visible_tbl_hdrs_by_attr(self, loc, attr='attr'):
        hdr_loc = loc + '/thead/tr/th'
        hdr_tmpl = hdr_loc + '[%s]'
        hdrs = []
        for i in range(0, self.get_xpath_count(hdr_loc)):
            loc, txt = hdr_tmpl % (i + 1), ''
            #@author: Anzuo, @change: get title if visible for edit currently managed APs on "Monitor" page
            try:
                if self.is_element_displayed(loc, 0.2):
                    pass
            except:
                continue
            try:
                txt = self.get_attr(loc, attr, .2)

            except: # fail to get the attr then use the name as id
                txt = self.get_text(loc)

            hdrs.append(self._convert_hdr_key_to_internal(txt))

        return hdrs
    
    def iter_tbl_pages(self, loc):
        '''
        . go through the table pages one by one
        WARNING
        . unexpected side effect: once in the middle of table pages,
          a whole page refresh is needed in case we want to go back to
          the first page
        input
        . loc: usually the "//table[@id...]/tfoot"
        '''
        next_btn_loc = loc + "//img[contains(@src,'next.gif')]"
        p = 1
        yield p # first page

        if not loc:
            return

        p += 1
        while self.is_element_present(next_btn_loc, .5) and \
        self.is_visible(next_btn_loc) and \
        not self.is_element_disabled(next_btn_loc, .5):
            self.click_and_wait(next_btn_loc, 1)
            yield p
            p += 1
    
    #
    # To cover the bug 22712. 
    # Added functions to verify if the element is visiable or not. 
    # Added step to verify if the element is visible or not.
    # @since: Nov 2011
    # @author: an.nguyen@ruckuswireless.com        
    #
    
    def is_element_visible(self, locator, timeout = None):
        """
        Check whether an element is visible or not. Retrying a couple of times before timeout.

        NOTE:
        In case, you use this function for bound checking, likes checking if reaching the end of a table,
        you should set the timeout as small as possible (likes 0.4)

        Input:
        - locator: element locator to be checked
        - timeout: the maximum time to find the locator (in secs)

        Output: Boolean
        """
        for z in try_interval(self.get_timeout(timeout), DEFAULT_TRY_WAIT):
            if selenium.is_visible(self, locator):
                return True

        return False


    def check_element_visible(self, locator, timeout = None):
        '''
        this function raise exception if element is not visible 
        while is_element_present() returns boolean
        '''
        if not self.is_element_visible(locator, self.get_timeout(timeout)):
            raise Exception('Element is not visible: "%s"' % locator)
    
    def wait_for_element_present(self, locator, timeout = 60):
        """
        To cover the case that ajax is call during page load which can not hadled by selenium RC v.1
        """
#        logging.info('Waiting for element %s is presented' % locator)
        start_time = time.time()
        waiting_time = start_time - time.time()
        
        while waiting_time < timeout:
            if selenium.is_element_present(self, locator):
                return
            else:
                time.sleep(timeout/5)
            waiting_time = start_time - time.time()
        
        raise Exception('The element %s does not present after %s' %(locator, waiting_time))