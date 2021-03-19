import matplotlib.pyplot as plt
import numpy as np
import pywt


def get_channels(filename):  # returns the matrix of all channels and axillary info

    # the header data will be returned as a python dictionary with following structure
    header = {
        "file_type": "",
        "version": "",
        "channels_exported": "",
        "samples_per_channel": "",
        "start_time": "",
        "end_time": "",
        "ch_info_pointer": "",
        "stamp_data": "",
        "mux_format": "",
        "mux_block_size": "",
        "data_format": "",
        "sample_rate": "",
        "channel_info": [
            {
                "channel_nr": "",
                "label": "",
                "range": "",
                "low": "",
                "high": "",
                "sample_rate": ""
            }
        ]
    }

    # Open a file
    file = open(filename, 'r')
    lines = file.readlines()

    # Read the header
    current_channel = 0
    for line in lines:
        if line.strip() == "[Data]":
            break
        if line.strip() == "[Header]" or line.strip() == "":
            continue
        if line[:11] == "Data Format":
            header["data_format"] = line[12:].strip()
            continue
        if line[:9] == "Channel #":
            current_channel = int(line[10:].strip())
            header["channel_info"].append(dict(channel_nr=current_channel, label="", range="", low="", high="", sample_rate=""))
        else:
            subline = line.split(':', 1)
            var = subline[0].strip().lower().replace(" ", "_").replace(".", "")
            val = subline[1].strip().replace(" ", "_").replace(".", "")
            try:
                val = int(val)
            except ValueError:
                # print("Can't convert " + val + " to int")
                pass
            if current_channel == 0:
                header[var] = val
            else:
                pass
                header["channel_info"][current_channel][var] = val

    number_of_channels = header["channels_exported"]

    # Search for ecg data
    count = False
    channels = np.empty((0, number_of_channels), int) # initialize channel matrix
    for i, line in enumerate(lines):
        if line.strip() == "[Data]":  # start processing after "[Data]" line
            count = True
            continue
        if count:
            # stripping the line (current sample for all channels), into np 1-D array
            newline = np.fromstring(line, dtype=int, sep=',')
            # adding data of the current sample to channel matrix
            channels = np.append(channels,[newline], axis=0)
            if i > 15000:
                break

    # transpose channel matrix and return
    return header, channels.T


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
        # axs[i].set_xticks ([])
        # axs[i].get_yaxis ().set_visible (False)
        axs[i].axis('off')

    # plt.grid(True)
    plt.show()


def main():

    header, channels = get_channels('ecg.txt')

    number_of_channels = header["channels_exported"]
    samples_per_channel = header["samples_per_channel"]
    label_of_channel_23 = header["channel_info"][23]["label"]
    color_of_channel_14 = header["channel_info"][14]["color"]

    print(number_of_channels, samples_per_channel, label_of_channel_23, color_of_channel_14)

    # Output
    plot_channels(channels)


if __name__ == '__main__':
    main()
