#!/usr/bin/env python3
"""
Cypher MJPEG camera stream — picamera2 + Flask

Camera Module 3 (IMX708): full-FOV 2304x1296 mode (less zoomed),
streamed as MJPEG. Continuous AF when available.

Serves http://0.0.0.0:8080/stream
"""

import logging
import time

from flask import Flask, Response

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("cypher-stream")

app = Flask(__name__)

# IMX708 full-FOV-ish video mode (2x2 binned). Avoids the tighter 720p crop.
WIDTH = 2304
HEIGHT = 1296
FPS = 12
QUALITY = 82
# Optional downscale for bandwidth (0 = send native)
STREAM_WIDTH = 1280
STREAM_HEIGHT = 720

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
    time.sleep(0.5)

    try:
        from libcamera import controls as camctrl
        cam.set_controls({"AfMode": camctrl.AfModeEnum.Continuous})
    except Exception as e:
        log.info("AF continuous not set (%s)", e)

    _camera = cam
    log.info(
        "Camera started capture %dx%d @ %d fps; stream scale %dx%d quality=%d",
        WIDTH, HEIGHT, FPS, STREAM_WIDTH, STREAM_HEIGHT, QUALITY,
    )
    return _camera


def mjpeg_generator():
    import cv2

    cam = get_camera()
    while True:
        frame = cam.capture_array()
        if frame.ndim == 3 and frame.shape[2] == 3:
            bgr = frame[:, :, ::-1]
        else:
            bgr = frame

        if STREAM_WIDTH and STREAM_HEIGHT:
            if bgr.shape[1] != STREAM_WIDTH or bgr.shape[0] != STREAM_HEIGHT:
                bgr = cv2.resize(bgr, (STREAM_WIDTH, STREAM_HEIGHT), interpolation=cv2.INTER_AREA)

        ok, buf = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY])
        if not ok:
            time.sleep(0.05)
            continue
        jpg = buf.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
        )
        time.sleep(1.0 / max(FPS, 1))


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
