import os, inspect, traceback, logging
import random, re, time, copy, datetime
from pprint import pformat

'''
. Putting these switches to global so that once init it can be refered anywhere

. By default, the log-to-output is enabled. So all the traces, debug messages
  don't log to the logging system. Testcase designers can have a clean
  logging logs while still can debug any arising issues.
. This also applies to log_trace() function.

. The log-to-logging is good for execution engineers in collecting debug logs
  which is helpful to testcase designers.
'''
global minilog_to_logging, minilog_to_output
try:
    minilog_to_output
except:
    minilog_to_logging = True
    minilog_to_output = True # disabled this on production testbed


def shift(msg, i = 3):
    '''
    Shift the given message to i chars.
    This helps the message printed out in clarity.
    '''
    txt = ' ' * i
    msg = txt + msg
    return msg.replace('\n', '\n%s' % txt)


def get_field_as_string(list, field):
    """
    For logging, debugging purposes
    Returning a comma-separated string of content from given field

    Ex:
      Call get_field_as_string(list, 'Serial Number') will return a string likes:
        123456, 233445, 2323323
    """
    new_list = []
    for item in list:
        new_list.append(item[field])

    # should have a sort here?
    return ', '.join(new_list)


def remove_blank_field_items(list, field):
    """
    Removing a new list with all the blank field items removed.
    The old list is left untouched.

    """
    given_list = copy.deepcopy(list)

    for i in reversed(range(len(given_list))):
        if given_list[i][field].strip() == '':
            given_list.remove(given_list[i])

    return given_list


'''
@TODO clean up those code after cross-checking nobody use them!
'''
def equals_operator(list, attr):
    """
    returning the random item of the list and a list of must found items

    Input:
    - list: a list of dictionary, each item is a dictionary representing a row of a table
            with table headers as keys.
    """
    op = 'equals to'
    idx = random.randint(0, len(list) - 1)
    match = []
    item = list[idx][attr]

    search_criteria = item
    logging.debug('Operator: "%s"; Item: "%s" and Search Criteria: "%s"' % (op, item, search_criteria))
    # for each item in the list
    #   if it match the selected attribute
    #   then add it to the list of match item.
    #   This will be used to validate the result of FM.
    for i in range(len(list)):
        if list[i][attr] == list[idx][attr]:
            match.append(list[i])

    logging.debug('Expected list (Serial# only): %s' % get_field_as_string(match, 'Serial Number'))
    return (list[idx][attr], match)


def contains_operator(list, attr):
    op = 'contains'
    idx = random.randint(0, len(list) - 1)
    match = []
    item = list[idx][attr].strip()

    # some characters from the begining of the string
    # this part can be enhanced
    search_criteria = item[:random.randint(1, len(item) - 1)]
    logging.debug('Operator: "%s"; Item: "%s" and Search Criteria: "%s"' % (op, item, search_criteria))

    for i in range(len(list)):
        if search_criteria in list[i][attr]:
            match.append(list[i])

    logging.debug('Expected list (Serial# only): %s' % get_field_as_string(match, 'Serial Number'))
    return (search_criteria, match)


def starts_with_operator(list, attr):
    op = 'starts with'
    idx = random.randint(0, len(list) - 1)
    match = []
    item = list[idx][attr].strip()

    # some characters from the begining of the string
    # this part can be enhanced
    search_criteria = item[:random.randint(1, len(item) - 1)]
    logging.debug('Operator: "%s"; Item: "%s" and Search Criteria: "%s"' % (op, item, search_criteria))

    for i in range(len(list)):
        if list[i][attr].startswith(search_criteria):
            match.append(list[i])

    logging.debug('Expected list (Serial# only): %s' % get_field_as_string(match, 'Serial Number'))
    return (search_criteria, match)


def ends_with_operator(list, attr):
    op = '"ends with"'
    idx = random.randint(0, len(list) - 1)
    match = []
    item = list[idx][attr].strip()

    # some characters from the begining of the string
    # this part can be enhanced
    search_criteria = item[random.randint(1, len(item) - 1):]
    logging.debug('Operator: "%s"; Item: "%s" and Search Criteria: "%s"' % (op, item, search_criteria))

    for i in range(len(list)):
        if list[i][attr].endswith(search_criteria):
            match.append(list[i])

    logging.debug('Expected list (Serial# only): %s' % get_field_as_string(match, 'Serial Number'))
    return (search_criteria, match)


def compare(item1, item2, op = 'in'):
    '''
    input:
    - item1
    - item2
    - op: (optional) 're' or 'eq' or 'in'
            default: 'in'
    NOTE:
    - use 'sin' when both items are strings
    '''
    func = {
        're':  lambda x, y: re.search(x, y, re.I),
        'in':  lambda x, y: x.lower() in y.lower(),
        'eq':  lambda x, y: x.lower() == y.lower(),
        'sin': lambda x, y: x.strip().lower() in y.strip().lower(), # strip, lower
        'seq': lambda x, y: x.strip().lower() == y.strip().lower(), # strip, lower
        'xeq': lambda x, y: x == y, # exactly equal
        'equal': lambda x, y: x.lower() == y.lower(), # backward compatible
    }[op.lower()]

    return func(item1, item2)


def is_in(**kwa):
    '''
    - is the given item in the list?
    kwa:
    - item
    - list
    - op:  refer to compare()
    '''
    for i in kwa['list']:
        if compare(i, kwa['item'], kwa['op']):
            return True
    return False


def is_matched(**kwa):
    '''
    - is the given table row matched search criteria?
    kwa:
    - row:      a table row
    - criteria: likes {'Device Name': 'RuckusAP', 'Model': 'Zf2925'}
    - op:       refer to compare()
    return:
    - boolean
    '''
    for k in kwa['criteria'].iterkeys():
        if not compare(kwa['criteria'][k], kwa['row'][k], kwa['op']):
            return False
    return True


def get_timestamp():
    return datetime.datetime.now().strftime('%y%m%d.%H%M%S')


def get_unique_name(prefix):
    return '%s_%s' % (prefix.lower(), get_timestamp())


def find_key(**kwa):
    '''
    . Since, recently, the WebUI have changing in cases, likes:
        Last successful contact
        Last Successful Contact
      this function to help find out the real key
    NOTE: this function is obsoleted by ignore_case feature of ListTable
    kwa:
    - keys: a list of keys
    - match: the desired key
    '''
    return [x for x in kwa['keys'] if kwa['match'].strip().lower() == x.strip().lower()][0]


'''
For getting the current line and function name, just call:
   _line_() and _func_()
The i argument is just for log() function

'''
def _line_(i = 1):
    return int(inspect.stack()[i][2])


def _func_(i = 1):
    return inspect.stack()[i][3]


def fmt_log(message, level = 2):
    return '[%s, %s] %s' % (_func_(level), _line_(level), message)


def log(message, level = 3):
    '''
    TODO:
    . log the msgs based on features
    . func to turn on/off the logging system (on the fly): Using global vars
    '''
    msg = message #fmt_log(message, level)
    if minilog_to_logging:
        logging.debug(msg)
    if minilog_to_output:
        print msg


def log_cfg(cfg, name = 'cfg'):
    ''' for loggin' the data structure likes dict, list '''
    log('%s:\n%s\n' % (name, pformat(cfg)), level = 4)


def get_rat_real_path():
    return os.path.join(os.path.dirname(__file__)).split('\\rat')[0]


firmware_path = os.path.join(get_rat_real_path(), 'firmwares')


def init_path(path):
    '''
    create the path if it is not exist
    '''
    try:
        os.mkdir(path)
    except:
        pass
    return path


def init_firmware_path():
    return init_path(firmware_path)


def get_fws_on_local_file_system():
    '''
    Get all firmwares on local filesystem
    '''
    fws = []
    for path, dirs, files in os.walk(init_firmware_path()):
        if path == init_firmware_path():
            fws.extend([f for f in files if '.bl7' in f.lower()])
    return fws


def log_trace_back(log_fn = logging.debug, level = 5):
    ''' WARNING: OBSOLETED! use log_trace() instead '''
    msg = '\n%s\n%s\n%s' % ('-- Traceback ' + '-' * 70,
                            traceback.format_exc(),
                            '-- Traceback End ' + '-' * (70 - 4))
    if log_fn == log:
        return log_fn(msg, level)
    return log_fn(msg)


def log_trace():
    ''' log to output or logging according to the global vars '''
    if minilog_to_logging:
        log_trace_back()
    if minilog_to_output:
        log_trace_back(log_fn = log)


def compare_dict(dict_1, dict_2, tied_compare = True, op = 'in'):
    '''
    This function is to compare values of two dictionaries.
    Note: . Two dictionaries must have the same keys.
          . This function is now enhanced to support recursive comparision (dict of dict)
          . Currently, only support operator "in". So the function does compare
            "dict_1 in dict_2" only. Will enhance this func soon.
    Input:
    - dict_1, dict_2: a dictionary
    Output:
    - None/Error msg: None if no difference else error message
    '''
    msg = None
    for k in dict_1.iterkeys():
        if isinstance(dict_1[k], dict):
            return compare_dict(dict_1[k], dict_1[k], tied_compare)
        elif tied_compare:
            if str(dict_1[k]).lower() != str(dict_2[k]).lower():
                msg = 'Error: Item "%s" has difference (%s,%s)\n' % \
                      (k, dict_1[k], dict_2[k])
                break
        else:
            if not re.search(str(dict_1[k]), str(dict_2[k]), re.I) and \
               not re.search(dict_2[k], dict_1[k], re.I):
                msg = 'Error: Item "%s" has difference (%s,%s)\n' % \
                      (k, dict_1[k], dict_2[k])
                break

    return msg

def compare_dict_key_value(dict_1, dict_2, pass_items = [], is_verify_key = True):
    '''
    Compare two dicts, for the item in pass items, will not compare it.
    Compare keys and values of dict.
    Input:
       dict_1, dict_2: two dicts.
       pass_items: the item don't need to verify it's value.
       is_verify_key: if true, will verify dict keys; 
                      if false, don't verify dict keys. 
    Output: 
       Error dict.
       None if keys and values are same.
    '''
    err_dict = {}
    
    new_dict_1 = copy.deepcopy(dict_1)
    new_dict_2 = copy.deepcopy(dict_2)
    
    #Remove pass items from two dicts.
    for key in pass_items:
        if new_dict_1.has_key(key):
            new_dict_1.pop(key)
        if new_dict_2.has_key(key):
            new_dict_2.pop(key)
    
    result = True
    if is_verify_key:
        dict_1_keys = new_dict_1.keys()
        dict_2_keys = new_dict_2.keys()
        
        dict_1_keys.sort()
        dict_2_keys.sort()
        if dict_1_keys != dict_2_keys:
            err_dict['Keys'] = "Dict 1: %s, Dict 2: %s" % (dict_1_keys, dict_2_keys)
            result = False
    
    if result:
        for key, value_1 in new_dict_1.items():
            if new_dict_2.has_key(key):
                value_2 = new_dict_2[key]
                if type(value_1) == dict and type(value_2) == dict:
                    res = compare_dict_key_value(value_1, value_2, pass_items, is_verify_key)
                    if res:
                        err_dict[key] = res
                elif type(value_1) == list and type(value_2) == list:
                    value_1.sort()
                    value_2.sort()
                    if value_1 != value_2:
                        err_dict[key] = "Dict 1: %s, Dict 2: %s" % (value_1, value_2)
                else:
                    value_1 = str(value_1)
                    value_2 = str(value_2)
                    if value_1.lower() != value_2.lower():
                        err_dict[key] = "Dict 1:%s, Dict 2:%s" % (value_1, value_2)
            else:
                err_dict[key] = 'No value in dict_2'

    return err_dict

def update_dict(dest, src):
    '''
    TODO: in case, k not in dest, then add it in

    WARNING: just one level support, no recursive since there is no need now
    . since dict.update() treats child dicts as object, this function
      helps updating child dicts before updating the dict
    ex: updateChildDict(self.p, cfg)
    input:
    . dest, src are 2 dictionaries
    '''
    _src = copy.deepcopy(src)
    for k in _src.keys(): # can't use iterkeys() since key is deleted sometimes
        if isinstance(_src[k], dict) and k in dest:
            dest[k].update(_src[k])
            del _src[k]
    dest.update(_src)


def join_keys(dict1, dict2):
    '''
    returning joining of unique keys of 2 dictionaries
    '''
    ks = dict1.keys()
    return ks + [k for k in dict2.keys() if k not in ks]


def dict_by_keys(d, ks):
    '''
    Getting a dict from a dict with given keys

    Helper function for getting values from default config
    instead of the following code:
        default_cfg = dict([(k, self.dv.device_cfg.access_mgmt[k])
                               for k in self.p['mgmt_ks']])
    '''
    return dict([(k, d[k]) for k in ks])


def to_str_dict_items(d):
    '''
    converting all the number item to str for comparing with what get from webUI
    NOTE: recursive function
    '''
    for i in d.iterkeys():
        if isinstance(d[i], int) or isinstance(d[i], float):
            d[i] = str(d[i])
        if isinstance(d[i], dict):
            d[i] = to_str_dict_items(d[i])
    return d # for convenience


def try_interval(timeout = 180, interval = 2):
    '''
    Simplify the re-trying actions in a definite interval
    A try_times() should be developed accordingly
    '''
    t, end_time = time.time(), time.time() + timeout
    while t < end_time:
        yield t
        time.sleep(interval)
        t = time.time()


def try_times(times = 3, interval = 2):
    '''
    Simplify the re-trying actions in definite times
    '''
    for t in range(1, times + 1):
        yield t
        time.sleep(interval)


def wait_for(msg, wait = 60):
    logging.info('Wait (%s secs) for %s' % (wait, msg))
    time.sleep(wait)


def download_file(file_name):
    '''
    This function is to download file from FireFox browser to current user home
    directory.
    Note that: This function only works with FireFox
    '''
    # get user home directory
    from RuckusAutoTest.common.DialogHandler import BaseDialog, DialogManager

    file_path = os.path.join(os.path.expanduser('~'), r"Desktop\%s" % file_name)

    remove_file(file_path)
    # Prepare the dialog handlers which will proceed to download the file and save it to the Desktop
    dlg1 = BaseDialog(title = "Opening %s" % file_name, text = "", button_name = "",
                      key_string = "{PAUSE 1}%{s}{PAUSE 0.5}{ENTER}")
    dlg2 = BaseDialog(title = "Downloads", text = "", button_name = "", key_string = "%{F4}")
    dlg_mgr = DialogManager()

    dlg_mgr.add_dialog(dlg1)
    dlg_mgr.add_dialog(dlg2)

    dlg_mgr.start()

    # Wait until the file is saved
    for i in try_interval(15, 2):
        if os.path.isfile(file_path): break

    # Regardless what has happened, stop the dialog handlers
    dlg_mgr.shutdown()
    time.sleep(2)
    if os.path.isfile(file_path):
        return file_path

    raise Exception("Unable to download and save the file to [%s]" % file_path)


def remove_file(file_path):
    '''This function is to remove a file if it exist'''
    if os.path.isfile(file_path):
        os.remove(file_path)


def is_row_match(row, matches, op, is_delete = False):
    '''
    matches: a list of match items
    is_delete: delete this match item after found it so it don't match twice
    '''
    for m in matches:
        if is_matched(row = row, criteria = m, op = op):
            if is_delete:
                matches.remove(m)
            return True
    return False

def filter_dict_data(cfg = {}, keys = []):
    '''
    This function is to filter to get keys of cfg which they are in keys only.
    If keys is empty, get all.
    Input:
    - cfg: a dictionary to filter
    - keys: keys to get from cfg
    Output:
    - Return a filter data dictionary or exception if any key in keys but not
    in cfg
    '''
    filter_data = {}

    if keys:
        for k in keys: filter_data[k] = cfg[k]
    else:
        filter_data = copy.deepcopy(cfg)

    return filter_data

def compare_version(version1, version2, base_version_num = 2):
    '''
    compares the versions in the dotted numbers format (i.e. 1.2.3.4)
    returns:
        -1 (negative) if version1 < version2
        0 if equal
        1 (positive) if version1 > version2
        2 the base version like 9.7.0.0 don't match
    '''
    #@author: Jane.Guo @since: 2013-09 change function name from conpare_version to compare_version
    #Add a parameter to check the base version
    list1 = version1.split('.')
    list2 = version2.split('.')

    end = len(list1) if len(list1) < len(list2) else len(list2)

    list1_basev = '.'.join(list1[0:base_version_num])
    list2_basev = '.'.join(list2[0:base_version_num])
    
    base_check = True
    if list1_basev <> list2_basev:
        base_check = False
    
    idx = 0
    while idx < end:
        if int(list1[idx]) == int(list2[idx]):
            idx += 1
        elif int(list1[idx]) < int(list2[idx]):
            return (-1,base_check)
        else:
            return (1,base_check)

    if len(list1) < len(list2):
        return (-1,base_check)
    elif len(list1) == len(list2):
        return (0,base_check)
    else:
        return (1,base_check)

def compare_version_list(version1, version_list, base_version_num =  2):
    """
      Add function to compare version with version list.
      If version is larger than any one of version list, the return is 1
      If version is equal with any one of version list, the return is 0
      If the base version doesn't match, the return is 2
      Else return -1
      @author: Jane.Guo 
      @since: 2013-09 
    """
    result_sum = 0
    for c_version in version_list:
        res, base_check = compare_version(version1,c_version,base_version_num)
        if (res == 1 and base_check) or res == 0 or (res == -1 and base_check):
            return res
                        
        if not base_check:
            result_sum = result_sum + res
        
    if result_sum == len(version_list):
        return 1
    else:
        return -1


def list_to_dict(list, key):
    '''
    . convert a list to a dict with given key
    NOTE: key must be unique
    '''
    return dict([(i[key], i) for i in list])


def get_cfg_items(cfg, items):
    '''
    . return a new dict with the selected keys from the config
    Example
    . get_cfg_items({1:2, 2:4, 3:6}, [2,3]) >>> {2:4, 3:6}
    '''
    return dict([(i, cfg[i]) for i in items])


def map_row(row, hdr_map):
    '''
    . for backward compatible, mapping the headers to old ones of each row
    NOTE
    . if there is name changing on headers, callers will raise exceptions
    '''
    return dict([(hdr_map[k], v) for k, v in row.iteritems() if k in hdr_map])


def map_rows(rows, hdr_map):
    '''
    input
    . rows: all the rows in a list needed to be mapped
    . hdr_map: is the table
    '''
    return [map_row(r, hdr_map) for r in rows]


def get_ip_address(ip_port):
    """
    . on FM WebUI, the IP Address field is formatted as IP:Port
      (likes 192.168.20.200:443)
    . this function will help strip out the port from IP part
    """
    return ip_port.split(':')[0].strip()

def kbps_to_mbps(v_str, to_mb = True):
    '''
    to convert from kbps to mbps or vice versa.

    . v_str: full string of unit: 1000kbps, 1mbps
    . to_mb: True: convert from kbps to mbps
             False: from mbps to kbps
    . return in string

    Note: . To make consistency, the result will be return in float for two cases
            need to convert and no need to convert.

    '''
    num = re.search('\d+', v_str).group(0)

    # no need to convert for 2 cases.
    if (to_mb and 'mb' in v_str.lower()) or \
        (not to_mb and 'kb' in v_str.lower()):
        return str(float(num)) + ('mbps' if to_mb else 'kbps')

    return str(round(float(num)/1000.0, 3)) + 'mbps' \
           if to_mb else \
           str(float(num)*1000.0) + 'kbps'
