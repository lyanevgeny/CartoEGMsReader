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
    for line in lines:
        if line.strip () == "[Data]":  # start processing after "[Data]" line
            count = True
            continue
        if count:
            # stripping the line (current sample for all channels), into np 1-D array
            newline = np.fromstring(line, dtype=int, sep=',')
            # adding data of the current sample to channel matrix
            channels = np.append(channels,[newline], axis=0)
    # transpose channel matrix and return
    return number_of_channels, samples_per_channel, channels.T

def main():

    number_of_channels, samples_per_channel, channels = get_channels('ecg.txt')
    print(channels.shape)

    # Filter
    wavelets = pywt.wavedec (channels[0], 'db4', level=3)


    # Output
    plt.plot (wavelets[0])
    plt.show ()


if __name__ == '__main__':
    main()



