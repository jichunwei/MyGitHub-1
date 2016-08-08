# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Common utility functions for developing test cases
   Every function here should be able to run on both windows and linux platform
"""

import random
import string
import sys
import time
import os
import glob
import ConfigParser
import socket
import copy
import re
import logging
import subprocess
import xlrd
import smtplib
import datetime


def exec_program(cmd_line):
    """
    copied from ratToolAgent
    """
    output = subprocess.Popen(cmd_line, stdout = subprocess.PIPE).communicate()[0]
    return output

def make_random_string(length, type = "ascii"):
    """ Generating either printable ASCII chars or Hex random string of given length.
    """

    # Using list comprehension and string.join() is the most efficient way to implement
    # string concanation (see http://www.skymind.com/~ocrow/python_string/)

    if type.lower() == "ascii":
        #  Characters decimal 32-126 are the printable ASCII code characters. chr(32) is space.
        return ''.join([chr(random.randint(33, 126)) for x in range(length)])
    elif type.lower() == 'alpha':
        # String with alpha chars only
        return ''.join([random.choice('abcdefghiklmnopqrstuvwxyzABCDEFGHIKLMNOPQRSTUVWXYZ') for x in range(length)])
    elif type.lower() == "hex": # Hex chars only
        return ''.join([random.choice('1234567890abcdef') for x in range(length)])
    elif type.lower() == "alnum": # Alphabetical and numeric characters
        char_set = 'abcdefghiklmnopqrstuvwxyzABCDEFGHIKLMNOPQRSTUVWXYZ0123456789'
        return ''.join([random.choice(char_set) for x in range(length)])
    else:
        return ''

def ping(target_ip, timeout_ms = 1000):
    """
    ping performs a basic connectivity test to the specified target
    Input:
    - target_ip: An IP address to ping to
    - tries: number of retry
    - timeout_ms: maximum time for a ping to be done
    Output:
    - "ok" if ping is done successfully
    - Or a message if ping fails
    """
    if sys.platform == "win32":
        # cmd = "ping %s -n 1 -w 1 > NUL" % (target_ip)
        return ping_win32(target_ip, timeout_ms)
    else:
        cmd = "ping %s -c 1 -W 1 > /dev/null" % (target_ip)

    timeout_s = timeout_ms / 1000.0
    start_time = time.time()
    current_time = start_time
    while current_time - start_time < timeout_s:
        err = os.system(cmd)
        current_time = time.time()
        if not err:
            return "%.1f" % (current_time - start_time)
        time.sleep(0.03)
    return "Timeout exceeded (%.1f seconds)" % timeout_s

def ping_win32(target_ip, timeout_ms = 1000, echo_count = 2, echo_timeout = 10, pause = 0.05):
    cmd_line = "ping %s -n %s -w %s" % (target_ip, str(echo_count), str(echo_timeout))
    ofmt = r"Packets:\s*sent\s*=\s*(\d+),\s*received\s*=\s*(\d+),\s+lost\s*=\s*(\d+)\s*\((\d+)%\s*loss\)"
    good_reply_list = [r"reply\s+from\s+[0-9.]+:\s*bytes=\d+.*TTL=\d+", 
                       r"reply\s+from\s+[0-9a-f:]+:\s*time[=,<]\d+ms"]
    
    timeout_s = timeout_ms / 1000.0
    start_time = time.time()
    current_time = start_time
    while current_time - start_time < timeout_s:
        data = exec_program(cmd_line)
        current_time = time.time()
        m = re.search(ofmt, data, re.M | re.I)
        if m and int(m.group(4)) == 0:
            for ptn in good_reply_list:
                if re.search(ptn, data, re.I):  
                    # bug in win32 ping program.
                    # if gateway exist in target_ip; the loss rate is ZERO %                  
                    return "%.1f" % (current_time - start_time)
                
        time.sleep(int(pause))
    return "Timeout exceeded (%.1f seconds)" % timeout_s

def get_indexed_item(text, index):
    """
    Quick and dirty way to get the text in column <index> in a line of text.
    """
    txt = text.split(' ')
    txt = remove_blanks_from_list(txt)
    if len(txt) > index:
        return txt[index]
    else:
        return ""

def get_random_int(min, max):
    """
    Returns random integer within a min/max range (min <= int < max).
    """
    return int(random.random() * (max - min + 1)) + min

def get_random_string(type, min_len, max_len = ""):
    """
    Returns random string of either printable ASCII chars or HEX of
    given length (min_len) or random length (min_len <= len < max_len).
    """
    if not max_len:
        length = min_len
    else:
        length = int(random.random() * (max_len - min_len + 1)) + min_len
    return (make_random_string(length, type))

def cfg_to_dict(cfg_file, d = ""):
    cp = ConfigParser.ConfigParser()
    cp.read(cfg_file)
    if not d:
        d = dict()
    for s in cp.sections():
        d[s] = dict()
        for i in cp.items(s):
            d[s][i[0]] = i[1]
    return d

def convert_cfg(cfg_dict):
    for sec in cfg_dict.keys():
        for i in cfg_dict[sec].keys():
            val = cfg_dict[sec][i].lower()
            if val in ['true', 'y', 'yes']:
                cfg_dict[sec][i] = True
            elif val in ['false', 'n', 'no']:
                cfg_dict[sec][i] = False
            if val.isdigit():
                cfg_dict[sec][i] = int(val)
            if val.find(';') != -1:
                valueList = val.split(';')
                valueListOfLists = list()
                for item in valueList:
                    subList = item.split(',')
                    if subList[0].isdigit():
                        intList = list()
                        # Make the list ints
                        for itm in subList:
                            intList.append(int(itm))
                        subList = intList
                    valueListOfLists.append(subList)
                cfg_dict[sec][i] = valueListOfLists
            elif val.find(',') != -1:
                newList = val.split(',')
                if newList[0].isdigit():
                    intList = list()
                    # Make the list ints
                    for itm in newList:
                        intList.append(int(itm))
                    newList = intList
                cfg_dict[sec][i] = newList

def get_test_cfg(cfg_file):
    d = dict()
    d = cfg_to_dict(cfg_file, d)
    convert_cfg(d)
    return d

def write_cfg_from_dict(cfg_dict, cfg_file):
    cp = ConfigParser.ConfigParser()
    for section_key in cfg_dict.keys():
        cp.add_section(section_key)
        for sub_key in cfg_dict[section_key].keys():
            val = cfg_dict[section_key][sub_key]
            if isinstance(val, list):
                val = string.join(val, ',')
            cp.set(section_key, sub_key, val)
    fp = open(cfg_file, 'w')
    cp.write(fp)
    fp.close()

def set_local_ip_to_dhcp(name = "V54Adapter"):
    """
    Windows function to set a network interface to use DHCP.
    """
    os.system("netsh interface ip set address \"%s\" dhcp" % name)

def make_list(the_list):
    if not isinstance(the_list, list):
        tmp = list()
        tmp.append(the_list)
        return tmp
    else:
        return the_list

def make_list_of_lists(the_list):
    if not isinstance(the_list, list):
        the_list = the_list.split()
    if isinstance(the_list[0], list):
        return the_list
    else:
        tmp = list()
        tmp.append(the_list)
        return tmp

def combine_lists(list1, list2):
    if not list2:
        if isinstance(list1, list):
            return list1
        else:
            tmp = list()
            if list1:
                tmp.append(list1)
            return tmp
    if not list1:
        if isinstance(list2, list):
            return list2
        else:
            tmp = list()
            if list2:
                tmp.append(list2)
            return tmp

    #list2_is_list_of_lists = 0 # Tu Bui: don't use this variable
    list2_is_empty = 0
    # Check to see whether the list is a list of lists or a string
    if isinstance(list2, list):
        combined_list = copy.copy(list2)
        if isinstance(list2[0], list):
            #listOfLists = 1 # Tu Bui: don't use this variable
            if len(list2[0]) == 0:
                list2_is_empty = 1
    else:
        combined_list = list()
        if not (list2_is_empty):
            combined_list.append(list2)
    # Check to see whether the list is a list or a string
    if not isinstance(list1, list):
        tmp = list()
        if list1:
            tmp.append(list1)
        list1 = tmp
    for item in list1:
        if not combined_list.__contains__(item):
            combined_list.append(item)
    return combined_list

def is_item_in_list(list_obj, item):
    if isinstance(list_obj, list) and len(list_obj):
        return int(list_obj.__contains__(item))
    elif list_obj == item:
        return 1
    return 0

def send_mail(mail_server_ip, to_addr_list, from_addr, subject, body, attachment_list = [], html_txt = ""):
    #from email import Message # Tu Bui: don't use this lib
    from email import MIMEText
    from email import MIMEBase
    from email import MIMEMultipart
    from email import Encoders
    if not isinstance(attachment_list, list):
        attachment_list = attachment_list.split()
    if isinstance(to_addr_list, list):
        toAddrStr = ", ".join(to_addr_list)
    else:
        toAddrStr = to_addr_list
    main_email_msg = MIMEMultipart.MIMEMultipart()

    # Check to see whether the MIME bug limit of ~60 characters will affect
    # the subject line and replace a space with a \n.  If it does, I add a \n
    # after a space so that it still displays correctly
    if len(subject) > 60:
        index = subject.find(" ", 50) + 1
        subject = subject[0:index] + "\n" + subject[index:]

    main_email_msg['subject'] = subject
    main_email_msg['To'] = toAddrStr
    main_email_msg['From'] = from_addr
    # Add the attachments
    for attachment in attachment_list:
        if glob.glob(attachment):
            fp = open(attachment, 'rb')
            msg = MIMEBase.MIMEBase('application', 'octet-stream')
            msg.set_payload(fp.read())
            Encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename = attachment.split('\\')[-1])
            fp.close()
            main_email_msg.attach(msg)
    # Fill in the body of the message
    if html_txt:
        msg = MIMEText.MIMEText(html_txt, 'html')
        main_email_msg.attach(msg)

    msg = MIMEText.MIMEText(body)
    main_email_msg.attach(msg)

    server = smtplib.SMTP(mail_server_ip)
    server.sendmail(from_addr, to_addr_list, main_email_msg.as_string())
    server.quit()

def get_filesize(filename):
    try:
        fp = open(filename, "r")
        fp.seek(0, 2)
        size = fp.tell()
        fp.close()
        return size
    except:
        return 0

def find_addr_on_same_net(ip_addr, ip_addr_list = ""):
    """
    Takes in an IP address to search for within a list of IP addresses.
    If the list of IP addresses isn't passed it, the function gets a
    list of all the local IP addresses.  The IP address from the list
    that is on the same network as the IP address passed in is returned.
    If no match is found, 0 is returned.
    """
    if ip_addr_list == "":
        ip_addr_list = get_local_address()
    oct_list = ip_addr.split('.')
    if oct_list[0] < 128:
        search_str = "%s." % oct_list[0]
    elif oct_list[0] < 192:
        search_str = "%s.%s." % (oct_list[0], oct_list[1])
    else:
        search_str = "%s.%s.%s." % (oct_list[0], oct_list[1], oct_list[2])

    for ip in ip_addr_list:
        if ip.find(search_str) == 0:
            return ip
    return 0

def get_local_address():
    """
    Returns a list of all the local IP addresses.
    """
    return(socket.gethostbyname_ex(socket.gethostname())[2])

def release_renew_ip_addr(ifName):
    """
    Windows function to release and renew the IP address on a network
    interface specified by ifName.
    """
    # find how many addresses are currently configured
    local_addr_list = get_local_address()
    pre_release_len = len(local_addr_list)

    os.system("ipconfig /release %s > NUL" % ifName)
    time.sleep(3)

    # find how many addresses are left after the release
    local_addr_list = get_local_address()
    post_release_len = len(local_addr_list)

    os.system("ipconfig /renew %s > NUL" % ifName)

    if post_release_len < pre_release_len:
        count = 0
        while count < 5:
            # find how many addresses there are now
            local_addr_list = get_local_address()
            post_release_len = len(local_addr_list)
            if len(local_addr_list) == pre_release_len:
                return
            else:
                count = count + 1
                if find_addr_on_same_net("169.0.0.0"):
                    release_renew_ip_addr(ifName)
                time.sleep(2)
    else:
        # We might not have had a configured address before, so that's why the
        # number of addresses didn't change.  Just wait for a while to see whether
        # we get an address this time
        count = 0
        while count < 5:
            # find how many addresses there are now
            local_addr_list = get_local_address()
            post_release_len = len(local_addr_list)
            if len(local_addr_list) > pre_release_len:
                return
            else:
                count = count + 1
                if find_addr_on_same_net("169.0.0.0"):
                    release_renew_ip_addr(ifName)
                time.sleep(4)

def set_local_static_ip(ip_addr, mask, gw, name = "V54Adapter"):
    """
    Windows function to set a network interface to a static IP.
    """
    os.system("netsh interface ip set address \"%s\" static %s %s %s 1" % (name, ip_addr, mask, gw))

def get_subnet_mask(ip_addr, use_short_form = True):
    """ Return the default subnet mask of a given IP address
    Input:
    - ip_addr: the subject address
    - use_short_form: if True, the mask is in format /N; otherwise it is /N.N.N.N
    Output: the subnet mask value
    """
    ip_addr_pattern = "([0-9]+)\.[0-9]+\.[0-9]+\.[0-9]+"
    match = re.match(ip_addr_pattern, ip_addr)
    if not match:
        raise Exception("Invalid IP address %s" % ip_addr)
    first_octet = int(match.group(1))
    if first_octet < 128:
        if use_short_form: return "8"
        else: return "255.0.0.0"
    elif first_octet < 192:
        if use_short_form: return "16"
        else: return "255.255.0.0"
    elif first_octet < 224:
        if use_short_form: return "24"
        else: return "255.255.255.0"
    else:
        raise Exception("The address is not configurable to hosts (%s)" % ip_addr)

def get_network_address(ip_addr, mask = ""):
    """ Return the default network address of a given IP address
    Input:
    @param ip_addr: the subject address
    @param mask: mask of the given address; if not given, default mask will be used
                 mask can also given as the bit length
    Output: the network address value
    """
    ip_addr_pattern = "([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)"
    ip_addr_obj = re.match(ip_addr_pattern, ip_addr)
    if not ip_addr_obj:
        raise Exception("Invalid IP address %s given" % ip_addr)
    ip_octets = [int(ip_addr_obj.group(i)) for i in [1, 2, 3, 4]]

    if not mask:
        mask = get_subnet_mask(ip_addr)
    mask_obj = re.match(ip_addr_pattern, mask)
    if not mask_obj:
        try:
            l = int(mask)
            mask_octets = [0] * 4
            for i in range(l / 8):
                mask_octets[i] = 255
            if i < 3 and l % 8:
                mask_octets[i + 1] = 2 ** (8 - l % 8)
        except ValueError:
            raise Exception("Invalid mask %s given" % mask)
    else:
        mask_octets = [int(mask_obj.group(i)) for i in [1, 2, 3, 4]]

    network_octets = [str(mask_octets[i] & ip_octets[i]) for i in range(4)]
    return ".".join(network_octets)

def get_network_address_ipv6(ip_addr, prefix_len = "64"):
    """ Return the default network address of a given IPV6 address
    Input:
    @param ip_addr: the subject address
    @param prefix_len: prefix length of ipv6 address.
    Output: the prefix length of number of ipv6 address.
    For example:
        ip_addr = 2020::1, prefix_len = 64, return 2020:0000:0000:0000 
    """
    ip_list = ip_addr.lower().split(':')
    
    zero_len = 8 - (len(ip_list) - 1)
    zero_list = ['0'.zfill(4)]*zero_len
        
    for i in range(0, len(ip_list)):
        if ip_list[i] == '':
            ip_list[i:i] = zero_list
        else:
            ip_list[i] = ip_list[i].zfill(4)
    
    addr_len = int(prefix_len)/4
    
    tar_list = []
    for val in ip_list:
        if addr_len > 4:
            tar_list.append(val)
            addr_len = addr_len - 4
        elif addr_len > 0:
            tar_list.append(val[:addr_len])
            addr_len = 0
        
    return ":".join(tar_list)

def is_ipv4_addr(ip_addr):
    ptn = '(\d{1,3}\.){3}\d{1,3}$'
    matcher = re.compile(ptn, re.I).match(ip_addr)
    if matcher:        
        return True
    else:
        return False

def is_ipv6_addr(ip_addr):
    ptn = '[0-9A-Fa-f]{0,4}:([0-9A-Fa-f]{0,4}:){0,6}[0-9A-Fa-f]{1,4}$'
    matcher = re.compile(ptn, re.I).match(ip_addr)
    if matcher:
        return True
    else:
        return False

def set_local_time(datetime):
    """
    Change time in the PC
    Input:
    - datetime: the target time that PC is changed.
      Its format can be seconds, "2008/05/03 03:32:03", or "Tuesday, May 20, 2008 08:22:12 PM"
    Output: none
    """
    try:
        seconds = time.mktime(time.strptime(datetime, "%Y/%m/%d %H:%M:%S"))
    except:
        try:
            seconds = time.mktime(time.strptime(datetime, "%A, %b %d, %Y %I:%M:%S %p"))
        except:
            seconds = datetime
    time_info = time.strftime("%m-%d-%y %H:%M:%S", time.localtime(seconds)).split()
    tries = 2
    while tries:
        change_date = os.system("date %s" % time_info[0])
        change_time = os.system("time %s" % time_info[1])
        if not change_date and not change_time:
            logging.info("PC Time: %s" % time_info)
            break
        else:
            tries = tries - 1
    if change_date and change_time:
        raise Exception("Can not set datetime for local PC")

def generate_wlan_parameter(basic_config):
    """
    """
    ssid = basic_config['ssid']
    auth = basic_config['auth']
    encryption = basic_config['encryption']

    if basic_config.has_key('wpa_ver'):
        wpa_ver = basic_config['wpa_ver']
    else:
        wpa_ver = ''

    if basic_config.has_key('key_index'):
        key_index = basic_config['key_index']
    else:
        key_index = ''

    if basic_config.has_key('key_string'):
        key_string = basic_config['key_string']
    else:
        key_string = ''

    if basic_config.has_key('username'):
        username = basic_config['username']
    else:
        username = 'testuser'

    if basic_config.has_key('password'):
        password = basic_config['password']
    else:
        password = 'testpass'

    if basic_config.has_key('ras_addr'):
        ras_addr = basic_config['ras_addr']
    else:
        ras_addr = ''

    if basic_config.has_key('ras_port'):
        ras_port = basic_config['ras_port']
    else:
        ras_port = ''

    if basic_config.has_key('ras_secret'):
        ras_secret = basic_config['ras_secret']
    else:
        ras_secret = ''

    if basic_config.has_key('use_radius'):
        use_radius = basic_config['use_radius']
    else:
        use_radius = ''

    return {'ssid':ssid, 'auth':auth, 'wpa_ver':wpa_ver,
            'encryption':encryption, 'sta_auth':auth,
            'sta_wpa_ver':wpa_ver, 'sta_encryption':encryption,
            'key_index':key_index , 'key_string':key_string,
            'username':username, 'password':password,
            'ras_addr':ras_addr, 'ras_port':ras_port,
            'ras_secret':ras_secret, 'use_radius':use_radius}

def lookup_domain_name(name, server = ""):
    if name[-1] != ".": name = "%s." % name
    cmd = "nslookup %s %s" % (name, server)
    output = exec_program(cmd.strip()).strip("\r\n").split("\r\n")
    if output[-1].startswith("***"): return ""
    while len(output):
        x = output.pop().split(":")
        if x[0] == "Address": return x[1].strip()
        if not x[0]: return ""

def rlstrip_list(string_list):
    """
    Takes in a list of strings and removes the empty space to the
    left and right of each string in the list.
    """
    for index in range(len(string_list)):
        string_list[index] = string_list[index].rstrip().lstrip()
    return string_list

def remove_blanks_from_list(item_list):
    """
    Takes in a list of items and returns a list with all the empty
    items removed from the list.
    """
    index = 0
    while index < len(item_list):
        if item_list[index] == "":
            del item_list[index]
        else:
            index += 1
    return item_list

def load_config_file(cfg_file):
    """
    This function is used for load default configuration (.inf)
    Input:
    - cfg_file: name of configuration file.
    Output:
    - cfg_info: a dictionary of infomation from the configuration file
    """
    info = dict()
    cp   = ConfigParser.ConfigParser()
    cp.read(cfg_file)
    for s in cp.sections():
        for i in cp.items(s):
            info[i[0]] = i[1]

    if not info:
        raise Exception('Cannot load any info from cfg file %s' % cfg_file)

    return info

def get_country_code_list(filename, countries = False):
    """
    Get all country codes from Country Matrix file
    """
    if not os.path.isfile(filename):
        raise Exception("%s is not a valid file" % filename)

    workbook = xlrd.open_workbook(filename)
    sh = workbook.sheet_by_index(0)

    # Find column that defines country code
    pat_cc = "^Country$"
    country = list()

    for i in range(sh.nrows):
        row_vals = sh.row_values(i)
        for val in row_vals:
            if val:
                mobj = re.search(pat_cc, str(val))
                if mobj:
                    country = sh.col_values(row_vals.index(val))
                    #@author: Chico@change:if countries = True, country will change from ['US'] to [('US':'UNITED_STATES')], @bug: ZF-9159
                    if countries:
                        countries_detail = sh.col_values(row_vals.index(val)+2)
                        for index_countries in range(len(countries_detail)):
                            country[index_countries]=(country[index_countries],countries_detail[index_countries])
                    break
        if country:
            break
    if not country:
        raise Exception("File [%s]: does not have Country column" % filename)

    # Get country code from Country Column
    cc_list = []
    for val in country:
        if val:
            if isinstance(val, tuple):
                #@author: Chico@change:if some has countries but has not country code, then the CLI can't execute those commands. They will be ignored from the matrix table.
                if val[0] and val[1]:
                    cc_list.append(val)
            else:
                cc_list.append(val)

    return cc_list[1:]#@author: Chico@change:remove the first element which is the title.
    #@author: Chico@change:if countries = True, country will change from ['US'] to [('US':'UNITED_STATES')], @bug: ZF-9159

def parse_country_matrix_xsl(filename, ap_model):
    """
    Get information from Country Matrix file for a specific AP
    @param filename: name of Country Matrix file
    @param ap_model: model of AP

    Output will be a list of dictionaries, each dictionary is a information of each countrycode
    Example: {'country':'BE', '2.4GHz':{'1':'20', '2':'20'}, '5GHz':{'36:'17', '40':'17'}}
    """
    if not os.path.isfile(filename):
        raise Exception("%s is not a valid file" % filename)

    workbook = xlrd.open_workbook(filename)
    sh = workbook.sheet_by_index(0)

    if 'zf' in ap_model.lower():
        ap_model = ap_model[2:]

    # Get all columns that has information of a specific device
    cols_of_dev = list()
    freq_cells = list()
    found_dev = False
    for idx in range(sh.nrows):
        row_vals = sh.row_values(idx)
        for i in range(len(row_vals)-1): #attention@author: Chico@change: ignoring the last column 'note'
            if row_vals[i]:
                try:
                    if ap_model.lower() in str(row_vals[i]).lower():#attention@author: Chico@change: format in standard
                        cols_of_dev.append(i)
                        freq_cells.append(sh.cell_value(idx+1, i))
                        found_dev = True
                except:
                    print("row number %s, column number %s" % (idx,i))
        if found_dev: break

    if not found_dev:
        raise Exception("File [%s]: does not have any information of product %s" %
                        (filename, ap_model))

    # Find column that defines country code
    pat_cc = "^Country$"
    country = list()
    row_header = ''
    for i in range(sh.nrows):
        row_vals = sh.row_values(i)
        for val in row_vals:
            if val:
                mobj = re.search(pat_cc, str(val))
                if mobj:
                    country = sh.col_values(row_vals.index(val))
                    break
        if country:
            row_header = i
            break
    if not country:
        raise Exception("File [%s]: does not have Country column" % filename)

    # Get country code from Country Column
    cc_list = []
    for val in country[int(row_header + 1):]:
        each_cc = dict()
        if val:
            each_cc['country'] = val
            each_cc['pos'] = country.index(val)
            each_cc['2.4GHz'] = dict()
            each_cc['5GHz'] = dict()
            cc_list.append(each_cc)


    # Get info from 2.4G Channels column
    ch11ng_pat = "^2\.4G\s+channels$"
    all_ch11ng = list()
    header = sh.row_values(row_header)
    for val in header:
        if val:
            mobj = re.search(ch11ng_pat, str(val))
            if mobj:
                all_ch11ng = sh.col_values(header.index(val))
                break
    if not all_ch11ng:
        raise Exception("File [%s]: does not have 2.4G Channel column")

    for freq in freq_cells:
        # If AP supports 11ng channels
        if freq in '2.4 - 2.4835':
            for countrycode in cc_list:
                # Get channel range that AP supports for 11ng
                channel_range = all_ch11ng[countrycode['pos']]
                channel_list = range(int(channel_range.split('-')[0]), int(channel_range.split('-')[1]) + 1)

                txpower = sh.cell_value(countrycode['pos'], cols_of_dev[freq_cells.index(freq)])
                for channel in channel_list:
                    countrycode['2.4GHz'][str(channel)] = int(txpower)

        if freq in '5.15 - 5.25':
            # If AP supports channels 36, 40, 44
            for countrycode in cc_list:
                txpower = sh.cell_value(countrycode['pos'], cols_of_dev[freq_cells.index(freq)])
                if type(txpower) in [float, int]:
                    channel_list = ['36', '40', '44', '48']
                    for channel in channel_list:
                        countrycode['5GHz'][channel] = int(txpower)

        # If AP supports channels in U-NII1 band
        if freq in '5.25 - 5.35':
            for countrycode in cc_list:
                txpower = sh.cell_value(countrycode['pos'], cols_of_dev[freq_cells.index(freq)])
                if type(txpower) in [float, int]:
                    channel_list = ['52', '56', '60', '64']
                    for channel in channel_list: countrycode['5GHz'][channel] = int(txpower)

        if freq in '5.47 - 5.725':
            for countrycode in cc_list:
                txpower = sh.cell_value(countrycode['pos'], cols_of_dev[freq_cells.index(freq)])
                if type(txpower) in [float, int]:
                    channel_list = ['100', '104', '108', '112', '116', '120', '124', '128', '132', '136', '140']
                    for channel in channel_list: countrycode['5GHz'][channel] = int(txpower)

        if freq in '5.725 - 5.825':
            for countrycode in cc_list:
                txpower = sh.cell_value(countrycode['pos'], cols_of_dev[freq_cells.index(freq)])
                if type(txpower) in [float, int]:
                    channel_list = ['149', '153', '157', '161', '165']
                    for channel in channel_list: countrycode['5GHz'][channel] = int(txpower)

    for cc in cc_list:
        del cc['pos']

    return cc_list

def create_custom_file(inputfile, ap_profile, outputfile, encrypt = True, psk = ''):

    ft = open(inputfile)
    fo = open(outputfile, 'w')
    if not encrypt:
        cmd = "./RuckusAutoTest/common/custom_add_header.dat %s %s > %s" % (inputfile, ap_profile, outputfile)
    else: cmd = "./RuckusAutoTest/common/omac.dat -i %s -o %s -k %s -v \"RaFeioWu\"" % (inputfile, outputfile, psk)
    os.system(cmd)
    time.sleep(1)

    ft.close()
    fo.close()

def convert_str_to_time_delta(**kwargs):
    '''
    - don't pass the extra 's' in 'mins' to this function
    kwargs:
    - str
    - seperators
    return:
    - a dict
    '''
    time = kwargs['str']
    uptime = {}
    for sep in kwargs['seperators'].keys():
        r = re.search('(\d+) %ss?' % sep, time) # ex: '(\d+) secs?'
        if r and r.group(1): uptime[kwargs['seperators'][sep]] = int(r.group(1))

    logging.debug('Uptime as dict: %s' % uptime)
    return datetime.timedelta(**uptime)


def get_uptime(str):
    UPTIME_SEP = dict(day='days', hr='hours', min='minutes', sec='seconds')
    time_del = convert_str_to_time_delta(**dict(str=str, seperators=UPTIME_SEP))

    uptime = time_del.days * 3600 * 24 + time_del.seconds
    return uptime

def set_super_ruca_attenuation(id, db):
    """
    configure attenuation value to super ruca
    id: super ruca id
    db: attenuation value
    """
    cmdline = "rac -i%s -v%s" % (str(id), str(db))
    print cmdline
    exec_program(cmdline)

# Example:
#
# environ variables:
#   set SELENIUM_SERVER_DIRT=C:\rwqaauto\xpkgs\selenium-rc-1.0.3
#   set SELENIUM_SERVER_PORT=5555
# command:
#   get_selenium_cmdline(os.path.join(os.path.dirname(__file__)))
def get_selenium_cmdline(
        selenium_dir = './', selenium_name = 'selenium-server.jar', port = 4444
    ):
    '''
    '''
    SELENIUM_SERVER_DIRE = "SELENIUM_SERVER_DIRE"
    SELENIUM_SERVER_NAME = "SELENIUM_SERVER_NAME"
    SELENIUM_SERVER_PORT = "SELENIUM_SERVER_PORT"
    RAT_LOGGER_CONF = "RAT_LOGGER_CONF"
    SELENIUM_SERVER_OPTIONS = "SELENIUM_SERVER_OPTIONS"

    #
    # Selenium RC Server configuration
    #
    if os.environ.has_key(SELENIUM_SERVER_DIRE):
        selenium_dir = os.environ.get(SELENIUM_SERVER_DIRE)

    if os.environ.has_key(SELENIUM_SERVER_NAME):
        selenium_name = os.environ.get(SELENIUM_SERVER_NAME)

    if os.environ.has_key(SELENIUM_SERVER_PORT):
        port = int(os.environ.get(SELENIUM_SERVER_PORT))

    #
    # Selenium RC Server Options
    # Ref: http://seleniumhq.org/docs/05_selenium_rc.html

    # Example:
    # C:\>echo %SELENIUM_SERVER_OPTIONS%
    # -multiWindow -DfirefoxDefaultPath='C:\Program Files\Mozilla Firefox 4\firefox.exe'
    # -DfirefoxProfileTemplate='D:\firefox_profiles\ff4\ff4.rat'
    #
    if os.environ.has_key(SELENIUM_SERVER_OPTIONS):
        selenium_options = os.environ.get(SELENIUM_SERVER_OPTIONS)

    # This is for backward compatibility with previous An's work
    else:
        # Modified to use user firefox profile
        # An Nguyen - an.nguyen@ruckuswireless.com - Nov 2010
        if os.environ.has_key('BROWSERPROFILEPATH'):
            selenium_options = \
                '-multiwindow -firefoxProfileTemplate "%s"' % os.environ['BROWSERPROFILEPATH']

        else:
            selenium_options = '-multiwindow'


    #
    # Selenium RC Server jar file
    #
    selenium_jar = os.path.realpath(os.path.join(selenium_dir, selenium_name))
    logging.debug('[selenium_jar]: %s' % selenium_jar)

    if not os.path.exists(selenium_jar):
        raise NameError("[Selenium jar] Not exist: %s" % (selenium_jar))

    #
    # Logging configuration
    #
    if os.environ.has_key(RAT_LOGGER_CONF):
        logger_conf = os.environ.get(RAT_LOGGER_CONF)

    else:
        logger_conf = "rat-configuration.properties"

    # If an absolute file path is provided, use it
    if os.path.isfile(logger_conf):
        log_file = logger_conf

    # Not an absolute log config, so assume it is under selenium_dir
    else:
        log_file = os.path.realpath(os.path.join(selenium_dir, logger_conf))


    log_cfg = '-Djava.util.logging.config.file=%s' % log_file


    #
    # Now generate the full command line for Selenium
    #
    selenium_cmd = ("java %s -jar %s -port %d %s" %
                    (log_cfg, selenium_jar, int(port), selenium_options))

    return (selenium_cmd, port)

def mac_address_standardized(mac):
    """
    This function used to standardize the mac address follow the format xx:xx:xx:xx:xx:xx
    """
    temp = mac.replace(":", "").replace("-", "").replace(".", "").upper()
    return temp[:2] + ":" + ":".join([temp[i] + temp[i+1] for i in range(2,12,2)])    

#
#
#
if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise Exception("Not enough parameter")
        if sys.argv[1] == "ping":
            if len(sys.argv) < 3:
                raise Exception("Not enough parameter to perform subcommand 'ping'")
            param = eval(sys.argv[2])
            print "[[ping][%s]]" % ping(**param)
            exit()
    except Exception, e:
        print "[[ERROR][%s]]" % e.message


