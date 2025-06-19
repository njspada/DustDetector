'''
DustSensor

v1:
Inherited from N. Spada

v2:
Attempt to disable camera automatically adjusting to ambient
light conditions. For now, attempt to work within cv2 library.

v3:
Different approach. Upgraded Raspberry Pi OS to Bookworm to take advantage of
Picamera2, based on open-source libcamera instead of a deprecated and
proprietary Broadcom API. The proprietary API was unable to guarantee support
for camera controls vital to the viability of the DustSensor project. This
version is based on controls.py by davidplowman and chrisruk.
https://github.com/raspberrypi/picamera2/blob/main/examples/controls.py#L6

v4a:
Creating widget in which preview video stream can run and real-time data can
be displayed. Using parts of timestamped_video.py by davidplowman and chrisruk.
Incorporating successful parts of v3.
https://github.com/raspberrypi/picamera2/blob/main/examples/timestamped_video.py
'''
import cv2
import time
from picamera2 import Picamera2, Preview, MappedArray

colour = (0, 255, 0)
origin = (0, 30)
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thickness = 2

def apply_timestamp(request):
    timestamp = time.strftime("%Y-%m-%d %X")
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)



picam2 = Picamera2()
picam2.pre_callback = apply_timestamp
picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)

# After ten seconds, we fix the AGC/AEC
# to the values it has reached whereafter it will no longer change.
picam2.start()
time.sleep(10)

# Get and print metadata values
metadata = picam2.capture_metadata()
controls = {c: metadata[c] for c in ["ExposureTime", "AnalogueGain", "ColourGains"]}
print(controls)

#Set metadata values
picam2.set_controls(controls)
time.sleep(5)