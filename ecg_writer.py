import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import re


# gets 12 lead data from file given channel names
def get_ecg_data(filename, ders):
    file = open(filename, 'r')
    lines = file.readlines()
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
            newline = np.fromstring(line, dtype=int, sep=' ')
            channel_array = []
            for key in derivations:
                channel_array.append(newline[indices["%s_index" % key]])
            channels = np.append(channels, [channel_array], axis=0)
        if i == 3:  # find columns with specified leads and save their index
            read_data = True
            channel_names = line.split()
            for j, c in enumerate(channel_names):
                result = re.search('(.*)\(.', c)
                channel_names[j] = result.group(1)
            for k, d in enumerate(derivations):
                indices["d%s_index" % k] = channel_names.index(derivations["d" + str(k)])

    return np.transpose(channels), ders  # return ecg data and lead names


# adds 7,5 seconds of invisible line or multiplies data
def make_longer(array, multiply):
    new = np.empty((0, 10000))
    for i, a in enumerate(array[0]):
        if multiply:
            dummy_array = np.concatenate((a, a, a, a))
            new = np.append(new, [dummy_array], axis=0)
        else:
            empty_array = np.zeros(7500)
            empty_array[:7499] = np.nan  # to hide the last part of plot
            new_array = np.concatenate((a, empty_array))
            new = np.append(new, [new_array], axis=0)
    return new, array[1]


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
    canvas.text(0.92, 0.95, t1, size='35', transform=canvas.transAxes)
    canvas.text(0.95, 0.95, t2, size='19', transform=canvas.transAxes)

    # add bottom annotation line
    t3 = "GE   MAC1600          1.0.2           12SL v239" \
         "                                 {}mm/s    10 mm/mV" \
         "                                 0.16-20 Hz    1000 Hz                              1/1".format(speed)
    canvas.text(0.085, 0.03, t3, size='19', transform=canvas.transAxes)

    # add black rectangle marker
    rect = patches.Rectangle((43, 638), 25, 28, linewidth=0.1, edgecolor='black', facecolor='black')
    canvas.add_patch(rect)


# plot ecg
def plot_data(ecg_data, speed=0, fixed=True, scale=500):
    img = plt.imread("ecg-paper.jpg")
    graph = plt.figure(constrained_layout=True, figsize=(24.5, 17.4), dpi=90)
    plt.imshow(img)
    plt.axis('off')
    spec = graph.add_gridspec(14, hspace=0)
    axs = spec.subplots(sharex=True, sharey=True)
    if speed == 0:
        speed = int(250000/len(ecg_data[0][0]))
    for i in range(14):  # for all subplots
        axs[i].axis('off')
        axs[i].set_xmargin(0.1)
    if type(ecg_data[1]) == tuple:
        for i, d in enumerate(ecg_data[0]):
            axs[i + 1].set_ylim(-scale, scale) if not fixed else True
            axs[i + 1].plot(d[:int(250000/speed)], 'k-', linewidth=1.7, clip_on=False)
            label = ecg_data[1][i]
            axs[i + 1].annotate(label, (0, 320), size='22')
    elif type(ecg_data[1]) == str:  # if a single lead was passed
        print("here")
        axs[6].set_ylim(-scale, scale) if not fixed else True
        axs[6].plot(ecg_data[0][0][0:int(250000/speed)], 'k-', linewidth=1.7, clip_on=False)
        label = ecg_data[1]
        axs[6].annotate(label, (0, 500), size='22')
    draw_on_ecg(graph, speed)
    plt.savefig('output.jpg', format='jpg')
    img = Image.open('output.jpg')
    img.show()


#####################
# Exec instructions #
#####################

# 1. Specify leads by their names in Carto-file
leads = 'I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'

# 2. Create data array from Carto-file using lead parameter, set multiply to 10 seconds or (pseudo)crop with true/false
data = get_ecg_data("data1/1-SR_P1_ECG_Export.txt", leads)
data2 = get_ecg_data("data1/1-SR_P1181_ECG_Export.txt", 'CS6')

# 3. Plot, optionally with:
# - make_longer(multiply) function to multiply tracing to 10 seconds or (pseuro)crop
# Experimental functions:
# - speed argument to make tracing proportional to paper speed
# - fixed argument that makes spacing between leads even, but voltage goes down (must fix it later)
# - scale argument to specify maximal y scale (works only if fixed = False; future update to adjust to paper scale required)

# Example of rhythm strip
plot_data(make_longer(data, True), speed=50, fixed=False)

# Example of single lead
plot_data(data2, fixed=False, scale=500)
