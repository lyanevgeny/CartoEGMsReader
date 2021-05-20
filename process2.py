import glob
import re
import numpy as np
import os


def get_paths(epdata_dir):
    print("\n> Scanning {}...".format(epdata_dir))
    carto_dir = glob.glob(epdata_dir + '/Carto')
    if len(carto_dir) == 0:
        print("> No Carto directory found, aborting")
    elif len(carto_dir) > 1:
        print("> Ambiguous file system, aborting")
    elif len(carto_dir) == 1:
        print("> Carto directory found ({})".format(carto_dir[0]))
        zip_dirs = []
        for root, dirs, files in os.walk(epdata_dir + '/Carto', topdown=False):
            for name in dirs:
                joined = os.path.join(root, name)
                if joined[-9:] == "extracted":
                    zip_dirs.append(joined)
        print("> {} valid directories with zip files found".format(len(zip_dirs)))
        zip_files = []
        for zd in zip_dirs:
            zip_dir = glob.glob(zd + '/*.zip')
            zip_files += zip_dir
        for z in zip_files:
            print(z)
        return zip_files


def get_files(search_dir, lim=None):
    contact_file_list = []
    ecg_file_list = []
    count = 0
    glob_result = glob.glob(search_dir + '/*ContactForce.txt')
    if glob_result:
        for i, name in enumerate(glob_result):
            if lim is None or (lim and i < lim):
                result = re.search('(.*)_P(.*)_ContactForce.txt', name)
                current_map = result.group(1).split('\\')[1]
                current_point = result.group(2)
                corresponding_ecg_file = search_dir + "\\{}_P{}_ECG_Export.txt".format(current_map, current_point)
                if glob.glob(corresponding_ecg_file):
                    contact_file_list.append(name)
                    ecg_file_list.append(corresponding_ecg_file)
                    count += 1
                else:
                    print("The corresponding ECG file not found for "+name)
    print("\n> {} ContactForce files with corresponding ECG files found (limit set to {})."
          .format(count, lim))
    return contact_file_list, ecg_file_list


def get_contact_data(filename, start=150, cols=[3, 4, 5]):
    # positive time values start after index 150
    # col 1 is obligatory for timing data, col 3 contains ForceValue
    file = open(filename, 'r')
    lines = file.readlines()
    read_data = False
    contact_data = np.empty((0, len(cols)), int)

    for i, line in enumerate(lines):
        if read_data:
            newline = np.fromstring(line, dtype=float, sep=' ')
            newline = np.take(newline, cols, 0)
            contact_data = np.append(contact_data, [newline], axis=0)
        if i == 7+start:
            read_data = True
        # inogda v faile ne 200, a 201 sampl!! poetomu limit na 50
        if i >= 7 + start + 50:
            break

    return np.transpose(contact_data)


def get_ecg_data(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    read_data = False
    channels = np.empty((0, 6), int)

    for i, line in enumerate(lines):

        d1 = "M1"
        d2 = "M2"
        d3 = "M3"
        d4 = "M4"
        d5 = "M1-M2"
        d6 = "M3-M4"

        if read_data:
            newline = np.fromstring(line, dtype=int, sep=' ')
            newline = [newline[d1_index], newline[d2_index], newline[d3_index], newline[d4_index], newline[d5_index], newline[d6_index]]
            channels = np.append(channels, [newline], axis=0)

        if i == 3:
            read_data = True
            channel_names = line.split()
            for i, c in enumerate(channel_names):
                result = re.search('(.*)\(.', c)
                channel_names[i] = result.group(1)
            d1_index = channel_names.index(d1)
            d2_index = channel_names.index(d2)
            d3_index = channel_names.index(d3)
            d4_index = channel_names.index(d4)
            d5_index = channel_names.index(d5)
            d6_index = channel_names.index(d6)

    return np.transpose(channels)


def get_study_data(contact_files, ecg_files):
    cf_array = np.empty((len(contact_files), 3, 50), float)
    ef_array = np.empty((len(ecg_files), 6, 2500), float)
    i = 0
    for cf, ef in zip(contact_files, ecg_files):
        print("reading "+cf)
        cf_array[i] = get_contact_data(cf)
        ef_array[i] = get_ecg_data(ef)
        i = i+1
    return cf_array, ef_array


if __name__ == '__main__':

    # 1. main arrays structure
    main_contact_array = np.empty((60000, 3, 50), float)
    main_ecg_array = np.empty((60000, 6, 2500), float)

    # 2. scan for target zip files
    zips = get_paths("F:/EPDATA")

    # 3. loop to unzip every file, get dir
    pass

    # 3a. search the dir for ContactForce data files and get lists
    contact_files, ecg_files = get_files('F:/EPDATA/Carto/test_patient/2021E120', lim=10)

    # 3b. process files and populate arrays
    contact_array, ecg_array = get_study_data(contact_files, ecg_files)

    # 3c. push to main array
    pass

    # 3d. delete unzipped dir, end loop cycle
    pass

    # 4. create files
    # np.save('cf_data', main_contact_array)
    # np.save('ecg_data', main_ecg_array)
