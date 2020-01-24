import netCDF4
import os
from scipy.integrate import simps
from pylab import text
import numpy as np
import matplotlib.pyplot as plt
# from matplotlib import colors
import plotly.graph_objects as go
import earthpy.plot as ep
import json
#Finds the netcdf file in the directory.
ds = ""
for root, dirs, files in os.walk(os.getcwd()):
    files.sort()
    for f in files:
        if f.endswith(".nc"):
            ds = f
#Once found, will open it with netCDF library under read mode
fileopen = netCDF4.Dataset(ds, "r")
#Finds the group for data
science = fileopen.groups["science_data"]
#Opens variables for red and blue bands
arr_blue = science.variables["sci_blue"]
arr = science.variables["sci_red"]
#transforms the lists into np arrays for better library functions
arr = np.array(arr)
#Transposes array, from (X, Band, Y) to (Band, X, Y)
arr = arr.transpose(1, 0, 2)
arr_blue =np.array(arr_blue)
arr_blue = arr_blue.transpose(1, 0, 2)

#Plot tool used for debugging and viewing data
fig, ax = plt.subplots(figsize=(6, 6))
ep.plot_bands(arr[10], cmap="Spectral", ax=ax)

#Varaible Initialization
xaxis = list(range(0, fileopen.dimensions["red_bands"].size))
bmean = []
bstd = []
bmin = []
bmax = []
brange = []
mean = []
std = []
mini = []
maxi = []
rrange = []

#Goes through each red band, and computes the values  for each measure, then adds it to array.
for a in range(0, fileopen.dimensions["red_bands"].size):
    mean.append(np.mean(arr[a]))
    std.append(np.std(arr[a]))
    mini.append(np.min(arr[a]))
    maxi.append(np.max(arr[a]))
    rrange.append(maxi[a] - mini[a])

for b in range(0, fileopen.dimensions["blue_bands"].size):
    bmean.append(np.mean(arr_blue[b]))
    bstd.append(np.std(arr_blue[b]))
    bmin.append(np.min(arr_blue[b]))
    bmax.append(np.max(arr_blue[b]))
    brange.append(bmax[b] - bmin[b])

#Makes new file, and then writes to it in csv format
band_red = open("band_info.csv", "w+")
band_red.write("Band,Mean,STD,Min,Max,Range\n")

#Writes all data, one  row for each band, and one column for each metrics
for c in range(0, fileopen.dimensions["blue_bands"].size):
    band_red.write("R%s,%s,%s,%s,%s,%s\n"
          % (str(c + 1), str(mean[c]), str(std[c]), str(mini[c]), str(maxi[c]), str(rrange[c])))

for d in range(0, fileopen.dimensions["red_bands"].size):
    band_red.write("B%s,%s,%s,%s,%s,%s\n"
          % (str(d + 1), str(bmean[d]), str(bstd[d]), str(bmin[d]), str(bmax[d]), str(brange[d])))


band_red.close()

#Plot for viewing data, uncomment to turn on.
fig3 = go.Figure()

fig3.add_trace(go.Scatter(x=xaxis, y=mean, name="Mean",
                                  line=dict(color='firebrick', width=2)))
fig3.update_layout(title="Band Information for " + "Mean",
                           xaxis_title='Band Number',
                           yaxis_title='Mean')

# fig3.show()

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=xaxis, y=std, name="Standard Deviation",
                                  line=dict(color='firebrick', width=2)))
fig4.update_layout(title="Band Information for " + "Standard Deviation",
                           xaxis_title='Band Number',
                           yaxis_title='Mean')

# fig4.show()


def onclick(event):
    global xaxis
    if event.xdata is not None and event.ydata is not None and event.button == 3:
        y = int(event.xdata)
        x = int(event.ydata)
        arrTemp = []
        for a in range(0, fileopen.dimensions["red_bands"].size):
            dataTemp = arr[a, x, y]
            arrTemp.append(dataTemp)
        # plt.close()
        a = 1
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=xaxis, y=arrTemp, name="(" + str(x) + "," + str(y) + ")",
                                  line=dict(color='firebrick', width=2)))
        fig2.update_layout(title="Band Information for " + "(" + str(x) + "," + str(y) + ")",
                           xaxis_title='Band Number',
                           yaxis_title='Value')

        fig2.show()


fig.canvas.mpl_connect('button_press_event', onclick)
# plt.show()


