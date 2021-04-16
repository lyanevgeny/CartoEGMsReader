import glob
import re
import numpy as np
import matplotlib.pyplot as plt


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
    print("{} ContactForce files with corresponding ECG files found, limit to {}."
          .format(len(glob_result), lim))
    return contact_file_list, ecg_file_list


def get_contact_data(filename, start=150):  # positive time values start after index 150
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

    return np.transpose(contact_data[start:])


def get_ecg_data(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    read_data = False
    channels = np.empty((0, 3), int)

    for i, line in enumerate(lines):

        if read_data:
            newline = np.fromstring(line, dtype=int, sep=' ')
            newline = [newline[uni_index], newline[bi_index], newline[ref_index]]
            channels = np.append(channels, [newline], axis=0)

        if i == 2:
            result = re.search(
                'Unipolar Mapping Channel=(.*) Bipolar Mapping Channel=(.*) Reference Channel=(.*)', line)
            if result:
                uni_map_ch = result.group(1)
                bi_map_ch = result.group(2)
                ref_ch = result.group(3)
                print("In '{}': UNI->{}, BI->{}, REF->{}.".format(filename, uni_map_ch, bi_map_ch, ref_ch))

        if i == 3:
            read_data = True
            channel_names = line.split()
            for i, c in enumerate(channel_names):
                result = re.search('(.*)\(.', c)
                channel_names[i] = result.group(1)
            uni_index = channel_names.index(uni_map_ch)
            bi_index = channel_names.index(bi_map_ch)
            ref_index = channel_names.index(ref_ch)

    return channels


def plot_data(data, suptitle="", titles=None):
    channels_count = len(data)
    graph = plt.figure()
    if channels_count > 1:
        graph.suptitle(suptitle)
        gs = graph.add_gridspec(channels_count, hspace=0.7)
        axs = gs.subplots(sharex=True)
        for i, channel in enumerate(data):
            axs[i].plot(channel)
            if titles:
                axs[i].set_title(titles[i], loc='left', y=1)
    plt.show()


def process_files(contact_data_file, ecg_data_file, mode="merge"):

    if mode == "merge":  # merge Contact Force and ECG data according to "Time" column in ContactForce file
        cf_array = get_contact_data(contact_data_file)
        ecg_array = get_ecg_data(ecg_data_file)

        time_array = cf_array[1].astype(int)
        time_array = time_array[time_array >= 0]

        ecg_array = np.transpose(ecg_array[time_array])

        cf_interest = [3]
        cf_array = np.transpose(cf_array[cf_interest])
        cf_array = np.transpose(cf_array)

        merged_array = np.append(cf_array, ecg_array, axis=0)
        return merged_array

    if mode == "mean":
        cf_array = get_contact_data(contact_data_file)
        return np.mean(cf_array[3])


if __name__ == '__main__':

    # 1. specify directory with Carto files
    folder = 'data1'

    # 2. search there for ContactForce data files and get lists
    #    with ContactForce and corresponding ECG files
    #    set limit for faster processing
    contact_files, ecg_files = get_files(folder, lim=1)

    # 3. process files
    for cf, ef in zip(contact_files, ecg_files):

        # plot merged data from both files
        merged_data = process_files(cf, ef, mode="merge")
        plot_data(merged_data,
                  suptitle="Merged data from {}".format(cf[:16]),
                  titles=["ContactForce", "Unipolar", "Bipolar", "Reference"])

        # get mean of ForceValue
        mean = process_files(cf, ef, mode="mean")
        print("In '{}': mean of ForceValue in is {}.".format(cf, mean))
