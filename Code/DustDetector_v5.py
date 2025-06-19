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

v5:
Merge v4a with v1 to incorporate thesholding and proper camera use.
'''

import time
import cv2
from picamera2 import Picamera2, Preview, MappedArray

COLOR = (0, 255, 0)
ORIGIN = (0, 30)
FONT = cv2.FONT_HERSHEY_SIMPLEX
SCALE = 1
THICKNESS = 2
        
def calculate_threshold(request):
    """Convert the frame to grayscale, threshold to black and white, then calculate pixel ratio"""
    # Get time for visual confirmation of running and framerate
    timestamp = time.strftime("%Y-%m-%d %X")
    
    with MappedArray(request, "main") as m:
        
        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(m.array, cv2.COLOR_BGR2GRAY)
        
        # Gaussian filtering (blurring for better discrimination
        blur = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        
        # Apply Otsu's binarization
        _, binary_frame = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        # Count black pixels (1 is white, 0 is black)
        black_pixels = binary_frame.size - cv2.countNonZero(binary_frame)
        
        # Calculate the ratio
        if black_pixels > 0:
            black_to_total_ratio = black_pixels / binary_frame.size
        else:
            black_to_total_ratio = 0.0
        
        # Display the calculated ratio on the frame
        cv2.putText(m.array, timestamp, ORIGIN, FONT, SCALE, COLOR, THICKNESS)
        cv2.putText(m.array, f'Ratio: {black_to_total_ratio:.3f}', (30, 60), FONT, SCALE, COLOR, THICKNESS)
    

def main():
    """Main function to run the DustSensor application."""
	
	# Open the video capture device
    picam2 = Picamera2()
	
	# Check if the camera opened successfully
    if not picam2:
        print("Error: Could not open camera.")
        return
    
    picam2.pre_callback = calculate_threshold
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
    
    while True:
        
        # Check for the 'q' key press to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
	
if __name__ == "__main__":
	main()
