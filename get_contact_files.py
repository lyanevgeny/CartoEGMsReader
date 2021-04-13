import glob
import re
import numpy as np


def get_contact_files(search_dir):
    file_list = []
    for name in glob.glob(search_dir+'/*ContactForce.txt'):
        result = re.search('(.*)_P(.*)_ContactForce.txt', name)
        current_map = result.group(1).split('\\')[1]
        current_point = result.group(2)
        file_list.append(["{}_P{}_ECG_Export.txt".format(current_map, current_point), "{}_P{}_ContactForce.txt".format(current_map, current_point)])
    return np.transpose(file_list)

 
# search folder 'data' for ContactForce data files and get a list with files to be analyzed
print(get_contact_files('data'))
