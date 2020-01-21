import matplotlib.pyplot as plt
import seaborn as sns
import netCDF4
import os
import pandas as pd
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import earthpy.plot as ep
from keras.models import Model
from keras.regularizers import l2, l1
from keras.layers import Input, Dense, Dropout, Embedding, Flatten, Multiply, Concatenate, LeakyReLU
import tensorflow as tf



fs: str = ""
for root, dirs, files in os.walk(os.getcwd()):
    files.sort()
    for f in files:
        if f.endswith(".nc"):
            fs = f
            

ds = netCDF4.Dataset(fs,"r")
input_features = ds.dimensions["Bands"].size
in_ = Input((input_features,))
x = Dense(32, activation="relu", kernel_regularizer=l1(0.001))(in_)
x = Dropout(0.5)(x)
x = Dense(2, activation="softmax")(x)

model = Model(in_, x)

model.load_weights("weights")

arrtemp = ds.variables["Data"][:]
arrmain = np.zeros(ds.variables["Data"].shape)
# Apply transformation to the arrays so it's right orientation
for c in range(0, input_features):
    arrmain[c] = np.fliplr(np.rot90(arrtemp[c, :, :], 2))
print(np.max(arrmain[:, 650 ,850]))
# Create new plot and insert data
fig, ax = plt.subplots(figsize=(6, 6))
# Uses the RGB bands, 29, 21, 16
ep.plot_rgb(arrmain, rgb=(29, 21, 16), ax=ax, title="HyperSpectral Image")
fig.tight_layout()


# Function event listenter, once detected right click, will generat nwe graph
def onclick(event):
    if event.xdata is not None and event.ydata is not None and event.button == 3:
        # (x,y) from click
        y = int(event.xdata)
        x = int(event.ydata)

        arr2 = []
        dataPred = arrmain[:, x, y]
        dataPred = np.array([dataPred])
        pred = model.predict(dataPred)
        dataPred = 0
        if pred[0][0]>.9:
            print("Water")
        else:
            print("Land")
        # Gets data from the click location (x,y) for all bands
        for b in range(1, input_features):
            data = arrmain[b][x][y]
            arr2.append(data)

        # Creates new graph
        fig2 = go.Figure()
        xaxis = list(range(0,input_features))
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

