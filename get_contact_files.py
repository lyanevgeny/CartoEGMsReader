import glob
import re
import numpy as np
import matplotlib.pyplot as plt


def get_contact_files(search_dir):
    file_list = []
    glob_result = glob.glob(search_dir + '/*ContactForce.txt')
    if glob_result:
        for name in glob.glob(search_dir + '/*ContactForce.txt'):
            result = re.search('(.*)_P(.*)_ContactForce.txt', name)
            current_map = result.group(1).split('\\')[1]
            current_point = result.group(2)
            corresponding_ecg_file = search_dir + "\\{}_P{}_ECG_Export.txt".format(current_map, current_point)
            if glob.glob(corresponding_ecg_file):
                file_list.append([name, corresponding_ecg_file])
            else:
                print("The corresponding ECG file not found for "+name)
    print(str(len(file_list)) + " ContactForce files with corresponding ECG files found.")
    return file_list if file_list else None


def get_contact_data(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    read_data = False
    contact_data = np.empty((0, 9), int)

    for i, line in enumerate(lines):
        if read_data:
            newline = np.fromstring(line, dtype=float, sep=' ')
            contact_data = np.append(contact_data, [newline], axis=0)
        if i == 7:
            read_data = True

    return np.transpose(contact_data)


def plot_force_data(data):
    s = list(data[3])
    fig, ax = plt.subplots()
    ax.plot(s)
    ax.set(title='Contact force data')
    ax.grid()
    plt.show()


if __name__ == '__main__':

    # 1. specify directory with Carto files
    folder = 'data1'

    # 2. search there for ContactForce data files and get a list with files to be analyzed
    files = get_contact_files(folder)

    # 3. process files (plot each file)
    if files is not None:
        for i, f in enumerate(files):
            if i < 3:  # limit 3
                plot_force_data(get_contact_data(f[0]))
