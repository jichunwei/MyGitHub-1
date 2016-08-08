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
def compare_xml_file_on_pc(dir_a,filename_a,dir_b,filename_b,filename='',
                           part_sync_file={'system.xml':("identity","mgmt-ip","mgmt-vlan","dhcps","cluster",
                                                         "realtime-monitor","time","portlet-pref","remote-access", "tr069"),
                                           'system.xmlbak':('cluster',),
                                            }
                           ): 
    #add node which you don't want to compare to 'part_sync_file', key is xml file name, value is a tuple contains node name
    path_a = os.path.join(dir_a,filename_a)
    path_b = os.path.join(dir_b,filename_b)
    
    if _compare_whole_file_only(path_a,path_b):
        msg='%s in both zd is the same' % filename
        return True,"[%s]%s " % (filename,msg)
    
    not_sync_node = ()
    logging.info('file name:' + filename)
    if part_sync_file.has_key(filename):
        if not part_sync_file[filename]:
            result,msg = _compare_xml_root_node_child_number(path_a,path_b)
            return result,"[%s]%s " % (filename,msg)
        not_sync_node=part_sync_file[filename]
    logging.info('begin compare %s node by node' % filename)
    result,msg = _compare_xml_node_by_node(path_a,path_b,*not_sync_node)
    return result,"[%s]%s " % (filename,msg)

#compare thd child nod number
def _compare_xml_root_node_child_number(file_path_a,file_path_b):
    dom1 = minidom.parse(file_path_a)
    dom2 = minidom.parse(file_path_b)
    root1 = dom1.documentElement
    root2 = dom2.documentElement
        
    if(len(root1.childNodes)!=len(root2.childNodes)) and (len(root1.childNodes)<500 or len(root2.childNodes)<500):
        logging.error("child node number mismatch![%s:%d,%d]" % (root1.nodeName,len(root1.childNodes),len(root2.childNodes)))
        return False,'root node child number not match'
    return True,'root node child number match:%d' % len(root1.childNodes)
           
    
#compare xml file from root node
def _compare_xml_node_by_node(file_path_a,file_path_b,*special_node):
    dom1 = minidom.parse(file_path_a)
    dom2 = minidom.parse(file_path_b)
    root1 = dom1.documentElement
    root2 = dom2.documentElement
    
#    if _compare_xml_node(root1,root2,*special_node):
#        return True,' node by node compare OK'
#    else:
#        return False,'node by node compare not OK!'
    logging.info("start to compare %s and %s" % (file_path_a,file_path_b))
    return _tmp_compare_xml_node(root1, root2, *special_node)


def _tmp_compare_xml_node(node1, node2, *special_node):        
    #1st, compare node name
    if node1.nodeName != node2.nodeName:
        msg = "COMPARE FAIL: nodes' names[%s, %s] are different" % (str(node1.nodeName), str(node2.nodeName))
        logging.error(msg)
        return False, msg
    
    #2nd, compare node type
    if node1.nodeType != node2.nodeType:
        msg = "COMPARE FAIL: node[%s]'s type[%s, %s] are different" % (str(node1.nodeName), node1.nodeType, node2.nodeType)
        logging.error(msg)
        return False, msg
    
    #3rd, skip compare special node or filter useless attribute, such as 'SKIP_POPULATE'
    if node1.nodeName in special_node:
        return True, "skip special node[%s, %s]" % (str(node1.nodeName), str(node2.nodeName))
    node1_attr = _filter_useless_node_attribute(node1.attributes.items())
    node2_attr = _filter_useless_node_attribute(node2.attributes.items())
    
    #4th, compare node attributes value
    if node1_attr != node2_attr:
        if set(node1_attr) != set(node2_attr):
            union = set(node1_attr) & set(node2_attr)
            msg = "COMPARE FAIL: node[%s]'s attributes[%s, %s] are different" % (str(node1.nodeName), str(set(node1_attr)-union), str(set(node2_attr)-union))
            logging.error(msg)
            return False, msg
    
    #5th, compare child nodes
    childnodes1 = node1.childNodes
    childnodes2 = node2.childNodes
    #remove TEXT_NODE, COMMENT_NODE
    tmp_childnode = []
    for x in childnodes1:
        if x.nodeType in [x.TEXT_NODE, x.COMMENT_NODE]:
            tmp_childnode.append(x)   
    for y in tmp_childnode:
        childnodes1.remove(y)
    
    tmp_childnode = []        
    for x in childnodes2:
        if x.nodeType in [x.TEXT_NODE, x.COMMENT_NODE]:
            tmp_childnode.append(x)
    for y in tmp_childnode:
        childnodes2.remove(y)
    
    if len(childnodes1) != len(childnodes2):
        msg = "COMPARE FAIL: node[%s]'s child nodes length[%s, %s] are different" % (str(node1.nodeName), childnodes1, childnodes2)
        logging.error(msg)
        return False, msg
    
    for idx in range(len(childnodes1)): 
        res, msg = _tmp_compare_xml_node(childnodes1[idx], childnodes2[idx], *special_node)
        if not res:
            return res, msg
    
    return True, "COMPARE PASS"
    

def _filter_useless_node_attribute(attr_items):
    for attr in attr_items:
        if attr[0].strip() in ['SKIP_POPULATE','last-seen', 'UPD_OBJ_FAILED']:
            attr_items.remove(attr)
        #TODO: add more attribute which you don't want to compare here
    return attr_items

#a recursive function compare xml node and its child node
def _compare_xml_node(node1,node2,*special_node):
    logging.info('let us begin to compare %s and %s' % (node1.nodeName,node2.nodeName))
    # add because in system.xml tun-enc is reamed by tun-cfg
    node1_attr=node1.attributes.items()
    node2_attr=node2.attributes.items()
#    if node1.nodeName=='tun-enc' or node1.nodeName=='tun-cfg':
#        import pdb
#        pdb.set_trace()
    if node1.nodeName=='tun-enc' and node2.nodeName=='tun-cfg' or node2.nodeName=='tun-enc' and node1.nodeName=='tun-cfg':
        
        if (('enabled','false') in node1_attr) and (('encrypt','true') in node2_attr) or (('enabled','false') in node2_attr) and (('encrypt','true') in node1_attr):
            logging.info("COMPARE FAIL: tun-enc and tun-cfg,compare not ok")
            return False
        logging.info("tun-enc and tun-cfg,compare ok")
        return True
    if (node1.nodeName==node2.nodeName)and(node1.nodeName in special_node):
        logging.info('[%s] is not sync node,not need to be compared' % node1.nodeName)
        return True
    
    if(node1.nodeName!=node2.nodeName or node1.nodeType!=node2.nodeType):
        logging.error("COMPARE FAIL: node type or name mismatch!type:[%s,%s],name:[%s,%s]" 
                      % (node1.nodeType,node2.nodeType,node1.nodeName,node2.nodeName))
        return False
    
    if  (('enabled','false')      in node1_attr) and (('enabled','false')     in node2_attr) or\
        (('tr069enable','false')  in node1_attr) and (('tr069enable','false') in node2_attr) or\
        (('enable','no')          in node1_attr) and (('enable','no')         in node2_attr):
        logging.info('item [%s] not enable,do not need compare' % node1.nodeName)
        return True
    
    #@author: Anzuo, @since: 20140124, @change: delete attribute of 'SKIP_POPULATE'
    node1_attr = node1.attributes.items()
    node2_attr = node2.attributes.items()
    for attr in node1_attr:
        if attr[0] == 'SKIP_POPULATE':
            node1_attr.remove(attr)
            
    for attr in node2_attr:
        if attr[0] == 'SKIP_POPULATE':
            node2_attr.remove(attr)
    
    if sorted(node1_attr)!=sorted(node2_attr):
        logging.error("COMPARE FAIL: node attributes mismatch![%s]" % node1.nodeName)
        return False
    
    child_list1=copy.copy(node1.childNodes)
    child_list2=copy.copy(node2.childNodes)
    if(len(node1.childNodes)!=len(node2.childNodes)):
        if(len(node1.childNodes)>len(node2.childNodes)) and (len(node1.childNodes)-len(node2.childNodes)==2):
            node_more = node1
            node_less = node2
        elif(len(node1.childNodes)<len(node2.childNodes)) and (len(node2.childNodes)-len(node1.childNodes)==2):
            node_more = node2
            node_less = node1
        else:        
            logging.error("COMPARE FAIL: child node number mismatch![%s:%d,%d]" % (node1.nodeName,len(node1.childNodes),len(node2.childNodes)))
            return False
        
        child_list1=copy.copy(node_more.childNodes)
        child_list2=copy.copy(node_less.childNodes)
        for child_node in  child_list1:
            if child_node.nodeName=='wips':
                wips_index=child_list1.index(child_node)
                child_list1.pop(wips_index+1)
                child_list1.remove(child_node)
           
    for child1, child2 in zip(child_list1, child_list2):
        if  child1.nodeType == child2.TEXT_NODE and child1.data!=child2.data:
            logging.error("COMPARE FAIL: text node content mismatch![%s(nodename):%s,%s]" % (child1.nodeName,child1.data,child2.data))
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
    
  