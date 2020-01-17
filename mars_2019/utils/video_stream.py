import cv2
from flask import Flask, render_template, Response

def start_stream(generator, port=8080):
    app = Flask(__name__)
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/video_feed")
    def video_feed():
        return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

    def generate():
        header = bytearray(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n')

        while True:
            frame = next(generator)
            flag, encodedImage = cv2.imencode(".jpg", frame)

            if not flag:
                print("Invalid frame")
                continue
            
            data = header.copy()
            data.extend(bytearray(encodedImage))
            data.extend(b'\r\n')
            yield bytes(data)

    app.run(host="0.0.0.0", port=port, debug=True, threaded=True, use_reloader=False)
    