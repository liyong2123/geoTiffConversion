import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
import earthpy.plot as ep

xaxis, ds = [], ""
# Finds the .nc file in directory
for root, dirs, files in os.walk(os.getcwd()):
    files.sort()
    for f in files:
        if f.endswith(".nc"):
            ds = f

# Uses netcdf4 library to open the file
fileOpen = netCDF4.Dataset(ds, "r")
# Gets the dimensions of data
lats, lons, depth2 = fileOpen.dimensions['x'], fileOpen.dimensions['y'], fileOpen.dimensions['Bands']

# Debug
print("Max x = " + str(lons.size - 1))
print("Max y = " + str(lats.size - 1))
print(depth2.size)
#

depth, arr1, xaxis, a = depth2.size, [], list(range(1, depth2.size)), 0
R, G, B = 29, 21, 16

arrmain = np.zeros(fileOpen.variables["Data"].shape)
arrtemp = fileOpen.variables["Data"]

# Apply transformation to the arrays so it's right orientation
for c in range(0, depth):
    arrmain[c] = np.fliplr(np.rot90(arrtemp[c, :, :], 2))

# Create new plot and insert data
fig, ax = plt.subplots(figsize=(6, 6))
# Uses the RGB bands, 29, 21, 16
ep.plot_rgb(arrmain, rgb=(29, 21, 16), ax=ax, title="HyperSpectral Image")


# Function event listenter, once detectede right click, will generat nwe graph
def onclick(event):
    if event.xdata is not None and event.ydata is not None and event.button == 3:
        # (x,y) from click
        y = int(event.xdata)
        x = int(event.ydata)

        arr2 = []
        print(depth)
        # Gets data from the click location (x,y) for all bands
        for b in range(1, depth):
            data = arrmain[b][x][y]
            arr2.append(data)

        # Creates new graph
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=xaxis, y=arr2, name="(" + str(x) + "," + str(y) + ")",
                                  line=dict(color='firebrick', width=2)))
        fig2.update_layout(title="Band Information for " + "(" + str(x) + "," + str(y) + ")",
                           xaxis_title='Band Number',
                           yaxis_title='Value')
        # displays graph onto web browser
        fig2.show()


# Adds event listener for right clicks
cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()
