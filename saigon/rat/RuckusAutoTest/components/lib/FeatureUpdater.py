'''
FeatureUpdater class (implements based on Observer pattern)
. naming:
    object (or obj) in this file is a reference to
    . a module (/components/lib/...)
    or
    . a class instance (instance of APWebUI, FlexMaster, ZoneDirector.. classes)

. registering phase
    for libraries, actively registered those on FeatureUpdater module is loading
    for class instances, registered on __init__ of that instance

. notifying/updating phase
    actively update, instead of passively notifying to observer classes -- as
    defined by Observer pattern

  . if the feature is a dict then update the content of that dict.
    This is needed to update locators -- WebUI.info
  . otherwise, replace that attribute/method with the given one

'''
import re
import sys
import types
import logging

from RuckusAutoTest.common import lib_FeatureTree as fttree
from RuckusAutoTest.common import lib_FeatureList as ftlist


zd_list=[]    
MODULE_TMPL = 'RuckusAutoTest.components.lib.%s'
MODULE_NAME_TMPL = 'lib.%s.'

ptype_obj_map = dict(
    ap = dict(
        cls = ['APWebUI', 'ZF', 'VF', 'RuckusAP'],
        lib = ['ap', 'apcli'],
    ),
    zd = dict(
        cls = ['ZoneDirector', 'ZD', 'ZoneDirectorCLI'],
        lib = ['zd', 'simap', 'zdcli', 'snmp'],
    ),
    #fm = dict(
    #    cls = ['FlexMaster', 'FMDeviceView', 'FMDV'],
    #    lib = ['fm', #'fm9',
    #           'fmdv'],
    #),
)

rat_libraries = [lib for ptype in ptype_obj_map
                     for lib in ptype_obj_map[ptype]['lib']]

#updated by jluh 2013-10-29
zd_ft_dict = \
    dict(# top level, contains root node '9.5.0.0'
         level0={'root': ['9.5.0.0']},
         level1 = {'9.5.0.0': ['9.6.0.0', '9.5.1.0', '9.5.2.0', '9.5.3.0']},
         level2 = {'9.6.0.0': ['9.7.0.0', '9.6.1.0', '9.6.2.0', '9.6.3.0']},
         level3 = {'9.7.0.0': ['9.8.0.0', '9.7.1.0', '9.7.2.0', '9.7.3.0']},
         level4 = {'9.8.0.0': ['9.9.0.0', '9.8.1.0', '9.8.2.0', '9.8.3.0']},
         level5 = {'9.9.0.0': ['9.10.0.0', '9.9.1.0', '9.9.2.0', '9.9.3.0','9.9.0.99']},
         level6 = {'9.10.0.0': ['9.12.0.0','9.10.1.0']},
#         level6 = {'10.0.0.0': ['10.1.0.0', '10.0.1.0', '10.0.2.0', '10.0.3.0']},
    )
#updated by jluh 2013-10-29
#0.0.0.99 will follow the last version.
first_num = True
comp_num = ''
for num in zd_ft_dict.keys():    
    if first_num:
        comp_num = int(re.findall(r'level(\d+)', num)[0])
        first_num = False
        continue
    if comp_num < int(re.findall(r'level(\d+)', num)[0]):
        comp_num = int(re.findall(r'level(\d+)', num)[0])
      
last_ver_key = u'level' + str(comp_num)
zd_ft_dict[last_ver_key][zd_ft_dict[last_ver_key].keys()[0]].append('0.0.0.99')

#generate the feature tree.    
zd_ftree = fttree.FeatureTree(zd_ft_dict)

#fm_flist = ['8.0.0.0', '9.0.0.0']


def _get_obj_name_type(obj):
    '''
    . returning obj (a library or class instance) name and its type in a tuple
    . obj_type is returned as string for better debug printing
    '''
    if type(obj) is types.InstanceType:
        return obj.__class__.__name__, 'class instance'

    elif type(obj) is types.ModuleType:
        return obj.__name__.split('.')[-1], 'module'

    raise Exception('Unknown object: %s' % obj)


def _instance_to_ptype(instance):
    '''
    . map a class instance to a specific product type, ie.:
      call with instance is a FlexMaster instance will return 'fm'
    '''
    cls_name = instance.__class__.__name__.lower()

    for k, ptype_to_obj in ptype_obj_map.iteritems():
        for c in ptype_to_obj['cls']:
            if c.lower() in cls_name:
                return k

    return None


def _module_to_ptype(module):
    '''
    . map a module to a specific product type
    '''
    module_full_name = module.__name__
    for k, ptype_to_obj in ptype_obj_map.iteritems():
        for m in ptype_to_obj['lib']:
            if MODULE_NAME_TMPL % m in module_full_name:
                return k

    return None


def obj_to_ptype(obj):
    obj_name, obj_type = _get_obj_name_type(obj)
    if obj_type == 'module':
        return _module_to_ptype(obj)

    return _instance_to_ptype(obj)


def _get_updating_version_list(ptype, version):
    '''
    . fm updates the version as accumulated version list
    . zd based on its tree
    '''
    #Don't need support FM again, updated by cwang@20130529
    #if ptype.lower() in ptype_obj_map['fm']['lib']:
    #    return ftlist.accumulate_versions(fm_flist, version)

    return [n.value for n in zd_ftree.iterate_path(str(version))]


class FeatureUpdater(object):
    '''
    _objs: a dict as below:
      dict(
        zd = [zd_obj1, zd_lib1, zd_lib2,... ]
        fm = [fm_obj1, fm_lib1, fm_lib2,... ]
      )
    '''
    _objs = {}

    @classmethod
    def register(cls, obj):
        '''
        Add an observer (a library under /components/lib/.. or an obj instance)
        . for library case, the ptype is needed
        . for class object case, it will be detected by obj_to_product_type()
        '''
        ptype = obj_to_ptype(obj)

        # don't let un-needed obj to register (ie. WebUI)
        # only subclasses of WebUI should be
        if ptype is None:
            return

        if ptype not in cls._objs:
            cls._objs[ptype] = [obj]

        else:
            if obj not in cls._objs[ptype]: # this guarantee no duplications!
                cls._objs[ptype].append(obj)


    @classmethod
    def notify(cls, obj, device_ver):
        '''
        Notifies the changes to all observers.
        '''
        global zd_list
        show_feature_update_log = True   
        ptype = obj_to_ptype(obj)
        # for each object (lib in this case) that was registered
        for obj in cls._objs[ptype]:
            from RuckusAutoTest.components import ZoneDirector 
            #West:if the ZD has been upgrade,do not upgrade the zd
            if isinstance(obj, ZoneDirector.ZoneDirector):
                if len(zd_list)==1 and obj in zd_list:
                    logging.info("Current obj is instance of ZoneDirector, and existed in zd_list, don't need update again.")
                    continue
                else:
                    zd_list.append(obj)
            
            if len(zd_list)==2:
                zd_list=[]
                         
            # walks from root node to node equals to device_ver
            for node in _get_updating_version_list(ptype, device_ver):
                # checks against each version listed in the object (lib)
                # and does the accumulative update from root to device_ver's node
                for (obj_version, feature_table) in obj.feature_update.iteritems():
                    if obj_version == node:
                        if obj_version == device_ver and show_feature_update_log:
                            logging.debug('Feature Update to the version %s' % obj_version)
                            show_feature_update_log = False
                        FeatureUpdater._update(feature_table, obj, obj_version)
                        


    @classmethod
    def _update(cls, feature_table, obj, obj_version):
        '''
        . actively update the obj (library or class instance) with the features
          in the feature_table
          . feature is an attribute or method or constant of the given object

          . if the feature is a dict then update the content of that dict.
            This is needed to update locators -- WebUI.info
          . otherwise, replace that attribute/method with the given one
        '''
        obj_name, obj_type = _get_obj_name_type(obj)
        for feature in feature_table:
            try:
#                logging.debug('Updating %s in %s %s to the version %s' %
#                              (feature, obj_name, obj_type, obj_version))                                    
                if isinstance(feature_table[feature], types.DictionaryType):                    
                    getattr(obj, feature).update(feature_table[feature])

                else:
                    setattr(obj, feature, feature_table[feature])

            except Exception, e:
                logging.debug('Error updating feature!!!' + e.message)


def register_libraries():
    '''
    . looks for the product's corresponding libraries under
      RuckusAutoTest.components.lib and registers them if they have
      the 'feature_update' attribute
    '''
    from RuckusAutoTest.components import Helpers as lib # required!
    for ptype in rat_libraries:
        for obj in sys.modules[MODULE_TMPL % ptype].__dict__.itervalues():
            if type(obj) == types.ModuleType and hasattr(obj, 'feature_update'):
                FeatureUpdater.register(obj)


## uncomment these settings if you want to run FeatureUpdater directly
#from django.core.management import setup_environ
#import settings
#setup_environ(settings)


# actively register all product's library when Feature Update is initialized
register_libraries()


if __name__ == "__main__":
    def log(version):
        print 'Update for ver %s' % version

    #FeatureUpdater.register(log)
    from RuckusAutoTest.components.lib.zd import guest_access_zd
    if hasattr(guest_access_zd, "feature_update"):
        FeatureUpdater.register(guest_access_zd, 'zd')

    FeatureUpdater.notify('zd', '9.5.0.0')
