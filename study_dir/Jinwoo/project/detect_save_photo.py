import sys
import argparse
import os
from datetime import datetime

from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput, Log

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=detectNet.Usage() + videoSource.Usage() + videoOutput.Usage() + Log.Usage())

parser.add_argument("input", type=str, default="", nargs='?', help="URI of the input stream")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 

try:
    args = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

# create video sources and outputs
input = videoSource(args.input, argv=sys.argv)

# Generate output filename based on current date and time
output_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg")

# If output directory doesn't exist, create it
output_directory = "output_images"
os.makedirs(output_directory, exist_ok=True)

# Construct full path for output file
output_path = os.path.join(output_directory, output_filename)

output = videoOutput(output_path, argv=sys.argv)
    
# load the object detection network
net = detectNet(args.network, sys.argv, args.threshold)

# List to store detected objects
detected_objects = []

# process frames until EOS or the user exits
while True:
    # capture the next image
    img = input.Capture()

    if img is None: # timeout
        continue  
    
    # detect objects in the image (with overlay)
    detections = net.Detect(img, overlay=args.overlay)

    # Add detected objects to the list
    detected_objects.extend(detections)

    # print the detections
    print("detected {:d} objects in image".format(len(detections)))

    for detection in detections:
        print(detection)

    # render the image
    output.Render(img)

    # update the title bar
    output.SetStatus("{:s} | Network {:.0f} FPS".format(args.network, net.GetNetworkFPS()))

    # print out performance info
    net.PrintProfilerTimes()

    # exit on input/output EOS
    if not input.IsStreaming() or not output.IsStreaming():
        break

# Print the detected objects list
print("감지된 오브젝트:")
for obj in detected_objects:
    print(obj)

print("Output image saved to:", output_path)
