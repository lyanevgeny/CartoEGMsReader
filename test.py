import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.simpledialog as tks
import tkinter.filedialog as tfd
import tkinter.messagebox as tms

SAMPLES_COUNT = 10000

window = tk.Tk()
window.title("ecgreader")
window.geometry("800x700")
window.resizable(False, True)
filename = ""


channel_names = []

def open_file():
    global filename
    filename = tfd.askopenfilename()
    label2["text"] = get_filename(filename)
    #label2["text"] = filename

def get_filename(filepath):
    pos = 0
    for i, char in enumerate(filepath):
        if char == "/":
            pos = i
    return filepath[pos+1:len(filepath)]

def get_dataEP(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    data = False
    channel_count = 28
    channels = np.empty((0, channel_count), int)
    for i, line in enumerate(lines):
        if data and (i-start) < SAMPLES_COUNT:
            newline = np.fromstring(line, dtype=int, sep=',')
            channels = np.append(channels, [newline], axis=0)

        if line.strip() == "[Data]":
            start = i
            data = True
    return np.transpose(channels)

def get_dataCarto(filename):
    global channel_names
    file = open(filename, 'r')
    lines = file.readlines()
    data = False
    channel_count = 79
    channels = np.empty((0, channel_count), int)
    for i, line in enumerate(lines):
        if data and (i-start) <= SAMPLES_COUNT:
            newline = np.fromstring(line, dtype=int, sep=' ')
            channels = np.append(channels, [newline], axis=0)

        if i == 3:
            start = i
            data = True
            channel_names = line.split()
    return np.transpose(channels)

def plot_data(data):
    global channel_names
    channels_count = len(data)
    graph = plt.figure()
    if channels_count > 1:
        graph.suptitle("{} samples of {} channels in {}".format(SAMPLES_COUNT, channels_count, filename))
        gs = graph.add_gridspec(channels_count, hspace=0.7)
        axs = gs.subplots(sharex=True)
        for i, channel in enumerate(data):
            # axs[i].plot (pywt.wavedec(channel, 'db4', level=7)[0])   # looks fine without Filter
            axs[i].plot(channel)
            axs[i].set_title(channel_names[i], loc='left', y=-1)
            # axs[i].get_xaxis ().set_visible (True)
            # axs[i].set_xticks ([])
            # axs[i].get_yaxis ().set_visible (False)
            axs[i].axis('off')
    plt.show()

def main():
    global filename, option
    if filename:
        option = tks.askstring(title="Type of System",
                                          prompt="1: EP, 2: Carto")
        if option == "1":
            data = get_dataEP(filename)
            plot_data(data)
        if option == "2":
            data = get_dataCarto(filename)
            print(data)
            plot_data(data)
    else:
        tms.showerror(title="ERROR", message= "Please choose the file first")

openfileicon = tk.PhotoImage(file="open_file.gif")
filebutton = tk.Button(window, image=openfileicon, command=open_file)
filebutton.place(x=350, y=80)
label1 = tk.Label(window, text="File Chosen:", font=("Arial", 15))
label1.place(x=130, y=30)
label2 = tk.Label(window, text="None", font=("Arial", 15))
label2.place(x=90, y=80)
renamebutton = tk.Button(window, text="Plot Data", font=("Arial", 15), command=main)
renamebutton.place(x=550, y=50)

window.mainloop()
# 1 EP  2 Carto