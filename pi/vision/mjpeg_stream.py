#!/usr/bin/env python3
"""
Cypher MJPEG camera stream — picamera2 + Flask

Camera Module 3 (IMX708): 1280x720, quality 85, AWB + continuous AF.
On this Pi the capture buffer order already matches cv2 JPEG encode.
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
    config = cam.create_video_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "RGB888"},
        controls={"FrameRate": FPS},
    )
    cam.configure(config)
    cam.start()
    time.sleep(0.6)

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

    cam = get_camera()
    while True:
        frame = cam.capture_array()
        # Do not channel-swap: on this platform RGB888 capture already
        # encodes with correct colors via cv2.imencode (verified empirically).
        if frame.ndim == 3 and frame.shape[2] > 3:
            frame = frame[:, :, :3]

        ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY])
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
