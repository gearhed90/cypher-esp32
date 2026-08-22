#!/usr/bin/env python3
"""
Cypher MJPEG camera stream — picamera2 + Flask

Camera Module 3 (IMX708): 1280x720, quality 85, AWB + continuous AF.
Serves http://0.0.0.0:8080/stream
"""

import logging
import time

from flask import Flask, Response

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("cypher-stream")

app = Flask(__name__)

WIDTH = 1280
HEIGHT = 720
FPS = 15
QUALITY = 85

_camera = None


def get_camera():
    global _camera
    if _camera is not None:
        return _camera
    from picamera2 import Picamera2

    cam = Picamera2()
    # XRGB8888 avoids ambiguous RGB channel ordering with some cv2 paths
    config = cam.create_video_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "XRGB8888"},
        controls={"FrameRate": FPS},
    )
    cam.configure(config)
    cam.start()
    time.sleep(0.5)

    try:
        from libcamera import controls as camctrl
        cam.set_controls({
            "AeEnable": True,
            "AwbEnable": True,
            "AfMode": camctrl.AfModeEnum.Continuous,
        })
    except Exception as e:
        log.info("Some controls not set (%s)", e)

    _camera = cam
    log.info("Camera started %dx%d @ %d fps (quality=%d)", WIDTH, HEIGHT, FPS, QUALITY)
    return _camera


def mjpeg_generator():
    import cv2
    import numpy as np

    cam = get_camera()
    while True:
        frame = cam.capture_array()
        # XRGB8888: (H,W,4) with bytes X,R,G,B or similar — build BGR for cv2
        if frame.ndim == 3 and frame.shape[2] == 4:
            # Common picamera2 XRGB layout: [:,:,1:4] is RGB
            bgr = frame[:, :, [3, 2, 1]].copy()
        elif frame.ndim == 3 and frame.shape[2] == 3:
            # Assume RGB from RGB888 — convert to BGR once
            bgr = frame[:, :, ::-1].copy()
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
    app.run(host="0.0.0.0", port=8080, threaded=True)
