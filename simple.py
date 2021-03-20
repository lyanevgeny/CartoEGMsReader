import matplotlib.pyplot as plt
import numpy as np
import pywt


def get_channels(filename, channel_range=None, start=0, end=None):
    # returns the matrix of all channels and axillary info
    # within optional specified channel range and sample offset

    # the header data will be returned as a python dictionary with following structure
    header = {
        "file_name": filename,      # data added to returned header
        "channels": "",
        "sample_count": "",

        "file_type": "",   # original header data
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
                "channel_nr": 0,
                "label": "Empty channel",  # added to shift index in container array
                "range": None,             # for easier referencing
                "low": None,               # when specifying channel_range in this function
                "high": None,
                "sample_rate": None,
                "color": None,
                "scale": None,
            }
        ]
    }

    # convert to iterable tuple if range is a single number
    if isinstance(channel_range, int):
        channel_range = (channel_range,)

    # Open a file
    file = open(filename, 'r')
    lines = file.readlines()

    # Read the header
    separate_at, current_channel = 0, 0
    for i, line in enumerate(lines):
        if line.strip() == "[Data]":
            separate_at = i+1   # remember the index of the line where the ecg curve data starts
            break
        if line.strip() == "[Header]" or line.strip() == "":
            continue
        if line[:11] == "Data Format":
            header["data_format"] = line[12:].strip()
            continue
        if line[:17] == "Channels exported":
            all_channels = int(line[18:].strip())
            header["channels_exported"] = all_channels
            for a in range(all_channels):
                # empty dictionary for every exported channel
                header["channel_info"].append(dict(channel_nr=a+1, label=None, range=None, low=None, high=None, sample_rate=None, color=None, scale=None))
            continue
        if line[:9] == "Channel #":
            current_channel = int(line[10:].strip())
            if channel_range and current_channel not in channel_range:
                # do not populate dictionary if chanel is not in the specified range
                current_channel = -1
        else:
            subline = line.split(':', 1)
            var = subline[0].strip().lower().replace(" ", "_").replace(".", "")
            val = subline[1].strip().replace(".", "")
            try:
                val = int(val)
            except ValueError:
                # print("Can't convert " + val + " to int")
                pass
            if current_channel == 0:
                header[var] = val
            elif current_channel > 0:
                header["channel_info"][current_channel][var] = val

    if not end:  # use all samples if end is not specified
        end = header["samples_per_channel"]

    # additional data for returned header
    header["channels_returned"] = list(channel_range) if channel_range else list(range(1, header["channels_exported"]+1))
    header["sample_count"] = len(lines[separate_at + start:separate_at+end])

    # Search for ecg data
    channel_count = len(channel_range) if channel_range else header["channels_exported"]
    channels = np.empty((0, channel_count), int)  # initialize channel matrix only for specified channel range
    for i, line in enumerate(lines[separate_at+start:separate_at+end]):  # process only specified sample range
        # stripping the line into np 1-D array, but only the according to specified channel range with np.take()
        newline = np.take(np.fromstring(line, dtype=int, sep=','), channel_range if channel_range else range(header["channels_exported"]))
        # adding data of the current sample to channel matrix
        channels = np.append(channels, [newline], axis=0)

    # transpose channel matrix and return
    return channels.T, header


def plot_channels(channels, header):

    # examples of using the passed data
    ci = header["channel_info"]
    channels_returned = header["channels_returned"]  # returns a list
    channels_count = len(channels)
    samples_count = header["sample_count"]
    # label_of_channel_7 = header["channel_info"][7]["label"]
    # color_of_channel_18 = header["channel_info"][18]["color"]
    print(channels_returned, channels_count, samples_count)

    # Visualization of all channels
    fig = plt.figure()

    if len(channels) > 1:
        fig.suptitle("{} samples of {} channels in {}".format(samples_count, channels_count, header["file_name"]))
        gs = fig.add_gridspec(len(channels), hspace=0.7)
        axs = gs.subplots(sharex=True)
        for i, channel in enumerate(channels):
            # axs[i].plot (pywt.wavedec(channel, 'db4', level=7)[0])   # looks fine without Filter
            axs[i].plot(channel)
            axs[i].set_title(ci[channels_returned[i]]["label"], loc='left', y=0.7)
            # axs[i].get_xaxis ().set_visible (True)
            # axs[i].set_xticks ([])
            # axs[i].get_yaxis ().set_visible (False)
            axs[i].axis('off')
        # plt.grid(True)
    else:  # if only a single channel was passed
        fig.suptitle("{} samples of channel {} in {}".format(samples_count, ci[channels_returned[0]]["label"], header["file_name"]))
        axs = fig.add_subplot(1, 1, 1)
        axs.plot(channels[0])
        axs.set_title(ci[channels_returned[0]]["label"], loc='left', y=0.7)
        axs.axis('off')
    plt.show()


# custom range function
def r(start, end):
    return range(start, end+1)


def main():

    # get_channels() now has a versatile usage possibilities:
    # - optionally specify the range of channels as single integer / separate integers in a tuple / as custom ranges *r() / combinations
    # - optionally specify the sample range as start and/or end sample

    # channels, header = get_channels('ecg.txt', end=5000)
    # channels, header = get_channels('ecg.txt', 3, start=800, end=1400)
    channels, header = get_channels('ecg.txt', (1, 2, *r(6, 9), *r(18, 19)), start=5000, end=10000)

    # Output
    plot_channels(channels, header)


if __name__ == '__main__':
    main()
