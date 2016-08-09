"""
Utility commands to deal with csv files.


01  [command csv_as_list_dict()]
        return a list-of-dictionary of csv file with the frist row its key of dictionary.
    [Example]
        csvld = csv_as_list_dict('batch_dpsk_100_20091007.csv')
        pprint(csvld)

"""
import csv
import sys
from pprint import pprint, pformat


def csv_as_list_dict(csvFilename, **kwargs):
    fcfg = dict(debug=False)
    fcfg.update(kwargs)
    csvReader = csv.reader(open(csvFilename))
    klist = None
    result = list()
    for row in csvReader:
        if type(klist) is not list:
            klist = row
            continue
        result.append(dict(zip(klist,row)))
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("CSV filename required\n\n\tUsage: %s <csv filename>" % sys.argv[0])
    csvld = csv_as_list_dict(sys.argv[1])
    print "List-of-Dictionary of csv file:%s\n%s" % (sys.argv[1], pformat(csvld))
