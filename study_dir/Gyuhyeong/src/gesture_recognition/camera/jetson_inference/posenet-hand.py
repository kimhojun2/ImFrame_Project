#!/usr/bin/env python3

import sys
import argparse

from jetson_inference import poseNet
from jetson_utils import videoSource, videoOutput, Log

# parse the command line
# parser = argparse.ArgumentParser(description="Run pose estimation DNN on a video/image stream.", 
#                                  formatter_class=argparse.RawTextHelpFormatter, 
#                                  epilog=poseNet.Usage() + videoSource.Usage() + videoOutput.Usage() + Log.Usage())

# parser.add_argument("input", type=str, default="csi://0", nargs='?', help="URI of the input stream")
# parser.add_argument("output", type=str, default="", nargs='?', help="URI of the output stream")
# parser.add_argument("--network", type=str, default="resnet18-hand", help="pre-trained model to load (see below for options)")
# parser.add_argument("--overlay", type=str, default="links,keypoints", help="pose overlay flags (e.g. --overlay=links,keypoints)\nvalid combinations are:  'links', 'keypoints', 'boxes', 'none'")
# parser.add_argument("--threshold", type=float, default=0.15, help="minimum detection threshold to use") 

# try:
# 	args = parser.parse_known_args()[0]
# except:
# 	print("")
# 	# parser.print_help()
# 	sys.exit(0)

# load the pose estimation model
net = poseNet("resnet18-hand", threshold=0.15)
camera = videoSource("csi://0")


# process frames until EOS or the user exits
while True:
    # capture the next image
    img = input.Capture()

    if img is None: # timeout
        continue  

    # perform pose estimation (with overlay)
    poses = net.Process(img, overlay="links,keypoints")

    # print the pose results
    print("detected {:d} objects in image".format(len(poses)))

    for pose in poses:
        print(pose)
        print(pose.Keypoints)
        print('Links', pose.Links)

    # render the image
    # output.Render(img)

    # update the title bar
    # output.SetStatus("{:s} | Network {:.0f} FPS".format(args.network, net.GetNetworkFPS()))
    print("{:.0f} FPS".format(net.GetNetworkFPS()))

    # print out performance info
    net.PrintProfilerTimes()

    # exit on input/output EOS
    if not input.IsStreaming():
        break