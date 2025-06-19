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

v4:
Creating widget in which preview video stream can run and real-time data can
be displayed. Using version of app_capture2.py by davidplowman and chrisruk
with the button and its functionality removed. Incorporating successful parts
of v3.
https://github.com/raspberrypi/picamera2/blob/main/apps/app_capture2.py
'''
import cv2
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel,
                             QVBoxLayout, QWidget)

from picamera2 import Picamera2, Preview
from picamera2.previews.qt import QGlPicamera2

def post_callback(request):
    label.setText(''.join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))


picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
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
picam2.stop_preview()
picam2.stop()
time.sleep(5)



picam2.post_callback = post_callback
picam2.configure(preview_config)

app = QApplication([])


qpicamera2 = QGlPicamera2(picam2, width=800, height=600, keep_ar=False)
label = QLabel()
window = QWidget()

label.setFixedWidth(400)
label.setAlignment(QtCore.Qt.AlignTop)
layout_h = QHBoxLayout()
layout_v = QVBoxLayout()
layout_v.addWidget(label)
layout_h.addWidget(qpicamera2, 80)
layout_h.addLayout(layout_v, 20)
window.setWindowTitle("Qt Picamera2 App")
window.resize(1200, 600)
window.setLayout(layout_h)

picam2.start()
window.show()
app.exec()