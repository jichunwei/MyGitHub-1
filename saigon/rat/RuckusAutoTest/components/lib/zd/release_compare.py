
def integ_release_list(release):
    number_string_list = release.split('.')
    number_integ_list = []
    for number in number_string_list:
        try:
            number_integ_list.append(int(number))
        except:
            raise Exception("String %s in the release number can't be integ-ed" % (number))
    return number_integ_list
        
def older_than_release(current_relase=None, target_release='9.8.0.0'):
    '''
    1: Yes, current release is older than target release
    0: No, current release is newer than target release
    None: current release is equal than target release
    
    '''
    integ_current_release = integ_release_list(current_relase)
    integ_target_release = integ_release_list(target_release)
    
    for x1 in integ_current_release:
        x2=integ_target_release[integ_current_release.index(x1)]
        if x1 > x2:
            return 0
        elif x1 == x2:
            continue
        else:
            return 1
    
    if len(integ_current_release) == len(integ_target_release):
        return None
    else:
        return 1


def main():
    target_release = raw_input('Please input the release number you want to compare to: ')
    current_release = raw_input('Current_release is: ')
    if older_than_release(current_release, target_release):
        print('Yes! %s is older than %s' % (current_release, target_release))
    else:
        print('No! %s is newer than or equal to %s' % (current_release, target_release))
    

if __name__ == '__main__':
    main()
