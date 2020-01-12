import cv2
from flask import Flask, render_template, Response

import jetson.inference
import jetson.utils
import numpy as np
import ctypes
import sys
import argparse

# parse the command line
parser = argparse.ArgumentParser(description="Segment a live camera stream using an semantic segmentation DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.segNet.Usage())

parser.add_argument("--network", type=str, default="fcn-resnet18-voc", help="pre-trained model to load, see below for options")
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
print(type(net.MaskClass))

width = opt.width
height = opt.height
classes = jetson.utils.cudaAllocMapped(width * height)
camera = jetson.utils.gstCamera(width, height, "/dev/video0")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

def generate():
    header = bytearray(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n')

    downscale = 2

    out_width = opt.width // downscale
    out_height = opt.height // downscale

    output = np.zeros((out_height * 2, out_width, 3), dtype=np.uint8)
    while True:
        # process the segmentation network
        img, width, height = camera.CaptureRGBA(zeroCopy=1)

        net.Process(img, width, height, "void")
        net.MaskClass(classes, out_width, out_height)

        # cudaToNumpy assumes float32. need to divide by 8 to account for uint8
        mask_np = jetson.utils.cudaToNumpy(classes, 1, out_width * out_height // 4, 1)[:, 0, 0]
        mask_np = mask_np.view('uint8').reshape(out_height, out_width)

        output.fill(0)
        output[:out_height, :, :][
            ((mask_np == 2) | (mask_np == 3) | (mask_np == 4) | (mask_np == 12))
        ] = (255, 255, 255)

        img_np = jetson.utils.cudaToNumpy(img, width, height, 4).astype('uint8') # convert original img to numpy
        img_np = cv2.resize(img_np, (out_width, out_height)) # resize
        cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR, dst=output[out_height:, :, :])

        # encode the frame in JPEG format
        flag, encodedImage = cv2.imencode(".jpg", output)

        if not flag:
            print('!!')
            continue
        
        data = header.copy()
        data.extend(bytearray(encodedImage))
        data.extend(b'\r\n')
        yield bytes(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True, use_reloader=False)