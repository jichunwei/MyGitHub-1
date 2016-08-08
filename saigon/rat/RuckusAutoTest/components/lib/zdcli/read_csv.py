'''
this module is used to read currently managed APs CSV file
by anzuo
'''
import os
import re
import logging
from RuckusAutoTest.common.utils import list_to_dict

def get_all_ap_briefs(file_path):
    if not os.path.isfile(file_path):
        raise Exception("cannot find/save csv file(%s)" % file_path)
    
    try:
        fs = open(file_path, 'r')
        fs_lines = []
        while True:
            line = fs.readline()
            if line == '':
                break
            else:
                regex = '\(.+\),.+\(.+\)'
                if re.search(regex, line):
                    match_str = re.search(regex, line).group()
                    match_str = match_str.replace(',', ':')
                    line = re.sub(regex, match_str ,line)
            if re.search('IPv.+ Address', line):
                line = line.replace(re.search('IPv.+ Address', line).group(),'IP Address')
            line = line.replace('\"','')   
            line = line.split(',')
            line.remove('\n')
            fs_lines.append(line)
        fs.close()
        
        aps_list = []
        for j in range(1, len(fs_lines)):
            tmp = dict([(i, fs_lines[j][fs_lines[0].index(i)]) for i in fs_lines[0]])
            if tmp.get("Channel"):
                tmp["Channel"] = tmp.get("Channel").replace(':', ',')
            aps_list.append(tmp)
        
        return list_to_dict(aps_list, 'MAC Address')
    except Exception, e:
        logging.info(e.message)