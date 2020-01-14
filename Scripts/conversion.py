import os
import netCDF4
import sys
import re
import numpy as np

# Required Libraries:
# gdal
# conda
# nco


# Takes in standard Degrees, Minutes, Seconds coordinate format and
# converts it into Decimal coordinate format
def dms2dd(degrees, minutes, seconds, direction):
    dd: float = float(degrees) + float(minutes)/60 + float(seconds)/360
    if direction == "W" or direction == "S":
        dd *= -1
    return dd


# this will parse the Degrees, Minutes, Seconds coordinate format
# into its components and pass it into dms2dd to return decimal
# coordinates
def parse_dms(dms):
    # Parsing
    parts = re.split('[^\d\w]+', dms)

    lat = dms2dd(parts[0], parts[1], parts[2] + "." + parts[3], parts[4])
    print(lat)
    return lat


args = len(sys.argv) - 1

# Reads in flags in terminal --clean will remove all TIF after ns to save space

largeFlag = 0
cleanFlag = 0
if args > 0:
    for a in range(1, args+1):
        if sys.argv[a] == "--large":
            largeFlag = 1
        elif sys.argv[a] == "--clean":
            cleanFlag = 1

            
# Issues Found during testing:
# Files larger than 2GB have issues with conversion due to netCDF's data
# type
# use --large to fix errors when compiling larger directories

fi = ""
arr = ""
meta = ""
depth: int = 0

# Goes through each files in directory in order and adds it to array
for root, dirs, files in os.walk(os.getcwd()):
    dirs.sort()
    files.sort()
    for f in files:
        if f.endswith(".TIF"):
            depth = depth + 1
            if arr == "":
                arr = f
                fi = f
            else:
                arr = arr+" " + f
        elif f.endswith(".TXT"):
            meta = f
# Reads in metadata from .TXT file, if not found mvoes on

f = fi[:-13]

UL_CORNER_LAT = ""
UL_CORNER_LON = ""
UR_CORNER_LON = ""
UR_CORNER_LAT = ""
LL_CORNER_LAT = ""
LL_CORNER_LON = ""
LR_CORNER_LON = ""
LR_CORNER_LAT = ""
sensorAngle = ""
sunAzimuth = ""
sunelevation = ""
endgroup = ""

if meta != "":
    openMetaFile = open(meta, "r")
    metaData = openMetaFile.read()
    splitted = metaData.split("\n")

    # init vars

    # goes through each line in metadata and trieds to find keywords
    for lines in splitted:
        if "PRODUCT_LL_CORNER_LAT" in lines:
            LL_CORNER_LAT = lines
        elif "PRODUCT_LL_CORNER_LON" in lines:
            LL_CORNER_LON = lines
        elif "PRODUCT_UR_CORNER_LON" in lines:
            UR_CORNER_LON = lines
        elif "PRODUCT_UR_CORNER_LAT" in lines:
            UR_CORNER_LAT = lines
        elif "PRODUCT_LR_CORNER_LON" in lines:
            LR_CORNER_LON = lines
        elif "PRODUCT_LR_CORNER_LAT" in lines:
            LR_CORNER_LAT = lines
        elif "PRODUCT_UL_CORNER_LAT" in lines:
            UL_CORNER_LAT = lines
        elif "PRODUCT_UL_CORNER_LON" in lines:
            UL_CORNER_LON = lines
        elif "SENSOR_LOOK_ANGLE" in lines:
            sensorAngle = lines
        elif "SUN_AZIMUTH" in lines:
            sunAzimuth = lines
        elif "SUN_ELEVATION" in lines:
            sunelevation = lines
        elif "CORRECTIONS" in lines:
            endgroup = lines

    while "=" in UL_CORNER_LAT:
        UL_CORNER_LAT = UL_CORNER_LAT[1:]
    UL_CORNER_LAT = UL_CORNER_LAT[1:]
    while "=" in UL_CORNER_LON:
        UL_CORNER_LON = UL_CORNER_LON[1:]
    UL_CORNER_LON = UL_CORNER_LON[1:]
    while "=" in UR_CORNER_LAT:
        UR_CORNER_LAT = UR_CORNER_LAT[1:]
    UR_CORNER_LAT = UR_CORNER_LAT[1:]
    while "=" in UR_CORNER_LON:
        UR_CORNER_LON = UR_CORNER_LON[1:]
    UR_CORNER_LON = UR_CORNER_LON[1:]
    while "=" in LL_CORNER_LAT:
        LL_CORNER_LAT = LL_CORNER_LAT[1:]
    LL_CORNER_LAT = LL_CORNER_LAT[1:]
    while "=" in LL_CORNER_LON:
        LL_CORNER_LON = LL_CORNER_LON[1:]
    LL_CORNER_LON = LL_CORNER_LON[1:]
    while "=" in LR_CORNER_LAT:
        LR_CORNER_LAT = LR_CORNER_LAT[1:]
    LR_CORNER_LAT = LR_CORNER_LAT[1:]
    while "=" in LR_CORNER_LON:
        LR_CORNER_LON = LR_CORNER_LON[1:]
    LR_CORNER_LON = LR_CORNER_LON[1:]
    while "=" in sunelevation:
        sunelevation = sunelevation[1:]
    sunelevation = sunelevation[1:]
    while "=" in sunAzimuth:
        sunAzimuth = sunAzimuth[1:]
    sunAzimuth = sunAzimuth[1:]
    while " " in endgroup:
        endgroup = endgroup[1:]
    endgroup = endgroup[1:]


    sensorAngle = sensorAngle[24:]

print("Linking:")

os.system("gdalbuildvrt -separate final.vrt " + arr)

print("Merging: ")


if largeFlag == 0:
    os.system("gdal_translate -of netcdf final.vrt final.nc")
else:
    os.system("gdal_translate -of -co FORMAT=NC2 final.vrt final.nc")
openfiled = netCDF4.Dataset("final.nc", "r")
arr = np.zeros((depth, openfiled.dimensions["y"].size, openfiled.dimensions["x"].size))

print("Extracting:")

nf = netCDF4.Dataset(f+".nc", "w")
for a in range(1, depth):
    # print(openfiled.variables["Band"+str(a)][300,200])
    if(int(a*100/depth) % 10) == 0 and a % 2 == 0:
        print(str(int(a*100/depth)) + "...", end="", flush=True)
    arr[a, :, :] = np.fliplr(np.rot90(openfiled.variables["Band"+str(a)][:], 2))
print("Done loading data")
print("Number of Bands: "+str(len(arr)), flush=True)
print("x: "+str(len(arr[0][0])), flush=True)
print("y: "+str(len(arr[0])), flush=True)
print(arr.shape)
print("Adding Data:")

# if the directory had a .TXT file it will simply add the data from the file
if meta != "":
    print("0...", end="", flush=True)
    depthDim = nf.createDimension('Bands', depth)
    xlen = nf.createDimension("x", len(arr[0][0]))
    ylen = nf.createDimension("y", len(arr[0]))

    data = nf.createVariable("Data", "short", ('Bands', 'y', 'x'))
    data.long_name = 'Intensity of Light in a given band and at a given x and y'
    data.standard_name = "3D Array With Bands, X, and Y"
    data.grid_mapping = 'crs'
    data.units = "Intensity"
    data.set_auto_maskandscale(False)

    data[:, :, :] = arr[:, :, :]

    print("10...", end="", flush=True)
    nf.close()
    try:
        print("20...", end="", flush=True)
        os.system("ncatted -O -a Upper_Left_Corner,global,a,c,"+"\"("+UL_CORNER_LAT+","+UL_CORNER_LON+")\" " + f +
                  ".nc " + f + ".nc")
        print("30...", end="", flush=True)
        os.system("ncatted -O -a Upper_Right_Corner,global,a,c,"+"\"("+UR_CORNER_LAT+","+UR_CORNER_LON+")\" " + f +
                  ".nc " + f + ".nc")
        print("40...", end="", flush=True)
        os.system("ncatted -O -a Lower_Left_Corner,global,a,c,"+"\"("+LL_CORNER_LAT+","+LL_CORNER_LON+")\" " + f +
                  ".nc " + f + ".nc")
        print("50...", end="", flush=True)
        os.system("ncatted -O -a Lower_Right_Corner,global,a,c,"+"\"("+LR_CORNER_LAT+","+LR_CORNER_LON+")\" " + f +
                  ".nc " + f + ".nc")
        print("60...", end="", flush=True)
        os.system("ncatted -O -a Sensor_Angle,global,a,f,"+sensorAngle+" " + f + ".nc " + f + ".nc")
        print("70...", end="", flush=True)
        os.system("ncatted -O -a Sun_Azimuth,global,a,f,"+sunAzimuth + " " + f + ".nc " + f + ".nc")
        print("80...", end="", flush=True)
        os.system("ncatted -O -a Sun_Elevation,global,a,f,"+sunelevation + " " + f + ".nc " + f + ".nc")
        print("90...", end="", flush=True)
        os.system("ncatted -O -a End_Group,global,a,c," + endgroup + " " + f + ".nc "+f + ".nc")
        print("100", end="", flush=True)
    except ValueError:
        print("Undefined Values")

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
                metadata = os.popen("gdalinfo "+f).read()
                splitted = metadata.split("\n")
                
                UpperLeft = ""
                UpperRight = ""
                LowerLeft = ""
                LowerRight = ""
                for ind, lines in enumerate(splitted):
                    if "Upper Left" in lines:
                        UpperLeft = lines
                        print(UpperLeft)
                    elif "Upper Right" in lines:
                        UpperRight = lines
                        print(UpperRight)
                    elif "Lower Left" in lines:
                        LowerLeft = lines
                        print(LowerLeft)
                    elif "Lower Right" in lines:
                        LowerRight = lines
                        print(LowerRight)
                UpperLeft = UpperLeft.replace('d', '°')
                UpperRight = UpperRight.replace('d', '°')
                LowerLeft = LowerLeft.replace('d', '°')
                LowerRight = LowerRight.replace('d', '°')
        
                # parses and translate dms coordinates into decimal coordinates
                UL_CORNER_LAT = parse_dms(UpperLeft[len(UpperLeft)-29:len(UpperLeft) - 16])
                UL_CORNER_LON = parse_dms(UpperLeft[len(UpperLeft)-14:len(UpperLeft)-1])
                UR_CORNER_LAT = parse_dms(UpperRight[len(UpperRight)-29:len(UpperRight) - 16])
                UR_CORNER_LON = parse_dms(UpperLeft[len(UpperLeft)-14:len(UpperRight)-1])
                LL_CORNER_LAT = parse_dms(LowerLeft[len(LowerLeft)-29:len(LowerLeft) - 16])
                LL_CORNER_LON = parse_dms(LowerLeft[len(LowerLeft)-14:len(LowerLeft)-1])
                LR_CORNER_LAT = parse_dms(LowerRight[len(LowerRight)-29:len(LowerRight) - 16])
                LR_CORNER_LON = parse_dms(LowerLeft[len(LowerLeft)-14:len(LowerRight)-1])
                UL_CORNER_LON = str(UL_CORNER_LON)
                UL_CORNER_LAT = str(UL_CORNER_LAT)
                UR_CORNER_LON = str(UR_CORNER_LON)
                UR_CORNER_LAT = str(UR_CORNER_LAT)
                LL_CORNER_LAT = str(LL_CORNER_LAT)
                LL_CORNER_LON = str(LL_CORNER_LON)
                LR_CORNER_LAT = str(LR_CORNER_LAT)
                LR_CORNER_LON = str(LR_CORNER_LON)
                
                os.system("ncatted -O -a Upper_Left_Corner,global,a,c,"+"\"("+UL_CORNER_LAT+","+UL_CORNER_LON+")\" " +
                          f + ".nc " + f + ".nc")
                os.system("ncatted -O -a Upper_Right_Corner,global,a,c,"+"\"("+UR_CORNER_LAT+","+UR_CORNER_LON+")\" " +
                          f + ".nc " + f + ".nc")
                os.system("ncatted -O -a Lower_Left_Corner,global,a,c,"+"\"("+LL_CORNER_LAT+","+LL_CORNER_LON+")\" " +
                          f + ".nc " + f + ".nc")
                os.system("ncatted -O -a Lower_Right_Corner,global,a,c,"+"\"("+LR_CORNER_LAT+","+LR_CORNER_LON+")\" " +
                          f + ".nc " + f + ".nc")
              
                print("done.")
                
                if cleanFlag == 1:
                    os.system("rm -f *.TIF")
                exit()
