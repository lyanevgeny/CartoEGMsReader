import glob
import re
import numpy as np
import os
from zipfile import ZipFile, is_zipfile
from matplotlib import pyplot as plt
from tqdm import tqdm
from numpy import ndarray
from tkinter import Tk
from tkinter import filedialog

CF_SAMPLES = 200
ECG_SAMPLES = 2500
Mapping_Channels = ['M1', 'M2', 'M3', 'M4', 'M1-M2', 'M3-M4']


def get_zip_files_paths(directory):
    """
    Searches in directory for zip files
    :param directory: directory for search
    :return: list of zip filenames
    """
    zip_files = glob.glob(directory + '/*.zip')
    return zip_files


def get_paths(epdata_dir):
    """
    searches for Carto folder, if finds returns the absolute paths of all zip files in subdirectories
    :param epdata_dir: folder to search in
    :return: the absolute paths of all zip files in subdirectories
    """
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


def clean_zip(zip_filename, clean_folder_name='/clean'):
    """
    searches for contact_force + corresponding ecg files
    creates new zip archive and copies found files pairwise into a '/clean subdirectory
    :param clean_folder_name: specify where to save cleaned zips
    :param zip_filename:
    :return: number of contact_force files found or 0 if file is already clean version
    """
    if not is_zipfile(zip_filename):
        print('File {} is corrupt!'.format(zip_filename))
        return 0
    with ZipFile(zip_filename, 'r') as zipfile:
        # checking for the file is already clean
        if re.search('_clean.zip', zip_filename):
            print('This is already cleaned file: ', zip_filename)
            return 0
        # Create target Directory if don't exist
        clean_dir_name = os.path.join(os.path.dirname(zip_filename), clean_folder_name)
        if not os.path.exists(clean_dir_name):
            os.mkdir(clean_dir_name)
            print("\n Directory ", clean_dir_name, " is created ")

        new_zip_filename = os.path.join(clean_dir_name, os.path.basename(zip_filename.replace('.zip', '_clean.zip')))
        new_zip = ZipFile(new_zip_filename, 'w')
        print('cleaned zip file name: ', os.path.basename(new_zip_filename))

        # getting list of filenames in zip file
        filename_list = zipfile.namelist()

        # initializing count of files/points
        contact_files_count = 0
        corresponding_ecg_files_count = 0
        ecg_files_count = 0

        # iteration though all files in zip archive
        with tqdm(total=len(filename_list), desc="Cleaning …", ascii=False, ncols=150) as pbar:
            for filename in filename_list:
                cf_file = re.search('(.*)_P(.*)_ContactForce.txt', filename)
                ecg_file = re.search('(.*)_P(.*)_ECG_Export.txt', filename)
                pbar.update(1)
                if ecg_file:
                    ecg_files_count += 1
                if cf_file:
                    contact_files_count += 1
                    # check for the ecg pair
                    for filename2 in filename_list:
                        ecg_filename = re.match(filename.replace('ContactForce.txt', '') + 'ECG_Export.txt', filename2)
                        if ecg_filename:
                            cf_data = zipfile.read(filename)
                            ecg_data = zipfile.read(filename2)
                            new_zip.writestr(zipfile.getinfo(filename), cf_data)
                            # print(zipfile.getinfo(filename))
                            new_zip.writestr(zipfile.getinfo(filename2), ecg_data)
                            # print(zipfile.getinfo(filename2))
                            corresponding_ecg_files_count += 1
        new_zip.close()

        print('\n', 'total contact points found = ', contact_files_count)
        print('total corresponding ecg files found = ', corresponding_ecg_files_count)
        print('total ecg files found = ', ecg_files_count)
    return contact_files_count


def get_files(search_dir, lim=None):
    """
    Directory version
    gets list of files from directory
    :param search_dir: name of directory with data files (unpacked zip archive)
    :param lim: limiting the number of files to iterate through
    :return: list of contact force files, list of corresponding ecg files
    """
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
                    print("The corresponding ECG file not found for " + name)
    print("\n> {} ContactForce files with corresponding ECG files found (limit set to {})."
          .format(count, lim))
    return contact_file_list, ecg_file_list


def get_files_from_zip(zip_filename):
    """
    Zip version
    gets list of filenames from zip archive
    :param zip_filename: name of zip archive with data files
    :return: list of contact force files, list of corresponding ecg files
    """
    contact_file_list = []
    ecg_file_list = []
    count = 0
    if is_zipfile(zip_filename):
        with ZipFile(zip_filename, 'r') as zipfile:
            # getting list of filenames in zip file
            filename_list = zipfile.namelist()

            # iteration though all files in zip archive
            for filename in filename_list:
                cf_file = re.search('(.*)_P(.*)_ContactForce.txt', filename)

                # if contact force file found, find the corresponding ecg file
                if cf_file:
                    current_map = cf_file.group(1)
                    current_point = cf_file.group(2)
                    corresponding_ecg_file = "{}_P{}_ECG_Export.txt".format(current_map, current_point)
                    if corresponding_ecg_file in filename_list:
                        contact_file_list.append(cf_file.string)
                        ecg_file_list.append(corresponding_ecg_file)
                        count += 1
                    else:
                        print("The corresponding ECG file not found for " + cf_file)
    else:
        print('File {} is corrupt!'.format(zip_filename))
    return contact_file_list, ecg_file_list


def get_contact_data(filename, start=150, cols=[3, 4, 5]):
    """
    Directory version
    :param filename: _ContactForce.txt file to get data from
    :param start: positive time values start after index 150
    :param cols: cols: col0 = Index, col1 = relative time, col2 = timestamp, col3 = ForceValue, col4 = AxialAngle,
            col5 = LateralAngle, col6 = MetalSeverity, col7 = InAccurateSeverity, col8 = NeedZeroing
    :return: Numpy array with shape = (len(cols), 50) if start=150
    """
    file = open(filename, 'r')
    lines = file.readlines()
    read_data = False
    contact_data = np.empty((0, len(cols)), int)

    for i, line in enumerate(lines):
        if read_data:
            newline = np.fromstring(line, dtype=float, sep=' ')
            newline = np.take(newline, cols, 0)
            contact_data = np.append(contact_data, [newline], axis=0)
        if i == 7 + start:
            read_data = True
        # inogda v faile ne 200, a 201 sampl!! poetomu limit na 50
        if i >= 7 + start + 50:
            break

    return np.transpose(contact_data)


def get_contact_data_from_zipped_txt(zip_file, cf_filename, start=150, cols=[3, 4, 5]):
    """
    Zip version
    iterates through the cf_file and collects contact force data
    :param zip_file: opened zip object
    :param cf_filename: name of the cf_file in zip archive
    :param start: positive time values start after index 150
    :param cols: col0 = Index, col1 = relative time, col2 = timestamp, col3 = ForceValue, col4 = AxialAngle,
            col5 = LateralAngle, col6 = MetalSeverity, col7 = InAccurateSeverity, col8 = NeedZeroing
    :return: Numpy array with shape = (len(cols), 50) if start=150
    """

    if cf_filename in zip_file.namelist():
        lines = zip_file.read(cf_filename).splitlines()
        read_data = False  # start read data skipping the headers
        contact_data = np.empty((0, len(cols)), int)

        for i, line in enumerate(lines):
            if read_data:
                newline = np.fromstring(line, dtype=float, sep='\t')
                newline = np.take(newline, cols, 0)
                contact_data = np.append(contact_data, [newline], axis=0)

            if i == 7 + start:
                read_data = True
            if i >= 7 + start + 50:  # if number of samples in file exceeds CF_SAMPLES
                break
    return contact_data.T


def get_ecg_data(filename):
    """
    Directory version
    iterates through the ecg file and collects ecg data
    searches for the names of the columns of the table
    and extracts data into numpy array
    :param filename: name of the ecg_file
    :return: Numpy array with shape = (len(Mapping_channels), 2500)
    """
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
            newline = [newline[d1_index], newline[d2_index], newline[d3_index], newline[d4_index], newline[d5_index],
                       newline[d6_index]]
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


def get_ecg_data_from_zipped_txt(zip_file, ecg_filename):
    """
    Zip version
    iterates through the ecg file and collects ecg data
    searches for the names of the columns of the table, corresponding to the Mapping_channel(global list) names
    and extracts data into numpy array
    :param zip_file: opened zip object
    :param ecg_filename: name of the ecg_file in zip archive
    :return: Numpy array with shape = (len(Mapping_channels), 2500)
    """
    if ecg_filename in zip_file.namelist():
        lines = zip_file.read(ecg_filename).splitlines()
        read_data = False  # start read data skipping the headers
        ecg_array: ndarray = np.empty((0, len(Mapping_Channels)), int)
        for i, line in enumerate(lines):
            # start to read from data field of the table
            if read_data:
                newline = np.fromstring(line, dtype=int, sep=' ')
                channel_data = np.take(newline, channel_indexes, axis=0)
                ecg_array = np.append(ecg_array, [channel_data], axis=0)

            # read headers of the table in ecg file
            if i == 3:
                read_data = True
                channel_indexes = []

                # get channel names from the headers of the table
                channel_names = line.decode('utf8').split()

                # get rid of channel numbers in channel names
                for channel_number, channel_name in enumerate(channel_names):
                    result = re.search('(.*)\(.', channel_name)
                    channel_names[channel_number] = result.group(1)

                # get indexes of those channels we need to extract from data
                # corresponding names defined in global Mapping_Channes
                for mapping_channel_name in Mapping_Channels:
                    channel_indexes.append(channel_names.index(mapping_channel_name))

    return ecg_array.T


def get_study_data(contact_files, ecg_files):
    """
    Directory version
    :param contact_files:
    :param ecg_files:
    :return: two Numpy arrays 1) contact data with the shape = (#of contact points in zip, len(cols), 50) if start=150
                              2) ecg data with the shape = (#of ecg points in zip, len(Mapping_channels, 2500)
    """
    cf_array = np.empty((len(contact_files), 3, 50), float)
    ef_array = np.empty((len(ecg_files), 6, 2500), float)
    i = 0

    for cf, ef in zip(contact_files, ecg_files):
        print("reading " + cf)
        cf_array[i] = get_contact_data(cf)
        ef_array[i] = get_ecg_data(ef)
        i = i + 1
    return cf_array, ef_array


def get_study_data_from_zip(zip_filename, cf_start=150, cf_cols=[3, 4, 5]):
    """
    Zip version
    iterates through zip archive and calls 1) get_contact_data_from_zipped_txt() on all contact force files
                                           2) get_ecg_data_from_zipped_txt on all ecg files
    :param zip_filename: zip archive name
    :param cf_start: positive time values start after index 150
    :param cf_cols: col0 = Index, col1 = relative time, col2 = timestamp, col3 = ForceValue, col4 = AxialAngle,
            col5 = LateralAngle, col6 = MetalSeverity, col7 = InAccurateSeverity, col8 = NeedZeroing
    :return: two Numpy arrays 1) contact data with the shape = (#of contact points in zip, len(cols), 50) if start=150
                              2) ecg data with the shape = (#of ecg points in zip, len(Mapping_channels, 2500)
    """

    cf_files, ecg_files = get_files_from_zip(zip_filename)
    if len(cf_files) != len(ecg_files):
        raise NameError('Number of CF and ECG points not equal!')
    cf_array = np.empty((0, len(cf_cols), CF_SAMPLES - cf_start), float)
    ecg_array = np.empty((0, len(Mapping_Channels), ECG_SAMPLES), float)

    if is_zipfile(zip_filename):
        with ZipFile(zip_filename, 'r') as zip_file:
            with tqdm(total=len(cf_files), desc="Loading from {0}".format(os.path.basename(zip_filename)), ascii=False,
                      ncols=150, colour='green', leave=True) as pbar:
                for cf_file, ecg_file in zip(cf_files, ecg_files):
                    new_cf_point = get_contact_data_from_zipped_txt(zip_file, cf_filename=cf_file, start=cf_start,
                                                                    cols=cf_cols)
                    cf_array = np.append(cf_array, [new_cf_point], axis=0)
                    pbar.update(1)

                    new_ecg_point = get_ecg_data_from_zipped_txt(zip_file, ecg_filename=ecg_file)
                    ecg_array = np.append(ecg_array, [new_ecg_point], axis=0)
    else:
        print('File {} is corrupt!'.format(zip_filename))
    return cf_array, ecg_array


def load_data(data_directory):
    """
    loads contact force and ecg data from .npy files in data_directory
    :param data_directory: name of directory with data
    :return: two Numpy arrays 1) contact data with the shape = (#of contact points in zip, len(cols), 50) if start=150
                              2) ecg data with the shape = (#of ecg points in zip, len(Mapping_channels, 2500)
    """
    npy_files = glob.glob(data_directory + '/*.npy')
    cf_array = np.empty((0, 3, CF_SAMPLES - 150), float)
    ecg_array = np.empty((0, len(Mapping_Channels), ECG_SAMPLES), float)
    with tqdm(total=len(npy_files), desc="Loading ...", ascii=False,
              ncols=150, colour='yellow', leave=True) as pbar:
        for npy in npy_files:
            pbar.update(1)
            cf = re.search('_cf_data.npy', npy)
            if cf:
                ecg_npy = npy.replace('_cf_data.npy', '_ecg_data.npy')
                if ecg_npy in npy_files:
                    cf_import = np.load(npy)
                    ecg_import = np.load(ecg_npy)
                    cf_array = np.append(cf_array, cf_import, axis=0)
                    ecg_array = np.append(ecg_array, ecg_import, axis=0)

    return cf_array, ecg_array


def ask_directory():
    root = Tk()
    root.withdraw()
    current_directory = filedialog.askdirectory()
    return current_directory


def plot_data(data, subtitle="", titles=None):
    channels_count = len(data)
    graph = plt.figure()
    if channels_count > 1:
        graph.suptitle(subtitle)
        gs = graph.add_gridspec(channels_count, hspace=0.7)
        axs = gs.subplots(sharex=True)
        for i, channel in enumerate(data):
            axs[i].plot(channel)
            if titles:
                axs[i].set_title(titles[i], loc='left', y=1)
    plt.show()


def plot_all_points(data, titles=None):
    """
    Plots all points from data block without pause
    :param data: numpy array with data
    :param titles:
    :return:
    """
    channels_count = data.shape[1]
    graph = plt.gcf()
    graph.show()
    graph.canvas.draw()
    for i, point in enumerate(data):

        if channels_count > 1:
            subtitle = str(i)
            graph.suptitle(subtitle)
            gs = graph.add_gridspec(channels_count, hspace=0.7)
            axs = gs.subplots(sharex=True)
            for i, channel in enumerate(point):
                axs[i].plot(channel)
                if titles:
                    axs[i].set_title(titles[i], loc='left', y=1)

        plt.pause(0.1)
        graph.canvas.draw()


def zip_to_npy(data_directory):
    zipfiles = get_zip_files_paths(data_directory)
    print('In ', data_directory, ' found ', len(zipfiles), ' .zip archives: ')
    for zipfile in zipfiles:
        print(os.path.basename(zipfile))
    zipfile_count = 0
    points_count = 0
    for zipfile in zipfiles:
        zipfile_count += 1
        cf_data, ecg_data = get_study_data_from_zip(zipfile)
        points_count += len(cf_data)
        cf_filename = os.path.join(data_directory, os.path.basename(
            zipfile.replace('.zip', '_' + str(zipfile_count) + '_cf_data.npy')))
        ecg_filename = os.path.join(data_directory, os.path.basename(
            zipfile.replace('.zip', '_' + str(zipfile_count) + '_ecg_data.npy')))
        np.save(cf_filename, cf_data)
        np.save(ecg_filename, ecg_data)

    print('Data processed from ', zipfile_count, ' files')
    print('Number of points: ', points_count)

    print('Data saved into ', data_directory + ' as cf_data.npy and ecg_data.npy')


def merge_npy(data_directory, filename_prefix='total'):
    """
    merges all npy files in two files
    :param data_directory: where all npy files are located
    :param filename_prefix: prefix for name of new files
    :return: number of points, final names of the files
    """
    cf_data, ecg_data = load_data(data_directory)
    cf_count = len(cf_data)
    ecg_count = len(ecg_data)
    cf_npy = os.path.join(data_directory, filename_prefix + cf_count + '_cf_data.npy')
    ecg_npy = os.path.join(data_directory, filename_prefix + ecg_count + '_ecg_data.npy')

    np.save(cf_npy, cf_data)
    np.save(ecg_npy, ecg_data)
    print("Contact force values for {0} points are saved into {1}".format(cf_count, cf_npy))
    print("Electrogramms for {0} points are saved into {1}".format(ecg_count, ecg_npy))

    return cf_count, ecg_count, cf_npy, ecg_npy


def plot_voltage_cf(cf_data, ecg_data):
    bipolar = 4
    x = np.mean(cf_data, axis=2).take(0, axis=1)
    x = np.maximum(x, 0)
    x = np.minimum(x, 60)
    y = np.max(ecg_data, axis=2).take(bipolar, axis=1)
    # y = np.minimum(y, 30)
    print(x.shape, y.shape)
    plt.scatter(x, y)
    plt.show()


if __name__ == '__main__':
    cf_filename = filedialog.askopenfilename(title="Open Contact Force data")
    cf_data = np.load(cf_filename)
    ecg_filename = filedialog.askopenfilename(title="Open Electrogramms")
    ecg_data = np.load(ecg_filename)
    print(cf_data.shape)
    print(ecg_data.shape)
    plot_all_points(ecg_data[:10])

    x = np.mean(cf_data, axis=2)[:, 0]
    print(x.shape)

    # Plot Distribution on Mean Force
    plt.hist(x, bins=1000)
    plt.gca().set(title='Frequency Histogram', ylabel='Frequency')
    plt.show()
