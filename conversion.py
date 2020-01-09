import os
import netCDF4
import sys
import re

#Required Libraries:
#gdal
#conda
#nco

#Takes in standard Degrees, Minutes, Seconds coordinate format and
#converts it into Decimal coordinate format
def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(360)
    print(direction)
    if(direction == "W" or direction == "S"):
        dd*=-1
    return dd

#this will parse the Degrees, Minutes, Seconds coordinate format
#into its components and pass it into dms2dd to return decimal
#coordinates
def parse_dms(dms):
    #Parsing
    parts = re.split('[^\d\w]+', dms)

    lat = dms2dd(parts[0],parts[1],parts[2]+"."+parts[3],parts[4])
    print(lat)
    return lat

args = len(sys.argv) - 1

#Reads in flags in terminal --clean will remove all TIF after ns to save space

largeFlag = 0
cleanFlag = 0
if(args>0):
    for a in range(1,args+1):
        if(sys.argv[a] == "--large"):
            largeFlag = 1
        elif(sys.argv[a] == "--clean"):
            cleanFlag = 1

            
#Issues Found during testing:
#Files larger than 2GB have issues with conversion due to netCDF's data
#type
#use --large to fix errors when compiling larger directories

arr = ""
meta = ""
depth = 0
#Goes through each files in directory in order and adds it to array
for root, dirs, files in os.walk(os.getcwd()):
    dirs.sort()
    files.sort()
    for f in files:
        if f.endswith(".TIF"):
            depth = depth + 1
            if arr is "":
                arr = f
            else:
                arr = arr+" "+ f
        elif f.endswith(".TXT"):
            meta = f
#Reads in metadata from .TXT file, if not found mvoes on
if(meta is not ""):
    openMetaFile = open(meta,"r")
    metaData = openMetaFile.read()
    splitted = metaData.split("\n")

    #init vars
    UL_CORNER_LAT = ""
    UL_CORNER_LON = "" 
    UR_CORNER_LON = ""
    UR_CORNER_LAT = ""
    LL_CORNER_LAT = ""
    LL_CORNER_LON = ""
    LR_CORNER_LON = ""
    LR_CORNER_LAT = ""
    sensorAngle = ""

    #goes through each line in metadata and trieds to find keywords
    for lines in splitted:
        if("PRODUCT_LL_CORNER_LAT" in lines):
            LL_CORNER_LAT = lines
        elif("PRODUCT_LL_CORNER_LON" in lines):
            LL_CORNER_LON = lines
        elif("PRODUCT_UR_CORNER_LON" in lines):
            UR_CORNER_LON = lines
        elif("PRODUCT_UR_CORNER_LAT" in lines):
            UR_CORNER_LAT = lines
        elif("PRODUCT_LR_CORNER_LON" in lines):
            LR_CORNER_LON = lines
        elif("PRODUCT_LR_CORNER_LAT" in lines):
            LR_CORNER_LAT = lines
        elif("PRODUCT_UL_CORNER_LAT" in lines):
            UL_CORNER_LAT = lines
        elif("PRODUCT_UL_CORNER_LON" in lines):
            UL_CORNER_LON = lines
        elif("SENSOR_LOOK_ANGLE" in lines):
            sensorAngle = lines
    #removes the front, only take the data
    #UL_CORNER_LAT = UL_CORNER_LAT[26:]
    #UL_CORNER_LON = UL_CORNER_LON[26:]
    #UR_CORNER_LON = UR_CORNER_LON[26:]
    #UR_CORNER_LAT = UR_CORNER_LAT[26:]
    #LL_CORNER_LAT = LL_CORNER_LAT[26:]
    #LL_CORNER_LON = LL_CORNER_LON[26:]
    #LR_CORNER_LON = LR_CORNER_LON[26:]
    #LR_CORNER_LAT = LR_CORNER_LAT[26:]
    while("=" in UL_CORNER_LAT or " "in UL_CORNER_LAT):
        UL_CORNER_LAT = UL_CORNER_LAT[1:]
    while("=" in UL_CORNER_LON or " "in UL_CORNER_LON):
        UL_CORNER_LON = UL_CORNER_LON[1:]
    while("=" in UR_CORNER_LAT or " "in UR_CORNER_LAT):
        UR_CORNER_LAT = UR_CORNER_LAT[1:]
    while("=" in UR_CORNER_LON or " "in UR_CORNER_LON):
        UR_CORNER_LON = UR_CORNER_LON[1:]
    while("=" in LL_CORNER_LAT or " "in LL_CORNER_LAT):
        LL_CORNER_LAT = LL_CORNER_LAT[1:]
    while("=" in LL_CORNER_LON or " "in LL_CORNER_LON):
        LL_CORNER_LON = LL_CORNER_LON[1:]
    while("=" in LR_CORNER_LAT or " "in LR_CORNER_LAT):
        LR_CORNER_LAT = LR_CORNER_LAT[1:]
    while("=" in LR_CORNER_LON or " "in UL_CORNER_LON):
        LR_CORNER_LON = LR_CORNER_LON[1:]
    
    sensorAngle = sensorAngle[24:]

os.system("gdalbuildvrt -separate final.vrt "+arr)
print("Merging: ")

if(largeFlag == 0):
    os.system("gdal_translate -of netcdf final.vrt final.nc")
else:
    os.system("gdal_translate -of -co FORMAT=NC2 final.vrt final.nc")
    
print("Adding Metadata:")
#if the directory had a .TXT file it will simply add the data from the file
if(meta is not ""):
    ds = netCDF4.Dataset("final.nc","a",format="NETCDF4")
    depthDim = ds.createDimension('Depth',depth)

    ds.close()

    os.system("ncatted -O -a Upper_Left_Corner,global,a,c,"+"\"("+UL_CORNER_LAT+","+UL_CORNER_LON+")\""+" final.nc final.nc")
    os.system("ncatted -O -a Upper_Right_Corner,global,a,c,"+"\"("+UR_CORNER_LAT+","+UR_CORNER_LON+")\""+" final.nc final.nc")
    os.system("ncatted -O -a Lower_Left_Corner,global,a,c,"+"\"("+LL_CORNER_LAT+","+LL_CORNER_LON+")\""+" final.nc final.nc")
    os.system("ncatted -O -a Lower_Right_Corner,global,a,c,"+"\"("+LR_CORNER_LAT+","+LR_CORNER_LON+")\""+" final.nc final.nc")
    os.system("ncatted -O -a Sensor_Angle,global,a,f,"+sensorAngle+" final.nc "+"final.nc")
    if(cleanFlag == 1):
        os.system("rm -f *.TIF")
    print("done.")
#if not .txt exists, then opens geoTIFF and reads metadata then parses it
else:
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
                for ind,lines in enumerate(splitted):
                    if( "Upper Left" in lines):
                        UpperLeft = lines
                        print(UpperLeft)
                    elif("Upper Right" in lines):
                        UpperRight = lines
                        print(UpperRight)
                    elif("Lower Left" in lines):
                        LowerLeft = lines
                        print(LowerLeft)
                    elif("Lower Right" in lines):
                        LowerRight = lines
                        print(LowerRight)
                UpperLeft = UpperLeft.replace('d','°')
                UpperRight = UpperRight.replace('d','°')
                LowerLeft = LowerLeft.replace('d','°')
                LowerRight = LowerRight.replace('d','°')
        
                #parses and translate dms coordinates into decimal coordinates
                UL_CORNER_LAT= parse_dms(UpperLeft[len(UpperLeft)-29:len(UpperLeft) - 16])
                UL_CORNER_LON=parse_dms(UpperLeft[len(UpperLeft)-14:len(UpperLeft)-1])
                UR_CORNER_LAT= parse_dms(UpperRight[len(UpperRight)-29:len(UpperRight) - 16])
                UR_CORNER_LON=parse_dms(UpperLeft[len(UpperLeft)-14:len(UpperRight)-1])
                LL_CORNER_LAT= parse_dms(LowerLeft[len(LowerLeft)-29:len(LowerLeft) - 16])
                LL_CORNER_LON=parse_dms(LowerLeft[len(LowerLeft)-14:len(LowerLeft)-1])
                LR_CORNER_LAT= parse_dms(LowerRight[len(LowerRight)-29:len(LowerRight) - 16])
                LR_CORNER_LON=parse_dms(LowerLeft[len(LowerLeft)-14:len(LowerRight)-1])
                UL_CORNER_LON = str(UL_CORNER_LON)
                UL_CORNER_LAT = str(UL_CORNER_LAT)
                UR_CORNER_LON = str(UR_CORNER_LON)
                UR_CORNER_LAT = str(UR_CORNER_LAT)
                LL_CORNER_LAT = str(LL_CORNER_LAT)
                LL_CORNER_LON = str(LL_CORNER_LON)
                LR_CORNER_LAT = str(LR_CORNER_LAT)
                LR_CORNER_LON = str(LR_CORNER_LON)
                
                os.system("ncatted -O -a Upper_Left_Corner,global,a,c,"+"\"("+UL_CORNER_LAT+","+UL_CORNER_LON+")\""+" final.nc final.nc")
                os.system("ncatted -O -a Upper_Right_Corner,global,a,c,"+"\"("+UR_CORNER_LAT+","+UR_CORNER_LON+")\""+" final.nc final.nc")
                os.system("ncatted -O -a Lower_Left_Corner,global,a,c,"+"\"("+LL_CORNER_LAT+","+LL_CORNER_LON+")\""+" final.nc final.nc")
                os.system("ncatted -O -a Lower_Right_Corner,global,a,c,"+"\"("+LR_CORNER_LAT+","+LR_CORNER_LON+")\""+" final.nc final.nc")
              
                print("done.")
                
                if(cleanFlag == 1):
                    os.system("rm -f *.TIF")
                exit()
