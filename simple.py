import matplotlib.pyplot as plt
import pywt

# Open a file
file = open('ecg.txt', 'r')
lines = file.readlines()

# Search for data
count = False
data = []
for line in lines:
    if line.strip() == "[Data]":  # start reading after "[Data]" line
        count = True
        continue
    if count:
        data.append(line.split(',')[1])  # adding to array data of second channel

# Filter
wavelets = pywt.wavedec(data, 'db4', level=3)

# Output
plt.plot(wavelets[0])
plt.show()
