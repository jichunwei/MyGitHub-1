'''
Library for Updating the Feature where feature are accumulated by each version
This lirary applies for FM
'''

def parse_version(version):
    '''
    . return version and build number as int for comparing
    '''
    l = version.split('.')
    return int(''.join(l[:4])), 0 if len(l) == 4 else int(l[4])


def accumulate_versions(version_list, version):
    '''
    . return a list of versions to be updated
    . below snippet is used for test this function
    '''
    release, build = parse_version(version)
    for i in reversed(range(len(version_list))):
        cur_release, cur_build = parse_version(version_list[i])
        if cur_release == release and cur_build <= build:
            return version_list[:i + 1]
        if cur_release < release:
            return version_list[:i + 1]
    raise Exception('given version (%s) can not be found' % version)


def tst():
    _tst_parse_version()
    _tst_acc_versions()


def _tst_parse_version():
    versions = ['9.0.0.0.142', '8.0.0.0', '9.1.0.5.11']

    for v in versions:
        print 'version: %12s >> %s' % (v, parse_version(v))
    print '\n'


def _tst_acc_versions():
    lst = ['8.0.0.0', '9.0.0.0', '9.0.0.0.150', '9.0.1.0', '9.0.1.0.121',
           '9.1.1.0', ]
    tst_lst = ['8.0.0.0.149', '9.0.0.0.149', '9.0.0.0.150', '9.0.0.0.151',
               '9.1.1.0.151']

    print 'List of versions:\n%s\n' % lst
    for v in tst_lst:
        print '%s >> %s' % (v, accumulate_versions(lst, v))
    print '\n'

