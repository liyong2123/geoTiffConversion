import os
import netCDF4
import numpy as np

ds = ""
for root, dirs, files in os.walk(os.getcwd()):
    files.sort()
    for f in files:
        if f.endswith(".nc"):
            ds = f

ds = netCDF4.Dataset(ds, "r")

filenew = netCDF4.Dataset("transposed.nc", "w")

science = ds.groups["science_data"]

arr = science.variables["sci_red"]

arr = np.transpose(arr, (1, 0, 2))

filenew.createDimension("Bands")

filenew.createDimension("X")
filenew.createDimension("Y")

red = filenew.createVariable("red_bands", "u2", ('Bands', "X", "Y"))
red[:, :, :] = arr[:, :, :]