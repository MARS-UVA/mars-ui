import cv2
from ..utils.video_stream import start_stream
from .aligned_depth import generate_rgbd

import jetson.inference
import jetson.utils
import numpy as np
import ctypes
import sys
import argparse

# parse the command line
parser = argparse.ArgumentParser(description="Segment a live camera stream using an semantic segmentation DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.segNet.Usage())

parser.add_argument("--network", type=str, default="fcn-resnet18-cityscapes-1024x512", help="pre-trained model to load, see below for options")
parser.add_argument("--width", type=int, default=1280, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

net = jetson.inference.segNet(opt.network, sys.argv)
net.SetOverlayAlpha(255)

width = opt.width
height = opt.height
classes = jetson.utils.cudaAllocMapped(width * height)

def frame_generator():
    downscale = 2

    out_width = opt.width // downscale
    out_height = opt.height // downscale

    output = np.zeros((out_height, out_width * 3, 3), dtype=np.uint8)
    rgbd_generator = generate_rgbd()
    rgba_img = np.ones((height, width, 4), dtype="float32") * 255
    while True:
        depth_img, color_img = next(rgbd_generator)
        rgba_img[:, :, :3] = color_img

        # net takes in float32 RGBA
        net.Process(jetson.utils.cudaFromNumpy(rgba_img), width, height, "void")
        net.MaskClass(classes, out_width, out_height)

        # cudaToNumpy assumes float32. need to divide by 8 to account for uint8
        mask_np = jetson.utils.cudaToNumpy(classes, 1, out_width * out_height // 4, 1)[:, 0, 0]
        mask_np = mask_np.view('uint8').reshape(out_height, out_width)

        output.fill(0)
        # color the ground with white color.
        output[:, :out_width, :][
            ((mask_np == 2) | (mask_np == 3) | (mask_np == 4) | (mask_np == 12)) #
        ] = (255, 255, 255)

        output[:, out_width:2 * out_width, :] = cv2.resize(color_img, (out_width, out_height))
        output[:, 2 * out_width:, :] = cv2.resize(depth_img, (out_width, out_height))[:, :, np.newaxis]

        yield output

if __name__ == "__main__":
    start_stream(frame_generator())