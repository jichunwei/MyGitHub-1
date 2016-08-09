'''
By west.li @2012.2.6
this file include function about List,not include in the standard function of python 
'''


#if a in b return True,else return False
def list_in_list(a,b):
    for i in a:
        if not i in b: 
            return False
    return True 
    
#return a list,
#if one element in list a and not in list b,it will be included in the returned list
#for example list_minus_list([1,2,3],[3,4,5]) will return [1,2]  
def list_minus_list(a,b):
    ret = []
    for i in a:
        if i not in b:
            ret.append(i) 
    return ret
    