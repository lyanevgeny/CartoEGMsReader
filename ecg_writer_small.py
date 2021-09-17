import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
import numpy as np
import re
from zipfile import ZipFile, is_zipfile
import os
from tqdm import tqdm


# opens a zip file and gets _ECG_Export.txt -files
def get_files_from_zip(zip_filename, limit = 3):
    """
    gets list of filenames from zip archive
    :param zip_filename: name of zip archive with data files
    :return: list of ecg files
    """
    ecg_file_list = []
    count = 0
    if is_zipfile(zip_filename):
        with ZipFile(zip_filename, 'r') as zipfile:
            # getting list of filenames in zip file
            filename_list = zipfile.namelist()

            # iteration though all files in zip archive
            for filename in filename_list:
                ecg_file = re.search('(.*)_ECG_Export.txt', filename)
                if ecg_file and count < limit:
                    ecg_file_list.append(ecg_file.string)
                    count = count + 1
    return ecg_file_list


# gets 12 lead data from file given channel names
def get_ecg_data_from_zip(zip_file, filename, ders):
    if filename in zip_file.namelist():
        lines = zip_file.read(filename).splitlines()
        derivations = {}  # make and populate a dictionary out of a tuple
        if type(ders) == tuple:
            for i, der in enumerate(ders):
                derivations["d" + str(i)] = der
            channels = np.empty((0, len(derivations)), int)
        elif type(ders) == str:  # if a single lead was passed
            derivations["d0"] = ders
            channels = np.empty((0, 1), int)
        indices = {}
        read_data = False
        for i, line in enumerate(lines):
            if read_data:  # get the data at indices
                newline = np.fromstring(line.decode('utf8'), dtype=int, sep=' ')
                channel_array = []
                for key in derivations:
                    channel_array.append(newline[indices["%s_index" % key]])
                channels = np.append(channels, [channel_array], axis=0)
            if i == 3:  # find columns with specified leads and save their index
                read_data = True
                channel_names = line.decode('utf8').split()
                for j, c in enumerate(channel_names):
                    result = re.search('(.*)\(.', c)
                    channel_names[j] = result.group(1)
                for k, d in enumerate(derivations):
                    indices["d%s_index" % k] = channel_names.index(derivations["d" + str(k)])
    return np.transpose(channels), ders, filename  # return ecg data, lead names and file name


# annotations
def draw_on_ecg(figure, speed):
    canvas = figure.add_subplot()

    # add voltage marker
    gx = 28
    gy = 603
    x = [gx, gx + 5, gx + 5, gx + 35, gx + 35, gx + 40]
    y = [gy, gy, gy - 28, gy - 28, gy, gy]
    line = Line2D(x, y, linewidth=1.5, linestyle='-', color='black')
    canvas.add_line(line)

    # add heart rate
    t1 = "84"
    t2 = "/min"
    canvas.text(0.85, 0.80, t1, size='35', transform=canvas.transAxes)
    canvas.text(0.89, 0.80, t2, size='19', transform=canvas.transAxes)

    # add bottom annotation line
    t3 = "GE   MAC1600          1.0.2           12SL v239" \
         "                                 {}mm/s    10 mm/mV" \
         "                                 0.16-20 Hz    1000 Hz                1/1".format(speed)
    canvas.text(0.085, 0.04, t3, size='19', transform=canvas.transAxes)


# plot ecg
def plot_data(ecg_data, speed=0, fixed=True, scale=500):
    img = plt.imread("ecg-paper-small.jpg")
    graph = plt.figure(constrained_layout=True, figsize=(24.5, 2.65), dpi=90)
    plt.imshow(img)
    plt.axis('off')
    axis = graph.add_axes([0, 0.15, 1, 0.7])
    if speed == 0:
        speed = int(250000/len(ecg_data[0][0]))
    axis.axis('off')
    axis.set_xmargin(0.1)
    if type(ecg_data[1]) == tuple:
        print("only a single lead is possible")
    elif type(ecg_data[1]) == str:  # if a single lead was passed
        axis.set_ylim(-scale, scale) if not fixed else True
        axis.plot(ecg_data[0][0][0:int(250000/speed)], 'k-', linewidth=1.7, clip_on=False)
        label = ecg_data[1]
        axis.annotate(label, (0, 50), size='22')
    draw_on_ecg(graph, speed)
    plt.savefig('output_{}.jpg'.format(ecg_data[2][:-4]), format='jpg')
    img = Image.open('output.jpg')
    img.show()


def get_data_from_zip(zip_filename, lead):
    ecg_files = get_files_from_zip(zip_filename)
    data_array = []
    if is_zipfile(zip_filename):
        with ZipFile(zip_filename, 'r') as zip_file:
            with tqdm(total=len(ecg_files), desc="Loading from {0}".format(os.path.basename(zip_filename)), ascii=False,
                      ncols=150, colour='green', leave=True) as pbar:
                for ecg_file in ecg_files:
                    pbar.update(1)
                    data_array.append(get_ecg_data_from_zip(zip_file, ecg_file, lead))
    return data_array


# Execute
data = get_data_from_zip('C:/Users/stans/Downloads/Export_2021E150-04_08_2021-14-49-19.zip', 'I')
for d in data:
    plot_data(d)
