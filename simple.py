import matplotlib.pyplot as plt
import numpy as np
import pywt

def get_channels(filename):
    # returns the matrix of all channels and axillary info

    # Open a file
    file = open ('ecg.txt', 'r')
    lines = file.readlines ()
    number_of_channels = 28             # TODO write a code to infer number of channels and samples
    samples_per_channel = 60000         # TODO write a code to infer the labels for channels
    # Search for data
    count = False

    channels = np.empty((0,number_of_channels), int) # initialize channel matrix
    for i, line in enumerate(lines):
        if line.strip () == "[Data]":  # start processing after "[Data]" line
            count = True
            continue
        if count:
            # stripping the line (current sample for all channels), into np 1-D array
            newline = np.fromstring(line, dtype=int, sep=',')
            # adding data of the current sample to channel matrix
            channels = np.append(channels,[newline], axis=0)
            if i > 10000:
                break

    # transpose channel matrix and return
    return number_of_channels, samples_per_channel, channels.T

def plot_channels(channels):
    # Visualization of all channels
    fig = plt.figure ()
    gs = fig.add_gridspec (len(channels), hspace=0)
    axs = gs.subplots (sharex=True)
    fig.suptitle ('All channels:')
    for i, channel in enumerate(channels):
        # axs[i].plot (pywt.wavedec(channel, 'db4', level=7)[0])   - seems we don't need the Filter
        axs[i].plot (channel)                                       # looks fine without Filter

        # axs[i].set_title ("Channel #")
        # axs[i].get_xaxis ().set_visible (True)
        axs[i].get_yaxis ().set_visible (False)
    # plt.grid(True)
    plt.show()



def main():

    number_of_channels, samples_per_channel, raw_channels = get_channels('ecg.txt')

    # Output
    plot_channels(raw_channels)


if __name__ == '__main__':
    main()



