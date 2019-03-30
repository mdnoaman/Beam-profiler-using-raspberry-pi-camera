from __future__ import(
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )

import io
import time
import picamera
import numpy as np
from numpy.lib.stride_tricks import as_strided

time1 = time.time()
stream = io.BytesIO()
with picamera.PiCamera() as camera:
    time.sleep(0.1)
    camera.iso = 100
    camera.exposure_mode = "off"
    camera.framerate = 10
    camera.shutter_speed = 200  #in microseconds
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g

    camera.capture(stream, format='jpeg', bayer=True)
    ver = {
        'RP_ov5647' : 1,
        'RP_imx219' : 2,
        }[camera.exif_tags['IFD0.Model']]

offset = {
    1: 6404096,
    2: 10270208,
    }[ver]

data = stream.getvalue()[-offset:]
assert data[:4] == 'BRCM'
data = data[32768:]
data = np.fromstring(data,dtype=np.uint8)

reshape, crop = {
    1: ((1952, 3264), (1944,3240)),
    2: ((2480, 4128), (2464,4100)),
    }[ver]

data = data.reshape(reshape)[:crop[0], :crop[1]]

data = data.astype(np.uint16) << 2
for byte in range(4):
    data[:,byte::5] |= ((data[:,4::5] >> ((4 - byte)*2)) & 0b11)
data = np.delete(data,np.s_[4::5],1)

print(data.shape)

#%% save image to file
with open('image.data', 'wb') as f:
    data.tofile(f)

#%% show image
from matplotlib import pyplot as plt
crop_img = data[500:1000,1000:1500]
plt.imshow(crop_img, cmap='gray', vmin=0, vmax=1023)
plt.show()

