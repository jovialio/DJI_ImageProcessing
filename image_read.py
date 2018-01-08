from libxmp import XMPFiles
import re
from geopy import Point
from geopy.distance import vincenty
from io import BytesIO
from PIL import Image
from urllib import request
#import matplotlib.pyplot as plt # this is if you want to plot the map using pyplot
import cv2
import matplotlib.image as mpimg
import glob
import os

"""
Settings
"""
font = cv2.FONT_HERSHEY_SIMPLEX
linedist = 0.3
filepath = 'image/DJI*.JPG'
outputfilefolder = 'image/editted/'

"""
Functions
"""
def parse_degmin(degmin):
    parts = re.split('[^\d.]', degmin)
    latlongdeg = float(parts[0]) + float(parts[1]) / 60.0
    return format(latlongdeg, '.6f')

if not os.path.exists(outputfilefolder):
    os.makedirs(outputfilefolder)

"""
Open image for processing
"""
for fname in glob.glob(filepath): 
    
    # print filename
    print(fname)
    
    img_photo = mpimg.imread(fname) #mpimg reads in RGB
    img_photo = cv2.resize(img_photo,(2048,1080), interpolation = cv2.INTER_AREA) #resize to smaller scale
    height, width, channels = img_photo.shape 
    
    xmpfile = XMPFiles(file_path=fname, open_forupdate=False )
    xmp = xmpfile.get_xmp()

    # Using drone-dji
    AbsoluteAltitude = xmp.get_property('http://www.dji.com/drone-dji/1.0/', 'AbsoluteAltitude')
    FlightYawDegree = xmp.get_property('http://www.dji.com/drone-dji/1.0/', 'FlightYawDegree')
    GimbalYawDegree = xmp.get_property('http://www.dji.com/drone-dji/1.0/', 'GimbalYawDegree')

    # Using Adobe exif
    lat1 = float(parse_degmin(xmp.get_property('http://ns.adobe.com/exif/1.0/', 'GPSLatitude')))
    lon1 = float(parse_degmin(xmp.get_property('http://ns.adobe.com/exif/1.0/', 'GPSLongitude')))

    # Write text on image
    cv2.putText(img_photo,"Absolute Altitude: " + AbsoluteAltitude + "m",(750,50), font, 1.5,(0,0,255),2,cv2.LINE_AA)
    cv2.putText(img_photo,"Gimbal Yaw Degree: " + GimbalYawDegree + "deg",(750,100), font, 1.5,(0,0,255),2,cv2.LINE_AA)
    cv2.putText(img_photo,"Latitude: " + str(lat1),(750,150), font, 1.5,(0,0,255),2,cv2.LINE_AA)
    cv2.putText(img_photo,"Longitude: " + str(lon1),(750,200), font, 1.5,(0,0,255),2,cv2.LINE_AA)

    # Obtain 2nd lat/lon for purpose of drawing line to indicate drone camera direction
    lat2, lon2 = re.split('[,]',vincenty(kilometers=linedist).destination(Point(lat1, lon1), float(GimbalYawDegree)).format_decimal())
    lat2 = float(lat2)
    lon2 = float(lon2)
    
    # Plot data on google map and overlay on image
    url = "https://maps.googleapis.com/maps/api/staticmap?center={lat1},{lon1}&zoom=14&size=500x500&markers=color:green|label:J|{lat1},{lon1}&path=color:0xff0000|weight:5|{lat1},{lon1}|{lat2},{lon2}&format=jpg".format(lat1 = str(lat1), lon1 = str(lon1), lat2 = str(lat2), lon2 = str(lon2))
    buffer = BytesIO(request.urlopen(url).read())
    img_map = Image.open(buffer)
    img_photo[0:500, width-500:width] = img_map
    
    # Show using pyplot
    #plt.imshow(img_photo)
    #plt.show()

    mpimg.imsave('image/editted/' + fname[fname.find("DJI"):-3] + 'editted.png' ,img_photo)

print('Process Complete')
