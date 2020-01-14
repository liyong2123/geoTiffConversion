#import gdal
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import plotly.graph_objects as go
import os
#import earthpy as et
#import earthpy.spatial as es
import earthpy.plot as ep


xaxis =[]

ds = ""
for root, dirs, files in os.walk(os.getcwd()):
    files.sort()
    for f in files:
        if f.endswith(".nc"):
            ds = f

fileOpen = netCDF4.Dataset(ds, "r")

lats = fileOpen.dimensions['x']


lons = fileOpen.dimensions['y']import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
import earthpy.plot as ep

xaxis, ds = [], ""
for root, dirs, files in os.walk(os.getcwd()):
    files.sort()
    for f in files:
        if f.endswith(".nc"):
            ds = f

fileOpen = netCDF4.Dataset(ds, "r")
lats, lons, depth = fileOpen.dimensions['x'], fileOpen.dimensions['y'], fileOpen.dimensions['Bands']

print("Max x = "+str(lons.size - 1))
print("Max y = "+str(lats.size - 1))

depth, arr1, xaxis, a = depth.size, [], list(range(1, depth)), 0
R, G, B = 29, 21, 16

arrm = fileOpen.variables["Data"]
arr = np.array([arrm[R, :, :], arrm[G, :, :], arrm[B, :, :]])

fig, ax = plt.subplots(figsize=(6, 6))
ep.plot_rgb(arr, rgb=(0, 1, 2), ax=ax, title="HyperSpectral Image")


def onclick(event):
    if event.xdata is not None and event.ydata is not None and event.button == 3:
        y = int(event.xdata)
        x = int(event.ydata)

        arr2 = []
        print(depth)
        for b in range(1, depth):
            data = arrm[b][x][y]
            arr2.append(data)
        print("A")
        # plt.close()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=xaxis, y=arr2, name="("+str(x)+","+str(y)+")",
                       line=dict(color='firebrick', width=2)))
        fig2.update_layout(title="Band Information for " + "("+str(x)+","+str(y)+")",
                           xaxis_title='Band Number',
                           yaxis_title='Value')

        fig2.show()


cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()



depth = fileOpen.dimensions['Bands']


print("Max x = "+str(lons.size - 1))
print("Max y = "+str(lats.size - 1))

arr1 = []

depth = depth.size

arr = []

xaxis = list(range(1,depth))

#for i in range(1,depth):
 #   xaxis.append(i)

a = 0

#arr_st,meta = es.stack(arr1,nodata=-9999)

arrm = fileOpen.variables["Data"]

arr = np.array([arrm[29, :, :], arrm[21, :, :],arrm[16, :, :]])

fig, ax = plt.subplots(figsize=(6,6))

ep.plot_rgb(arr, rgb=(0, 1, 2), ax=ax, title="HyperSpectral Image")

def onclick(event):
    if event.xdata != None and event.ydata != None and event.button == 3:
        y = int(event.xdata)
        x = int(event.ydata)

        arrTemp = []
        for a in range (1,depth + 1):
            dataTemp = arrm[a]
            arrTemp.append(dataTemp)
        #plt.close()
        a = 1
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=xaxis, y=arrTemp, name="("+str(x)+","+str(y)+")",
                         line=dict(color='firebrick', width=2)))
        fig2.update_layout(title="Band Information for "+ "("+str(x)+","+str(y)+")",
                   xaxis_title='Band Number',
                   yaxis_title='Value')

        
        fig2.show()

cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()

