import netCDF4
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
lats, lons, depth2 = fileOpen.dimensions['x'], fileOpen.dimensions['y'], fileOpen.dimensions['Bands']

print("Max x = "+str(lons.size - 1))
print("Max y = "+str(lats.size - 1))
print(depth2.size)
depth, arr1, xaxis, a = depth2.size, [], list(range(1, depth2.size)), 0
R, G, B = 29, 21, 16

arrm = fileOpen.variables["Data"]
arr = np.array([np.fliplr(np.rot90(arrm[R, :, :], 2)), np.fliplr(np.rot90(arrm[G, :, :], 2)), np.fliplr(np.rot90(arrm
                [B, :, :], 2))])

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