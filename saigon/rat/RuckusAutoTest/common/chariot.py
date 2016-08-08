'''
Created on 2011-6-8

@author: serena.tan@ruckuswireless.com

This library let you clone a chariot test, run the test and format the test result using the chariot command line.

For more information about the chariot command line, please refer to User Guide for Chariot -> How To -> Command-Line Programs.
'''


from subprocess import Popen, PIPE, STDOUT
import re
import logging
import os


ARGS_MAP = {'txt': "",
            'html': "-h",
            'csv':  "-v"
            }


#------------------------------------------------------------------------------------------------------------------------------
#                                        PUBLIC METHODs 

def chariot_test(template_filename, endpoint_pair_list, result_filename, result_type, timeout = None):
    '''
    Create a clone file according to the endpoint pair list,
    clone the test template using the clone file, 
    run the test, generate the result file and format the result file if needed.
    
    Input:
    template_filename:    a tst file created by chariot console.
    endpoint_pair_list:   a list of the endpoint pairs information.
        [{"num_in_temp": 1,    #endpoint pair number in the format file, start from 1
          "endpoint1_ip": "192.168.0.10",
          "endpoint2_ip": "192.168.0.100"},
         {"num_in_temp": 1,
          "endpoint1_ip": "192.168.0.10",
          "endpoint2_ip": "192.168.0.100"},
         {"num_in_temp": 2,
          "endpoint1_ip": "192.168.0.10",
          "endpoint2_ip": "192.168.0.100"},
         {"num_in_temp": 1,
          "endpoint1_ip": "192.168.0.10",
          "endpoint2_ip": "192.168.0.150"},
          ...
        ]
    result_filename:    name of the test result file.
    result_type:        format of the result file, 'tst'/'txt'/'html'/'csv'.
    
    For more information about how to clone chariot test, please refer to 
    User Guide for Chariot -> How To -> Command-Line Programs -> CLONETST--Replicating Pairs in a Test
    '''
    _filenames = dict(clone_filename = 'chariot_clone.txt',
                      test_filename = 'chariot_test.tst',
                      res_filename = 'chariot_result.tst'
                      )
    
    remove_files(_filenames.values())
    
    create_clone_file(endpoint_pair_list, _filenames['clone_filename'])
    
    res, msg = clone_test(template_filename, _filenames['clone_filename'], _filenames['test_filename'])
    if not res:
        return (False, msg)
    
    if result_type == 'tst':
        if not re.search("\.tst$", result_filename, re.I):
            result_filename += ".tst"
            
        res, msg = run_test(_filenames['test_filename'], result_filename, timeout)
        if not res:
            return (False, msg)
    
    else:
        res, msg = run_test(_filenames['test_filename'], _filenames['res_filename'], timeout)
        if not res:
            return (False, msg)
        
        res, msg = format_test_result(_filenames['res_filename'], result_filename, ARGS_MAP[result_type])
        if not res:
            return (False, msg)

    remove_files(_filenames.values())
    
    return (True, "Do the chariot test successfully")


def get_throughput_info(filename):
    '''
    Input:
        filename: name of the text file. 
    
    WARNING: Need to use format_test_result() to format the Chariot tst format file
             to text file before using this method.
        
    Output: 
        A dictionary of the throughput test results:
        {'1': {'Average': '4.231(Mbps)',
               'Confidence Interval': '0.857',
               'Maximum': '17.778(Mbps)',
               'Minimum': '0.731(Mbps)',
               'Relative Precision': '20.259',
               'Time': '18.910(secs)'
               },
         'Totals:': {'Average': '4.209(Mbps)',
                     'Maximum': '17.778(Mbps)',
                     'Minimum': '0.731(Mbps)'
                     }
        }
    '''
    logging.info('Get throughput information from file: %s.' % filename)
    th_table = _get_throughput_table(filename)
    th_info = {}
    
    #parse the parameters and unites
    paras = []
    unites = []
    line0 = th_table[0].split()
    line1 = th_table[1].split()
    for i in range(0, len(line0)):
        if "(" in line1[i]:
            paras.append(line0[i])
            unites.append(line1[i])
            
        else:
            paras.append(line0[i] + " " + line1[i])
            unites.append("")
    
    #parse the data
    for i in range(4, len(th_table)):
        line = th_table[i].split()
        th_info[line[0]] = {}
        for i in range(1, len(line)):
            th_info[line[0]][paras[i]] = line[i] + unites[i]
    
    logging.info('The throughput information is: %s' % th_info)
    return th_info


def create_clone_file(endpoint_pair_list, output_filename):
    """
    Create a text file used to clone Chariot test.
    Input:
        endpoint_pairs: a list of the endpoint pairs information.
        {"num_in_temp": 1,    #endpoint pair number in the format file, start from 1
         "endpoint1_ip": "192.168.0.10",
         "endpoint2_ip": "192.168.0.100"
        },
        output_filename: name of the output file.
    """
    lines = []
    for i in range(len(endpoint_pair_list)):
        pair = endpoint_pair_list[i]
        string = "%d %s %s\n" % (pair["num_in_temp"], pair["endpoint1_ip"], pair["endpoint2_ip"])
        lines.append(string)

    logging.info('Create the chariot clone file: %s.' % output_filename)
    f = open(output_filename, 'w')
    f.writelines(lines)
    f.close()
    logging.info('Create the chariot clone file successfully!')
    
    
def clone_test(template_filename, clone_filename, output_filename):
    '''
    Clone a Chariot test.
    Input:
        original_filename: name of the Chariot test file created at the Chariot console
        clone_filename:    a text file containing a list of pair numbers and network addresses
        output_filename:   name of the output file, if the file doesn't exist, create it,
                           if the file already exists, override it.
    
    Chariot command:
        CLONETST input.tst clone.txt output.tst
    '''
    logging.info('Clone the chariot test template: %s to a new test: %s.' % (template_filename, output_filename))
    cmd = "CLONETST %s %s %s" % (template_filename, clone_filename, output_filename)
    msg = _do_cmd(cmd)
    r = re.search("Clone completed successfully.", msg, re.I)
    if r:
        logging.info('Clone the chariot test file successfully!')
        return (True, msg)
    
    logging.info('Fail to clone the chariot test file: %s!' % msg)
    return (False, msg)


def run_test(tst_filename, res_filename = "", timeout = None, return_detail = False):
    '''
    Run a Chariot test. All endpoint pairs in the test file will be tested at the same time, 
    and all tests will stop if one of them finished.
    Input:
        tst_filename:        name of the Chariot test file, it should be a tst file
        res_filename:        name of the result file, if it is omitted, 
                             the results are written directly to the original test file
        timeout:             stop running the test after N seconds.
        return_detail:  return all run information
        
    Chariot command:
        RUNTST test_filename [new_test_filename] [-t N] [-v]
    '''
    logging.info('Run chariot test file: %s.' % tst_filename)
    cmd = "RUNTST %s" % tst_filename
    if res_filename:
        cmd += " %s" % res_filename
    
    if timeout:
        cmd += " -t %d" % timeout
        
    if return_detail:
        cmd += " -v"
        
    msg = _do_cmd(cmd)
    r = re.search("error|RUNTST has not completed", msg, re.I)
    if r:
        logging.info('Fail to run chariot test: %s!' % msg)
        return (False, msg)
    
    logging.info('Run chariot test successfully!')
    return (True, msg)


def format_test_result(res_filename, output_filename, args = ""):
    '''
    Format the Chariot test result file to an output file in other forms.
    Input:
        res_filename:    name of the Chariot result file, it should be a tst file
        output_filename: name of the output file, if the file doesn't exist, create it,
                         if the output file already exists, override it.
                         If the name doesn't has extend name, it will append a file extension 
                         like .txt, .CSV.. to the name
        args:            a string of options of command: FMTTST
    
    Chariot command:
        FMTTST tst_filename [output_filename] [-v [-o] [-s] [-d] | [-h [-c | -t template_name]]] [-q]
        
    The output file has three different forms: ASCII text, HTML Web page, or a .CSV spreadsheet file.
    args:
        -h: generate HTML output
        -v: generate spreadsheet output in the .CSV file format
        run FMTTST with no options to generate ASCII text
    '''
    logging.info('Format chariot test result file: %s to: %s.' % (res_filename, output_filename))
    cmd = "FMTTST %s %s -q" % (res_filename, output_filename)
    if args:
        cmd += " %s" % args
        
    msg = _do_cmd(cmd)
    r = re.search("error", msg, re.I)
    if r:
        logging.info('Faile to format chariot test result file: %s!' % msg)
        return (False, msg)
    
    logging.info('Format chariot test result file successfully!')
    return (True, msg)
    
    
def remove_files(filename_list):
    logging.info('Remove files: %s' % filename_list)
    for file in filename_list:
        if os.path.exists(file):
            os.remove(file)


#------------------------------------------------------------------------------------------------------------------------------
#                                        UNPUBLIC METHODs 

def _do_cmd(cmd):
    '''
    Execute command and get execution result.
    '''
    try:
        logging.info("Do command: %s" % cmd)
        p = Popen(cmd, stdin = PIPE, stdout = PIPE, stderr = STDOUT)
        msg = p.communicate()[0]

    except OSError, e:
        msg = 'Error when execute command, %s' % e

    return msg


def _get_throughput_table(filename):
    f = open(filename)
    data = f.read()
    f.close()
    
    th_table = []
    is_th_entry = False
    lines = data.split("\n")
    for line in lines:
        if "THROUGHPUT" in line:
            is_th_entry = True
            
        if "TRANSACTION RATE" in line:
            break
        
        if is_th_entry and len(line.strip()) > 0:
            th_table.append(line)
    
    return th_table[3:]

