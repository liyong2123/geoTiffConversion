import netCDF4
import sys
import os
import re
import numpy as np
import timeit
# Required Libraries:
# gdal
# conda
# nco


# Takes in standard Degrees, Minutes, Seconds coordinate format and
# converts it into Decimal coordinate format
def dms2dd(degrees: str, minutes: str, seconds: str, direction: str) -> float:
    dd: float = float(degrees) + float(minutes) / 60 + float(seconds) / 360
    if direction == "W" or direction == "S":
        dd *= -1
    return dd


# this will parse the Degrees, Minutes, Seconds coordinate format
# into its components and pass it into dms2dd to return decimal
# coordinates
def parse_dms(dms: str) -> float:
    # Parsing
    parts = re.split('[^\d\w]+', dms)
    lat = dms2dd(parts[0], parts[1], parts[2] + "." + parts[3], parts[4])
    return lat


def rid(stp: str) -> str:
    inx: int = stp.index("=")
    return stp[inx + 2:]


args: int = len(sys.argv) - 1
# Reads in flags in terminal --clean will remove all TIF after ns to save space
cleanFlag: int = 0
if args > 0:
    for a in range(1, args + 1):
        if sys.argv[a] == "--clean":
            cleanFlag = 1

# Issues Found during testing:
# Files larger than 2GB have issues with conversion due to netCDF's data
# type
# use --large to fix errors when compiling larger directories

fi: str = ""
arr: str = ""
meta: str = ""
depth: int = 0

# Goes through each files in directory in order and adds it to array
for root, dirs, files in os.walk(os.getcwd()):
    files.sort()
    for f in files:
        if f.endswith(".TIF"):
            depth = depth + 1
            if arr == "":
                arr = f
                fi = f
            else:
                arr = arr + " " + f
        elif f.endswith(".TXT"):
            meta = f
# Reads in metadata from .TXT file, if not found moves on

f: str = fi[:-13]
# If .TXT file was found, parse
if meta != "":
    openMetaFile = open(meta, "r")
    metaData: str = openMetaFile.read()
    splitted: str = metaData.split("\n")

    # goes through each line in metadata and tries to find keywords
    for lines in splitted:
        if "PRODUCT_LL_CORNER_LAT" in lines:
            LL_CORNER_LAT: str = lines
        elif "PRODUCT_LL_CORNER_LON" in lines:
            LL_CORNER_LON :str = lines
        elif "PRODUCT_UR_CORNER_LON" in lines:
            UR_CORNER_LON: str = lines
        elif "PRODUCT_UR_CORNER_LAT" in lines:
            UR_CORNER_LAT: str = lines
        elif "PRODUCT_LR_CORNER_LON" in lines:
            LR_CORNER_LON: str = lines
        elif "PRODUCT_LR_CORNER_LAT" in lines:
            LR_CORNER_LAT: str = lines
        elif "PRODUCT_UL_CORNER_LAT" in lines:
            UL_CORNER_LAT: str = lines
        elif "PRODUCT_UL_CORNER_LON" in lines:
            UL_CORNER_LON: str = lines
        elif "SENSOR_LOOK_ANGLE" in lines:
            sensorAngle: str = lines
        elif "SUN_AZIMUTH" in lines:
            sunAzimuth: str = lines
        elif "SUN_ELEVATION" in lines:
            sunelevation: str = lines
        elif "CORRECTIONS" in lines:
            endgroup: str = lines
    # gets rid of spaces in front
    UL_CORNER_LAT, UL_CORNER_LON = rid(UL_CORNER_LAT), rid(UL_CORNER_LON)
    UR_CORNER_LAT, UR_CORNER_LON = rid(UR_CORNER_LAT), rid(UR_CORNER_LON)
    LL_CORNER_LAT, LL_CORNER_LON = rid(LL_CORNER_LAT), rid(LL_CORNER_LON)
    LR_CORNER_LAT, LR_CORNER_LON = rid(LR_CORNER_LAT), rid(LR_CORNER_LON)
    sunelevation, sunAzimuth, endgroup = rid(sunelevation), rid(sunAzimuth), rid(endgroup)
    sensorAngle = sensorAngle[24:]

print("Linking:")
os.system("gdalbuildvrt -separate final.vrt %s" % arr)
print("Merging: ")


os.system("gdal_translate -of netcdf --config GDAL_CACHEMAX 500 final.vrt final.nc")

# Opens up the file and reads in dimensions
openfiled = netCDF4.Dataset("final.nc", "r")

xc = openfiled.dimensions["x"].size
yc = openfiled.dimensions["y"].size

print("Extracting:")
s: int = 0

arr = np.zeros((depth, openfiled.dimensions["y"].size, openfiled.dimensions["x"].size), dtype="u2")

# Create new file
nf = netCDF4.Dataset("%s.nc" % f, "w", format="NETCDF4")

print("0...", end="")
a: int = 0
while a <= (depth - 1):
    # prints current percentage done
    b: int = int(round(a * 100 / depth+5.1, -1))
    if b % 10 == 0 and b != s:
        s: int = b
        print("%s..." % str(b), end="", flush=True)
    # Gets all the bands and puts them into numpy array
    arr[a, :, :] = openfiled.variables["Band%s" % str(a + 1)][:]
    a = a + 1
    # This is for reorienting the array
    # arr[a, :, :] = np.fliplr(np.rot90(openfiled.variables["Band" + str(a)][:], 2))


# Debugging
print("Done loading data")
print("Number of Bands: %s" + str(depth), flush=True)
print("x: %s" % str(xc), flush=True)
print("y: %s" % str(yc), flush=True)
print("Array Size: %s" % str(arr.shape))
print("Adding Data:")

# if the directory had a .TXT file it will simply add the data from the file

print("0...", end="", flush=True)
# Creates new dimensions from opened .nc file data
depthDim = nf.createDimension('Bands', depth)
xlen = nf.createDimension("x", xc)
ylen = nf.createDimension("y", yc)

# Creates new variable for the data/array to bee store
data = nf.createVariable("Data", "u2", ('Bands', 'y', 'x'))
# Adds metadata for the Variable
data.long_name = 'Hyper-Spectral Bands'
data.standard_name = "3D Array With Bands, X, and Y"
data.grid_mapping = 'crs'
data.units = "Intensity"
data.set_auto_maskandscale(False)
# Adds Data
data[:, :, :] = arr[:, :, :]
nf.close()
# Adds metadata using ncatted
if meta != "":
    print("10...", end="", flush=True)
    try:
        print("20...", end="", flush=True)
        os.system(
            "ncatted -O -a Upper_Left_Corner,global,a,c," + "\"(" + UL_CORNER_LAT + "," + UL_CORNER_LON + ")\" " + f +
            ".nc " + f + ".nc")
        print("30...", end="", flush=True)
        os.system(
            "ncatted -O -a Upper_Right_Corner,global,a,c," + "\"(" + UR_CORNER_LAT + "," + UR_CORNER_LON + ")\" " + f +
            ".nc " + f + ".nc")
        print("40...", end="", flush=True)
        os.system(
            "ncatted -O -a Lower_Left_Corner,global,a,c," + "\"(" + LL_CORNER_LAT + "," + LL_CORNER_LON + ")\" " + f +
            ".nc " + f + ".nc")
        print("50...", end="", flush=True)
        os.system(
            "ncatted -O -a Lower_Right_Corner,global,a,c," + "\"(" + LR_CORNER_LAT + "," + LR_CORNER_LON + ")\" " + f +
            ".nc " + f + ".nc")
        print("60...", end="", flush=True)
        os.system("ncatted -O -a Sensor_Angle,global,a,f," + sensorAngle + " " + f + ".nc " + f + ".nc")
        print("70...", end="", flush=True)
        os.system("ncatted -O -a Sun_Azimuth,global,a,f," + sunAzimuth + " " + f + ".nc " + f + ".nc")
        print("80...", end="", flush=True)
        os.system("ncatted -O -a Sun_Elevation,global,a,f," + sunelevation + " " + f + ".nc " + f + ".nc")
        print("90...", end="", flush=True)
        os.system("ncatted -O -a End_Group,global,a,c," + endgroup + " " + f + ".nc " + f + ".nc")
        print("100", end="", flush=True)
    except ValueError:
        print("Undefined Values")
        os.system("")
    os.system("rm -f final.*")
    if cleanFlag == 1:
        os.system("rm -f *.TIF")
    print(" - done. :)")

# if not .txt exists, then opens geoTIFF and reads metadata then parses it
else:
    print("Metadata TXT not found, manually parsing from TIFF")
    for root, dirs, files in os.walk(os.getcwd()):
        dirs.sort()
        files.sort()
        for f in files:
            if f.endswith(".TIF"):
                metadata = os.popen("gdalinfo " + f).read()
                splitted = metadata.split("\n")

                UpperLeft, UpperRight, LowerLeft, LowerRight = "", "", "", ""
                for ind, lines in enumerate(splitted):
                    if "Upper Left" in lines:
                        UpperLeft = lines
                    elif "Upper Right" in lines:
                        UpperRight = lines
                    elif "Lower Left" in lines:
                        LowerLeft = lines
                    elif "Lower Right" in lines:
                        LowerRight = lines

                UpperLeft, UpperRight, LowerLeft, LowerRight = UpperLeft.replace('d', '°'),\
                    UpperRight.replace('d', '°'), LowerLeft.replace('d', '°'), LowerRight.replace('d', '°')

                # parses and translate dms coordinates into decimal coordinates
                UL_CORNER_LAT = parse_dms(UpperLeft[len(UpperLeft) - 29:len(UpperLeft) - 16])
                UL_CORNER_LON = parse_dms(UpperLeft[len(UpperLeft) - 14:len(UpperLeft) - 1])
                UR_CORNER_LAT = parse_dms(UpperRight[len(UpperRight) - 29:len(UpperRight) - 16])
                UR_CORNER_LON = parse_dms(UpperLeft[len(UpperLeft) - 14:len(UpperRight) - 1])
                LL_CORNER_LAT = parse_dms(LowerLeft[len(LowerLeft) - 29:len(LowerLeft) - 16])
                LL_CORNER_LON = parse_dms(LowerLeft[len(LowerLeft) - 14:len(LowerLeft) - 1])
                LR_CORNER_LAT = parse_dms(LowerRight[len(LowerRight) - 29:len(LowerRight) - 16])
                LR_CORNER_LON = parse_dms(LowerLeft[len(LowerLeft) - 14:len(LowerRight) - 1])

                UL_CORNER_LON, UL_CORNER_LAT, UR_CORNER_LON, UR_CORNER_LAT, LL_CORNER_LAT, LL_CORNER_LON, LR_CORNER_LAT\
                    , LR_CORNER_LON = str(UL_CORNER_LON), str(UL_CORNER_LAT), str(UR_CORNER_LON), str(UR_CORNER_LAT), \
                    str(LL_CORNER_LAT), str(LL_CORNER_LON), str(LR_CORNER_LAT), str(LR_CORNER_LON)

                os.system(
                    "ncatted -O -a Upper_Left_Corner,global,a,c," + "\"(" + UL_CORNER_LAT + "," + UL_CORNER_LON + ")\" "
                    "" + f[:-13] + ".nc " + f[:-13] + ".nc")
                os.system(
                    "ncatted -O -a Upper_Right_Corner,global,a,c," + "\"(" + UR_CORNER_LAT + "," + UR_CORNER_LON + ")\""
                    " " + f[:-13] + ".nc " + f[:-13] + ".nc")
                os.system(
                    "ncatted -O -a Lower_Left_Corner,global,a,c," + "\"(" + LL_CORNER_LAT + "," + LL_CORNER_LON + ")\""
                    " " + f[:-13] + ".nc " + f[:-13] + ".nc")
                os.system(
                    "ncatted -O -a Lower_Right_Corner,global,a,c," + "\"(" + LR_CORNER_LAT + "," + LR_CORNER_LON + ")\""
                    " " + f[:-13] + ".nc " + f[:-13] + ".nc")

                os.system("rm -f final.*")
                print("done.")

                if cleanFlag == 1:
                    os.system("rm -f *.TIF")
                exit()
