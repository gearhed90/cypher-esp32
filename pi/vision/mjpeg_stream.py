#!/usr/bin/env python3
"""
Cypher MJPEG camera stream — picamera2 + Flask

Serves multipart JPEG at http://0.0.0.0:8080/stream
Match CYPHER_STREAM_URL=http://cypher:8080/stream (or localhost).

Run on the Pi:
  source /home/sentry/cypher-dashboard/venv/bin/activate   # or any venv with deps
  pip install picamera2 flask
  python3 pi/vision/mjpeg_stream.py

Or from repo root on the Pi after install.
"""

import io
import logging
import time

from flask import Flask, Response

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("cypher-stream")

app = Flask(__name__)

WIDTH = 640
HEIGHT = 480
FPS = 15
QUALITY = 70

_camera = None


def get_camera():
    global _camera
    if _camera is not None:
        return _camera
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput

    cam = Picamera2()
    config = cam.create_video_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "RGB888"},
        controls={"FrameRate": FPS},
    )
    cam.configure(config)
    cam.start()
    time.sleep(0.3)
    _camera = cam
    log.info("Camera started %dx%d @ %d fps", WIDTH, HEIGHT, FPS)
    return _camera


def mjpeg_generator():
    import cv2
    import numpy as np

    cam = get_camera()
    while True:
        frame = cam.capture_array()
        # RGB -> BGR for cv2 encode
        if frame.ndim == 3 and frame.shape[2] == 3:
            bgr = frame[:, :, ::-1]
        else:
            bgr = frame
        ok, buf = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY])
        if not ok:
            time.sleep(0.05)
            continue
        jpg = buf.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
        )
        time.sleep(1.0 / FPS)


@app.route("/stream")
def stream():
    return Response(
        mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/")
def index():
    return (
        "<html><body style='background:#111;color:#8cf;font-family:sans-serif'>"
        "<h1>Cypher stream</h1>"
        "<p><a href='/stream' style='color:#8cf'>/stream</a></p>"
        "<img src='/stream' style='max-width:100%'/>"
        "</body></html>"
    )


if __name__ == "__main__":
    # Bind all interfaces for Tailscale / LAN
    app.run(host="0.0.0.0", port=8080, threaded=True)
