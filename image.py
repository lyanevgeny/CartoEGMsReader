import matplotlib.pyplot as plt
import numpy as np
import re


def get_ecg_data(filename, ders):
    file = open(filename, 'r')
    lines = file.readlines()
    derivations = {}
    for i, der in enumerate(ders):
        derivations["d"+str(i)] = der
    indices = {}
    channels = np.empty((0, len(derivations)), int)
    read_data = False
    for i, line in enumerate(lines):
        if read_data:
            newline = np.fromstring(line, dtype=int, sep=' ')
            channel_array = []
            for key in derivations:
                channel_array.append(newline[indices["%s_index" % key]])
            channels = np.append(channels, [channel_array], axis=0)
        if i == 3:
            read_data = True
            channel_names = line.split()
            for j, c in enumerate(channel_names):
                result = re.search('(.*)\(.', c)
                channel_names[j] = result.group(1)
            for k, d in enumerate(derivations):
                indices["d%s_index" % k] = channel_names.index(derivations["d" + str(k)])
    return np.transpose(channels), ders


def plot_data(data):
    img = plt.imread("hd-e.jpg")
    channels_count = len(data[0])
    graph = plt.figure(constrained_layout=True, figsize=(12, 8))
    plt.imshow(img)
    plt.axis('off')
    if channels_count > 1:
        '''
        cols = 2
        rows = 6
        widths = [3, 3]
        heights = [2, 2, 2, 2, 2, 2]
        '''
        cols = 1
        rows = 12
        widths = [1]
        heights = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

        spec = graph.add_gridspec(ncols=cols, nrows=rows, width_ratios=widths, height_ratios=heights)
        count = 0
        for col in range(cols):
            for row in range(rows):
                ax = graph.add_subplot(spec[row, col])
                ax.plot(data[0][count], 'k-', linewidth=0.5)
                label = data[1][count]
                ax.annotate(label, (1, 1), va='center')
                ax.axis('off')
                count = count + 1

    plt.savefig('foo.jpg', format='jpg')
    plt.show()


leads = ('I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')
data = get_ecg_data("data1/1-SR_P1_ECG_Export.txt", leads)
plot_data(data)
