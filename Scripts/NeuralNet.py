import matplotlib.pyplot as plt
import netCDF4
import os
import numpy as np
import plotly.graph_objects as go
import earthpy.plot as ep
from keras.models import Model
from Neuro2 import create_model

#main function
def learnmain():
    fs: str = ""
    #finds the netCDF file in directory
    for root, dirs, files in os.walk(os.getcwd()):
        files.sort()
        for f in files:
            if f.endswith(".nc"):
                fs = f
                
    # opens the netCDF file in "read" state       
    ds = netCDF4.Dataset(fs,"r")
    # gets the number of bands in the netcdf file
    input_features: int = ds.dimensions["Bands"].size
    # creates a model based on the number of bands
    model = create_model(input_features)

    model.load_weights("weights")

    #gets the array from netCDF file and rotates 180, and flips
    arrtemp = ds.variables["Data"][:]
    print(arrtemp.shape)
    arrmain = np.zeros(ds.variables["Data"].shape)
    # Apply transformation to the arrays so it's right orientation
    for c in range(0, input_features):
        arrmain[c] = np.fliplr(np.rot90(arrtemp[c, :, :], 2))

    # Create new plot and insert data
    fig, ax = plt.subplots(figsize=(6, 6))

    # Uses the RGB bands, 29, 21, 16
    ep.plot_rgb(arrmain, rgb=(29, 21, 16), ax=ax, title="HyperSpectral Image")
    fig.tight_layout()

    # Function event listenter, once detected right click, will generate new graph
    def onclick(event):
        if event.xdata is not None and event.ydata is not None and event.button == 3:
            # (x,y) from click
            y = int(event.xdata)
            x = int(event.ydata)
            #init array
            arr2 = []
            #Grabs array for (x,y) from the main array
            dataPred = arrmain[:, x, y]
            #
            dataPred = np.array([dataPred])
            pred = model.predict(dataPred)
            if pred[0][0]>.9:
                print("Water")
            elif pred[0][1]>.9:
                print("Land")
            else:
                print("No Data")
            #Gets data from the click location (x,y) for all bands
            for b in range(1, input_features):
                data = arrmain[b][x][y]
                arr2.append(data)

            #Creates new graph
            fig2 = go.Figure()
            xaxis = list(range(0,input_features))
            fig2.add_trace(go.Scatter(x=xaxis, y=arr2, name="(" + str(x) + "," + str(y) + ")",
                                    line=dict(color='firebrick', width=2)))
            fig2.update_layout(title="Band Information for " + "(" + str(x) + "," + str(y) + ")",
                            xaxis_title='Band Number',
                            yaxis_title='Value')
            #displays graph onto web browser
            #fig2.show()


    # Adds event listener for right clicks to main graph
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

if __name__ == "__main__":
    learnmain()