import matplotlib.pyplot as plt
import pywt

def get_channels(filename):
    # Open a file
    file = open ('ecg.txt', 'r')
    lines = file.readlines ()

    # Search for data
    count = False
    channels = []
    for line in lines:
        if line.strip () == "[Data]":  # start processing after "[Data]" line
            count = True
            continue
        if count:
            channels.append (line.split (',')[0])  # adding data of channel with index [1] to array

    return channels

def main():

    data = get_channels('ecg.txt')

    # Filter
    wavelets = pywt.wavedec (data, 'db4', level=3)
    print (len (wavelets))

    # Output
    plt.plot (wavelets[0])
    plt.show ()


if __name__ == '__main__':
    main()



