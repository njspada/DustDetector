'''
DustSensor

v1:
Inherited from N. Spada

v2:
Attempt to disable camera automatically adjusting to ambient
light conditions. For now, attempt to work within cv2 library.

v2a:
Using CAP_PROP_FORMAT to get raw video seemingly unsupported.
https://techoverflow.net/2022/11/01/how-to-enable-disable-manual-white-balance-in-opencv-python/
Trying CAP_PROP_AUTO_EXPOSURE, CAP_PROP_AUTO_WB, V4L2_CID_AUTO_WHITE_BALANCE
Issues with support for CAP_PROP_AUTO_WB, V4L2_CID_AUTO_WHITE_BALANCE

'''
import cv2

def main():
	
	# Open the video capture device
	cap = cv2.VideoCapture(0)
	
	# Check if the camera opened successfully
	if not cap.isOpened():
		print("Error: Could not open camera.")
		return
    
	# Determine cv2.CAP_PROP_AUTO_EXPOSURE
	print("CAP_PROP_AUTO_EXPOSURE: ", cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))

	# Determine cv2.CAP_PROP_AUTO_WB
	#print("CAP_PROP_AUTO_WB: ", cap.get(cv2.CAP_PROP_AUTO_WB))

	# Determine cv2.V4L2_CID_AUTO_WHITE_BALANCE
	#print("V4L2_CID_AUTO_WHITE_BALANCE: ", cap.get(cv2.V4L2_CID_AUTO_WHITE_BALANCE))


	# Disable auto-exposure
	cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.0)

	# Check if auto-exposure was properly disabled
	if cap.get(cv2.CAP_PROP_AUTO_EXPOSURE) != 0.0:
		print("Error: Failed to disable auto-exposure.")
		return


	while True:
		# Read a frame from the camera
		ret, frame = cap.read()
		
		# If the frame was not captured successfully,
		# break the loop
		if not ret:
			print("Error: Could not read frame.")
			break
		
		# Convert the frame to grayscale
		gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		
		# Gaussian filtering (blurring for better discrimination
		blur = cv2.GaussianBlur(gray_frame, (5, 5), 0)
		
		# Apply a binary threshold
		#_, binary_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)
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
		cv2.putText(frame, f'Ratio: {black_to_total_ratio:.3f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
		
		# Display the captured frame
		cv2.imshow("Video Stream", frame)
		
		# Check for the 'q' key press to exit the loop
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	
	# Release the camera and close the OpenCV windows
	cap.release()
	cv2.destroyAllWindows()
	
if __name__ == "__main__":
	main()
13