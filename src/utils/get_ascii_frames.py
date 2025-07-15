import cv2

# Load the video
video_path = "C:/Users/Faruk/Downloads/55850-504238889_small.mp4"
cap = cv2.VideoCapture(video_path)

# Check if video was opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

frame_count = 0  # Initialize frame counter
pixel_ascii_map = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


with open("animation_frames.txt", "w") as f:
    # Loop through each frame in the video
    while True:
        ret, frame = cap.read()
        
        # Increasing Contrast for a better ascii visual
        frame = cv2.convertScaleAbs(frame, alpha=1, beta=-50)

        # Break the loop if the video ends
        if not ret:
            break

        # Resize image
        frame = cv2.resize(frame, (120, 40))
        
        for row in frame: # Discarding unnnecessary image rows
            for pixel in row:
                asciiIndex = int((sum(pixel) / 3) / 255 * (len(pixel_ascii_map) - 1))
                asciiVal = pixel_ascii_map[asciiIndex]
                f.write(asciiVal)
            f.write("\n")
        
        f.write("\n")
            
        print(f"Frame {frame_count}")
        
        
        frame_count += 1


        

# Release the video capture object
cap.release()
print("Video capture object released.", frame_count)

