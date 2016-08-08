'''
this module is used to compare two xml files in pc
by west.li
'''

import logging
import filecmp
from xml.dom import minidom
import time
import os    
import copy


#get not sync node from dictionary
#and then compare
#parameter 'filename' is used to get not sync nodes
#if a element in part_sync_file,only get a null tuple-for example 'xxx.xml':()-means only need to compare the number of child of rood node 
def compare_xml_file_on_pc(dir_a,dir_b,filename='',
                           part_sync_file={'system.xml':("identity","mgmt-ip","mgmt-vlan","dhcps","cluster",
                                                         "realtime-monitor","time","portlet-pref","remote-access"),
                                           'system.xmlbak':('cluster',),
                                            }
                           ):   
    path_a = os.path.join(dir_a,filename)
    path_b = os.path.join(dir_b,filename)
    
    if _compare_whole_file_only(path_a,path_b):
        msg='%s in both zd is the same' % filename
        return True,"[%s]%s " % (filename,msg)
    
    not_sync_node = ()
    logging.info('file name:' + filename)
    if part_sync_file.has_key(filename):
        not_sync_node=part_sync_file[filename]
    logging.info('begin compare %s node by node' % filename)
    result,msg = _compare_xml_node_by_node(path_a,path_b,*not_sync_node)
    return result,"[%s]%s " % (filename,msg)

#compare xml file from root node
def _compare_xml_node_by_node(file_path_a,file_path_b,*special_node):
    dom1 = minidom.parse(file_path_a)
    dom2 = minidom.parse(file_path_b)
    root1 = dom1.documentElement
    root2 = dom2.documentElement
    
    if _compare_xml_node(root1,root2,*special_node):
        return True,' node by node compare OK'
    else:
        return False,'node by node compare not OK!'
    

#a recursive function compare xml node and its child node
def _compare_xml_node(node1,node2,*special_node):
    logging.info('let us begin to compare %s and %s' % (node1.nodeName,node2.nodeName))
    
    node1_attr=node1.attributes.items()
    node2_attr=node2.attributes.items()

    if (node1.nodeName==node2.nodeName)and(node1.nodeName in special_node):
        logging.info('[%s] is not sync node,not need to be compared' % node1.nodeName)
        return True
    
    if(node1.nodeName!=node2.nodeName or node1.nodeType!=node2.nodeType):
        logging.error("node type or name mismatch!type:[%s,%s],name:[%s,%s]" 
                      % (node1.nodeType,node2.nodeType,node1.nodeName,node2.nodeName))
        return False
    
    node_name = node1.nodeName
    
    if  (('enabled','false')      in node1_attr) and (('enabled','false')     in node2_attr) or\
        (('tr069enable','false')  in node1_attr) and (('tr069enable','false') in node2_attr) or\
        (('enable','no')          in node1_attr) and (('enable','no')         in node2_attr):
        logging.info('item [%s] not enable,do not need compare' % node1.nodeName)
        return True
    
    if node_name == 'tr069':
        temp1=[]
        for attr in node1_attr:
            if '-password' not in attr[0]:
                temp1.append(attr)
        node1_attr = temp1
        temp2=[]
        for attr in node2_attr:
            if '-password' not in attr[0]:
                temp2.append(attr)
        node2_attr = temp2

    if sorted(node1_attr)!=sorted(node2_attr):
        logging.error("node attributes mismatch![%s]" % node1.nodeName)
        return False
    
    child_list1=copy.copy(node1.childNodes)
    child_list2=copy.copy(node2.childNodes)

    for child1, child2 in zip(child_list1, child_list2):
        if  child1.nodeType == child2.TEXT_NODE and child1.data!=child2.data:
            logging.error("text node content mismatch![%s(nodename):%s,%s]" % (child1.nodeName,child1.data,child2.data))
            return False
        
        if child1.nodeType==child1.ELEMENT_NODE and not _compare_xml_node(child1, child2,*special_node):
            return False
        
    return True
    

#use filecmp to compare whole file
def _compare_whole_file_only(file_path_a,file_path_b): 
    if filecmp.cmp(file_path_a,file_path_b):
        return True
    else:
        return False
 

  